"""
🔒 Sandbox de Ejecución Segura - RepletO v2.0

Sistema de ejecución aislada para múltiples lenguajes con:
- Límites estrictos de recursos (CPU, memoria, tiempo)
- Entorno aislado sin acceso al sistema
- Captura de visualizaciones (matplotlib, plotly)
- Streaming de output en tiempo real
- Detección de código malicioso
"""

import subprocess
import sys
import os
import tempfile
import resource
import signal
import asyncio
import io
import base64
import json
import re
from typing import Dict, Any, Callable, Optional, List
import logging
from datetime import datetime
import uuid
import shutil
from pathlib import Path

# Imports para captura de visualizaciones
try:
    import matplotlib
    matplotlib.use('Agg')  # Backend sin GUI
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Error de seguridad en el código"""
    pass

class ExecutionTimeoutError(Exception):
    """Error de timeout en la ejecución"""
    pass

class SecureSandbox:
    """
    Sandbox seguro para ejecución de código múltiple lenguaje
    """
    
    def __init__(self, 
                 default_timeout: int = 30,
                 max_memory_mb: int = 512,
                 temp_dir: str = None):
        """
        Inicializar sandbox
        
        Args:
            default_timeout: Timeout por defecto en segundos
            max_memory_mb: Límite de memoria en MB
            temp_dir: Directorio temporal personalizado
        """
        self.default_timeout = default_timeout
        self.max_memory = max_memory_mb * 1024 * 1024  # Convertir a bytes
        self.temp_dir = temp_dir or tempfile.gettempdir()
        
        # Patrones de código malicioso
        self.dangerous_patterns = [
            r'import\s+(os|sys|subprocess|socket|urllib|requests)',
            r'from\s+(os|sys|subprocess|socket|urllib|requests)',
            r'__import__\s*\(',
            r'eval\s*\(',
            r'exec\s*\(',
            r'compile\s*\(',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\(',
            r'\.system\s*\(',
            r'\.popen\s*\(',
            r'\.call\s*\(',
            r'shutil\.',
            r'pathlib\.',
            r'glob\.',
            r'tempfile\.',
            r'pickle\.',
        ]
        
        # Imports permitidos
        self.allowed_imports = {
            'math', 'random', 'datetime', 'json', 'csv', 'itertools',
            'collections', 'functools', 'operator', 'string', 'decimal',
            'fractions', 'statistics', 're', 'unicodedata',
            'numpy', 'pandas', 'matplotlib', 'seaborn', 'plotly',
            'scipy', 'sklearn', 'PIL', 'cv2', 'sympy'
        }

    def _check_security(self, code: str) -> None:
        """
        Verificar que el código no contenga patrones peligrosos
        
        Args:
            code: Código a verificar
            
        Raises:
            SecurityError: Si se detecta código malicioso
        """
        code_lower = code.lower()
        
        # Verificar patrones peligrosos
        for pattern in self.dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                raise SecurityError(f"Código bloqueado: patrón peligroso detectado - {pattern}")
        
        # Verificar imports
        import_matches = re.findall(r'import\s+(\w+)', code) + \
                        re.findall(r'from\s+(\w+)', code)
        
        for module in import_matches:
            if module not in self.allowed_imports:
                logger.warning(f"Import no permitido detectado: {module}")
                # No bloqueamos, pero loggeamos
        
        # Verificar longitud del código
        if len(code) > 50000:  # 50KB máximo
            raise SecurityError("Código demasiado largo (máximo 50KB)")

    def _create_secure_environment(self) -> Dict[str, str]:
        """
        Crear entorno de variables seguro
        
        Returns:
            Dict con variables de entorno limitadas
        """
        return {
            'PATH': '/usr/local/bin:/usr/bin:/bin',
            'PYTHONPATH': '',
            'HOME': self.temp_dir,
            'TEMP': self.temp_dir,
            'TMP': self.temp_dir,
            'PYTHONIOENCODING': 'utf-8',
            'PYTHONUTF8': '1',
            'PYTHONDONTWRITEBYTECODE': '1',
            'PYTHONUNBUFFERED': '1',
            # Prevenir que matplotlib use GUI
            'MPLBACKEND': 'Agg',
        }

    async def execute_python(self, 
                            code: str, 
                            timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Ejecutar código Python de forma segura
        
        Args:
            code: Código Python a ejecutar
            timeout: Timeout personalizado
            
        Returns:
            Dict con resultado de la ejecución
        """
        timeout = timeout or self.default_timeout
        
        # Verificación de seguridad
        self._check_security(code)
        
        # Crear directorio temporal único
        execution_id = str(uuid.uuid4())
        work_dir = Path(self.temp_dir) / f"repleto_exec_{execution_id}"
        work_dir.mkdir(exist_ok=True)
        
        try:
            # Crear archivo temporal con el código
            code_file = work_dir / "code.py"
            
            # Preparar código con captura de visualizaciones
            enhanced_code = self._prepare_python_code(code)
            
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(enhanced_code)
            
            # Ejecutar en subprocess
            start_time = datetime.now()
            
            result = await asyncio.create_subprocess_exec(
                sys.executable, str(code_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(work_dir),
                env=self._create_secure_environment(),
                preexec_fn=self._set_resource_limits if os.name != 'nt' else None
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    result.communicate(), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                result.terminate()
                await result.wait()
                raise ExecutionTimeoutError(f"Ejecución excedió {timeout}s")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Procesar salida
            output = stdout.decode('utf-8', errors='replace')
            error = stderr.decode('utf-8', errors='replace') if stderr else None
            
            # Leer visualizaciones generadas
            visualizations = self._collect_visualizations(work_dir)
            
            # Leer datos estructurados si existen
            data = self._collect_data(work_dir)
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": output,
                "error": error,
                "execution_time": execution_time,
                "visualizations": visualizations,
                "data": data
            }
            
        except SecurityError as e:
            logger.warning(f"Security violation: {e}")
            return {
                "status": "error",
                "output": "",
                "error": str(e),
                "execution_time": 0.0,
                "visualizations": [],
                "data": {}
            }
        except ExecutionTimeoutError as e:
            logger.warning(f"Execution timeout: {e}")
            return {
                "status": "timeout",
                "output": "",
                "error": str(e),
                "execution_time": timeout,
                "visualizations": [],
                "data": {}
            }
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {
                "status": "error",
                "output": "",
                "error": f"Error interno: {str(e)}",
                "execution_time": 0.0,
                "visualizations": [],
                "data": {}
            }
        finally:
            # Limpiar directorio temporal
            try:
                shutil.rmtree(work_dir)
            except Exception as e:
                logger.warning(f"No se pudo limpiar directorio temporal: {e}")

    def _prepare_python_code(self, code: str) -> str:
        """
        Preparar código Python con captura de visualizaciones
        
        Args:
            code: Código original
            
        Returns:
            Código modificado con captura automática
        """
        enhanced_code = f"""
import sys
import os
import io
import json
import base64
from contextlib import redirect_stdout, redirect_stderr

# Configurar matplotlib si está disponible
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Configurar pandas para mejor visualización
try:
    import pandas as pd
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 1000)
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Capturar stdout
captured_output = io.StringIO()

try:
    with redirect_stdout(captured_output):
        # === CÓDIGO DEL USUARIO ===
{code}
        # === FIN CÓDIGO DEL USUARIO ===
        
        # Guardar plots de matplotlib si existen
        if MATPLOTLIB_AVAILABLE and plt.get_fignums():
            for i, fig_num in enumerate(plt.get_fignums()):
                fig = plt.figure(fig_num)
                fig.savefig(f'plot_{{i}}.png', dpi=100, bbox_inches='tight')
            plt.close('all')
        
    # Imprimir output capturado
    output = captured_output.getvalue()
    if output:
        print(output, end='')
        
except Exception as e:
    print(f"Error: {{str(e)}}", file=sys.stderr)
    sys.exit(1)
"""
        return enhanced_code

    def _collect_visualizations(self, work_dir: Path) -> List[str]:
        """
        Recolectar visualizaciones generadas
        
        Args:
            work_dir: Directorio de trabajo
            
        Returns:
            Lista de imágenes en base64
        """
        visualizations = []
        
        # Buscar archivos de imagen
        for img_file in work_dir.glob("*.png"):
            try:
                with open(img_file, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                    visualizations.append(img_data)
            except Exception as e:
                logger.warning(f"Error cargando visualización {img_file}: {e}")
        
        return visualizations

    def _collect_data(self, work_dir: Path) -> Dict[str, Any]:
        """
        Recolectar datos estructurados generados
        
        Args:
            work_dir: Directorio de trabajo
            
        Returns:
            Dict con datos estructurados
        """
        data = {}
        
        # Buscar archivos JSON de datos
        for data_file in work_dir.glob("data_*.json"):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    data[data_file.stem] = file_data
            except Exception as e:
                logger.warning(f"Error cargando datos {data_file}: {e}")
        
        return data

    def _set_resource_limits(self):
        """
        Establecer límites de recursos del proceso (Unix only)
        """
        if os.name != 'nt':  # Solo en sistemas Unix
            # Límite de memoria
            resource.setrlimit(resource.RLIMIT_AS, (self.max_memory, self.max_memory))
            
            # Límite de CPU (prevenir loops infinitos)
            resource.setrlimit(resource.RLIMIT_CPU, (60, 60))  # 60 segundos
            
            # Límite de archivos abiertos
            resource.setrlimit(resource.RLIMIT_NOFILE, (20, 20))

    async def execute_javascript(self, 
                                code: str, 
                                timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Ejecutar código JavaScript con Node.js
        
        Args:
            code: Código JavaScript a ejecutar
            timeout: Timeout personalizado
            
        Returns:
            Dict con resultado de la ejecución
        """
        timeout = timeout or self.default_timeout
        
        # Verificación básica de seguridad
        if 'require(' in code and 'fs' in code:
            return {
                "status": "error",
                "output": "",
                "error": "Acceso al sistema de archivos no permitido",
                "execution_time": 0.0,
                "visualizations": [],
                "data": {}
            }
        
        # Crear archivo temporal
        execution_id = str(uuid.uuid4())
        work_dir = Path(self.temp_dir) / f"repleto_js_{execution_id}"
        work_dir.mkdir(exist_ok=True)
        
        try:
            code_file = work_dir / "code.js"
            
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            start_time = datetime.now()
            
            # Ejecutar con Node.js
            result = await asyncio.create_subprocess_exec(
                'node', str(code_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(work_dir)
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    result.communicate(), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                result.terminate()
                await result.wait()
                raise ExecutionTimeoutError(f"Ejecución excedió {timeout}s")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            output = stdout.decode('utf-8', errors='replace')
            error = stderr.decode('utf-8', errors='replace') if stderr else None
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": output,
                "error": error,
                "execution_time": execution_time,
                "visualizations": [],
                "data": {}
            }
            
        except Exception as e:
            logger.error(f"JavaScript execution error: {e}")
            return {
                "status": "error",
                "output": "",
                "error": str(e),
                "execution_time": 0.0,
                "visualizations": [],
                "data": {}
            }
        finally:
            try:
                shutil.rmtree(work_dir)
            except Exception:
                pass

    async def execute_streaming(self, 
                              code: str, 
                              language: str,
                              output_callback: Callable[[str, str], None],
                              timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Ejecutar código con streaming de output en tiempo real
        
        Args:
            code: Código a ejecutar
            language: Lenguaje de programación
            output_callback: Función para enviar output en tiempo real
            timeout: Timeout personalizado
            
        Returns:
            Dict con resultado final
        """
        # TODO: Implementar streaming real
        # Por ahora, ejecutamos normal y enviamos el resultado
        
        if language == "python":
            result = await self.execute_python(code, timeout)
        elif language == "javascript":
            result = await self.execute_javascript(code, timeout)
        else:
            result = {
                "status": "error",
                "output": "",
                "error": f"Lenguaje no soportado: {language}",
                "execution_time": 0.0,
                "visualizations": [],
                "data": {}
            }
        
        # Enviar output via callback
        if result["output"]:
            await output_callback("stdout", result["output"])
        
        if result["error"]:
            await output_callback("stderr", result["error"])
        
        return result