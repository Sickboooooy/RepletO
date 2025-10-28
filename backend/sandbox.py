import subprocess
import sys
import os
import tempfile
import signal
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def execute_code(code: str, timeout: int = 5) -> Dict[str, Any]:
    """
    Ejecuta código Python de forma segura en un entorno sandbox
    
    Args:
        code: Código Python a ejecutar
        timeout: Tiempo límite en segundos (default: 5)
    
    Returns:
        Dict con status, output y error
    """
    
    # Validación básica
    if not code or not code.strip():
        return {
            "status": "error",
            "output": "",
            "error": "No se proporcionó código para ejecutar"
        }
    
    # Verificar código malicioso básico
    dangerous_imports = [
        'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
        'shutil', 'pathlib', 'glob', 'tempfile', 'pickle'
    ]
    
    for dangerous in dangerous_imports:
        if f"import {dangerous}" in code or f"from {dangerous}" in code:
            return {
                "status": "error",
                "output": "",
                "error": f"Importación prohibida detectada: {dangerous}"
            }
    
    # Crear archivo temporal para el código
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        # Ejecutar en subprocess con restricciones
        result = subprocess.run(
            [sys.executable, temp_file_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir(),  # Ejecutar en directorio temporal
            env={  # Entorno limitado
                'PATH': os.environ.get('PATH', ''),
                'PYTHONPATH': '',
                'HOME': tempfile.gettempdir(),
                'PYTHONIOENCODING': 'utf-8',  # Forzar UTF-8 para emojis
                'PYTHONUTF8': '1'  # Modo UTF-8 en Python 3.7+
            },
            encoding='utf-8',  # Especificar encoding explícitamente
            errors='replace'   # Reemplazar caracteres problemáticos
        )
        
        # Limpiar archivo temporal
        os.unlink(temp_file_path)
        
        if result.returncode == 0:
            return {
                "status": "success",
                "output": result.stdout,
                "error": result.stderr if result.stderr else None
            }
        else:
            return {
                "status": "error",
                "output": result.stdout,
                "error": result.stderr
            }
    
    except subprocess.TimeoutExpired:
        # Limpiar archivo temporal en caso de timeout
        try:
            os.unlink(temp_file_path)
        except:
            pass
        
        return {
            "status": "error",
            "output": "",
            "error": f"Tiempo de ejecución excedido ({timeout}s)"
        }
    
    except Exception as e:
        # Limpiar archivo temporal en caso de error
        try:
            os.unlink(temp_file_path)
        except:
            pass
        
        logger.error(f"Error ejecutando código: {str(e)}")
        return {
            "status": "error",
            "output": "",
            "error": f"Error de ejecución: {str(e)}"
        }