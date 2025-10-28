"""
🔬 Jupyter Kernel Manager - RepletO v2.0

Sistema de gestión de kernels Jupyter para ejecución persistente:
- Kernels reutilizables con estado compartido
- Integración nativa con Jupyter ecosystem
- Soporte para visualizaciones interactivas
- Streaming de output en tiempo real
- Gestión automática de memoria
"""

import asyncio
import json
import uuid
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import threading
import queue

try:
    from jupyter_client import KernelManager, AsyncKernelManager
    from jupyter_client.kernelspec import KernelSpecManager
    JUPYTER_AVAILABLE = True
except ImportError:
    JUPYTER_AVAILABLE = False
    KernelManager = None
    AsyncKernelManager = None

logger = logging.getLogger(__name__)

class JupyterKernelManager:
    """
    Gestor de kernels Jupyter para ejecución persistente
    """
    
    def __init__(self, max_kernels: int = 10, kernel_timeout: int = 3600):
        """
        Inicializar gestor de kernels
        
        Args:
            max_kernels: Número máximo de kernels simultáneos
            kernel_timeout: Timeout de kernels inactivos en segundos
        """
        if not JUPYTER_AVAILABLE:
            logger.warning("Jupyter no disponible - funcionalidad limitada")
            self.available = False
            return
            
        self.available = True
        self.max_kernels = max_kernels
        self.kernel_timeout = kernel_timeout
        
        # Diccionario de kernels activos: session_id -> kernel_info
        self.kernels: Dict[str, Dict[str, Any]] = {}
        
        # Gestor de especificaciones de kernel
        self.kernel_spec_manager = KernelSpecManager()
        
        # Thread para limpieza automática
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        
        logger.info(f"JupyterKernelManager inicializado (max_kernels={max_kernels})")

    def _cleanup_worker(self):
        """Worker para limpiar kernels inactivos"""
        while True:
            try:
                self._cleanup_inactive_kernels()
                # Verificar cada 5 minutos
                threading.Event().wait(300)
            except Exception as e:
                logger.error(f"Error en cleanup worker: {e}")

    def _cleanup_inactive_kernels(self):
        """Eliminar kernels que han estado inactivos demasiado tiempo"""
        current_time = datetime.now()
        inactive_sessions = []
        
        for session_id, kernel_info in self.kernels.items():
            last_activity = kernel_info.get('last_activity', current_time)
            if (current_time - last_activity).total_seconds() > self.kernel_timeout:
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            logger.info(f"Eliminando kernel inactivo: {session_id}")
            self.kill_session(session_id)

    def get_or_create_kernel(self, session_id: str, kernel_name: str = 'python3') -> Dict[str, Any]:
        """
        Obtener kernel existente o crear uno nuevo
        
        Args:
            session_id: ID de la sesión
            kernel_name: Nombre del kernel (python3, javascript, etc.)
            
        Returns:
            Información del kernel
        """
        if not self.available:
            raise RuntimeError("Jupyter no está disponible")
        
        # Si el kernel ya existe, actualizamos su actividad
        if session_id in self.kernels:
            self.kernels[session_id]['last_activity'] = datetime.now()
            return self.kernels[session_id]
        
        # Verificar límite de kernels
        if len(self.kernels) >= self.max_kernels:
            # Eliminar el kernel más antiguo
            oldest_session = min(
                self.kernels.keys(),
                key=lambda k: self.kernels[k]['last_activity']
            )
            logger.info(f"Límite de kernels alcanzado, eliminando: {oldest_session}")
            self.kill_session(oldest_session)
        
        # Crear nuevo kernel
        try:
            km = KernelManager(kernel_name=kernel_name)
            km.start_kernel()
            kc = km.client()
            kc.start_channels()
            
            # Esperar a que el kernel esté listo
            kc.wait_for_ready(timeout=30)
            
            kernel_info = {
                'kernel_manager': km,
                'kernel_client': kc,
                'kernel_name': kernel_name,
                'session_id': session_id,
                'created_at': datetime.now(),
                'last_activity': datetime.now(),
                'execution_count': 0
            }
            
            self.kernels[session_id] = kernel_info
            logger.info(f"Kernel creado: {session_id} ({kernel_name})")
            
            return kernel_info
            
        except Exception as e:
            logger.error(f"Error creando kernel {session_id}: {e}")
            raise

    async def execute_cell(self, 
                          session_id: str, 
                          code: str,
                          timeout: int = 30) -> Dict[str, Any]:
        """
        Ejecutar código en un kernel específico
        
        Args:
            session_id: ID de la sesión
            code: Código a ejecutar
            timeout: Timeout en segundos
            
        Returns:
            Resultado de la ejecución
        """
        if not self.available:
            # Fallback al sandbox básico
            from .sandbox import SecureSandbox
            sandbox = SecureSandbox()
            return await sandbox.execute_python(code, timeout)
        
        try:
            # Obtener o crear kernel
            kernel_info = self.get_or_create_kernel(session_id)
            kc = kernel_info['kernel_client']
            
            # Incrementar contador de ejecución
            kernel_info['execution_count'] += 1
            kernel_info['last_activity'] = datetime.now()
            
            start_time = datetime.now()
            
            # Ejecutar código
            msg_id = kc.execute(code, silent=False, store_history=True)
            
            # Recolectar outputs
            outputs = []
            execution_result = None
            error_output = None
            
            # Esperar mensajes del kernel
            deadline = datetime.now() + timedelta(seconds=timeout)
            
            while datetime.now() < deadline:
                try:
                    # Verificar mensajes disponibles
                    if kc.iopub_channel.msg_ready():
                        msg = kc.get_iopub_msg(timeout=1)
                        
                        if msg['parent_header'].get('msg_id') == msg_id:
                            msg_type = msg['msg_type']
                            content = msg['content']
                            
                            if msg_type == 'stream':
                                # Output de print statements
                                outputs.append({
                                    'type': 'stream',
                                    'name': content['name'],
                                    'text': content['text']
                                })
                            
                            elif msg_type == 'execute_result':
                                # Resultado de expresiones
                                execution_result = content
                                outputs.append({
                                    'type': 'execute_result',
                                    'data': content['data'],
                                    'metadata': content.get('metadata', {})
                                })
                            
                            elif msg_type == 'display_data':
                                # Visualizaciones (matplotlib, etc.)
                                outputs.append({
                                    'type': 'display_data',
                                    'data': content['data'],
                                    'metadata': content.get('metadata', {})
                                })
                            
                            elif msg_type == 'error':
                                # Errores de ejecución
                                error_output = {
                                    'ename': content['ename'],
                                    'evalue': content['evalue'],
                                    'traceback': content['traceback']
                                }
                            
                            elif msg_type == 'status' and content['execution_state'] == 'idle':
                                # Ejecución completada
                                break
                    
                    # Verificar si hay respuesta en shell channel
                    if kc.shell_channel.msg_ready():
                        reply = kc.get_shell_msg(timeout=1)
                        if reply['parent_header'].get('msg_id') == msg_id:
                            if reply['content']['status'] != 'ok':
                                if not error_output:
                                    error_output = reply['content']
                            break
                    
                    # Pequeña pausa para no saturar
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Error procesando mensaje: {e}")
                    continue
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Procesar outputs
            output_text = ""
            visualizations = []
            data = {}
            
            for output in outputs:
                if output['type'] == 'stream':
                    output_text += output['text']
                elif output['type'] in ['execute_result', 'display_data']:
                    output_data = output['data']
                    
                    # Texto plano
                    if 'text/plain' in output_data:
                        output_text += output_data['text/plain'] + "\n"
                    
                    # Imágenes (matplotlib, etc.)
                    if 'image/png' in output_data:
                        visualizations.append(output_data['image/png'])
                    
                    # Datos HTML (pandas DataFrames)
                    if 'text/html' in output_data:
                        data['html'] = output_data['text/html']
                    
                    # Datos JSON
                    if 'application/json' in output_data:
                        data['json'] = output_data['application/json']
            
            # Determinar estado
            if error_output:
                status = "error"
                error_message = f"{error_output['ename']}: {error_output['evalue']}"
                if 'traceback' in error_output:
                    error_message += "\n" + "\n".join(error_output['traceback'])
            else:
                status = "success"
                error_message = None
            
            return {
                "status": status,
                "output": output_text.strip(),
                "error": error_message,
                "execution_time": execution_time,
                "visualizations": visualizations,
                "data": data,
                "execution_count": kernel_info['execution_count']
            }
            
        except Exception as e:
            logger.error(f"Error en ejecución Jupyter: {e}")
            return {
                "status": "error",
                "output": "",
                "error": f"Error interno del kernel: {str(e)}",
                "execution_time": 0.0,
                "visualizations": [],
                "data": {},
                "execution_count": 0
            }

    async def execute_cell_streaming(self,
                                   session_id: str,
                                   code: str,
                                   output_callback: Callable[[str, str], None],
                                   timeout: int = 30) -> Dict[str, Any]:
        """
        Ejecutar código con streaming de output en tiempo real
        
        Args:
            session_id: ID de la sesión
            code: Código a ejecutar
            output_callback: Función para enviar output en tiempo real
            timeout: Timeout en segundos
            
        Returns:
            Resultado final de la ejecución
        """
        if not self.available:
            # Fallback al sandbox básico
            from .sandbox import SecureSandbox
            sandbox = SecureSandbox()
            return await sandbox.execute_streaming(code, "python", output_callback, timeout)
        
        try:
            # Obtener o crear kernel
            kernel_info = self.get_or_create_kernel(session_id)
            kc = kernel_info['kernel_client']
            
            kernel_info['execution_count'] += 1
            kernel_info['last_activity'] = datetime.now()
            
            start_time = datetime.now()
            
            # Ejecutar código
            msg_id = kc.execute(code, silent=False, store_history=True)
            
            # Variables para resultado final
            final_output = ""
            final_error = None
            visualizations = []
            data = {}
            
            # Stream outputs en tiempo real
            deadline = datetime.now() + timedelta(seconds=timeout)
            
            while datetime.now() < deadline:
                try:
                    if kc.iopub_channel.msg_ready():
                        msg = kc.get_iopub_msg(timeout=1)
                        
                        if msg['parent_header'].get('msg_id') == msg_id:
                            msg_type = msg['msg_type']
                            content = msg['content']
                            
                            if msg_type == 'stream':
                                text = content['text']
                                final_output += text
                                # Enviar en tiempo real
                                await output_callback('stdout', text)
                            
                            elif msg_type == 'execute_result':
                                if 'text/plain' in content['data']:
                                    text = content['data']['text/plain']
                                    final_output += text + "\n"
                                    await output_callback('result', text)
                            
                            elif msg_type == 'display_data':
                                # Visualizaciones
                                if 'image/png' in content['data']:
                                    visualizations.append(content['data']['image/png'])
                                    await output_callback('visualization', 'Plot generado')
                            
                            elif msg_type == 'error':
                                error_text = f"{content['ename']}: {content['evalue']}"
                                final_error = error_text
                                await output_callback('stderr', error_text)
                            
                            elif msg_type == 'status' and content['execution_state'] == 'idle':
                                break
                    
                    if kc.shell_channel.msg_ready():
                        reply = kc.get_shell_msg(timeout=1)
                        if reply['parent_header'].get('msg_id') == msg_id:
                            break
                    
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Error en streaming: {e}")
                    continue
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": "success" if not final_error else "error",
                "output": final_output.strip(),
                "error": final_error,
                "execution_time": execution_time,
                "visualizations": visualizations,
                "data": data,
                "execution_count": kernel_info['execution_count']
            }
            
        except Exception as e:
            error_msg = f"Error en streaming Jupyter: {str(e)}"
            await output_callback('stderr', error_msg)
            return {
                "status": "error",
                "output": "",
                "error": error_msg,
                "execution_time": 0.0,
                "visualizations": [],
                "data": {},
                "execution_count": 0
            }

    def interrupt_session(self, session_id: str) -> bool:
        """
        Interrumpir ejecución en una sesión específica
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            True si se interrumpió correctamente
        """
        if session_id not in self.kernels:
            return False
        
        try:
            km = self.kernels[session_id]['kernel_manager']
            km.interrupt_kernel()
            logger.info(f"Kernel interrumpido: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error interrumpiendo kernel {session_id}: {e}")
            return False

    def kill_session(self, session_id: str) -> bool:
        """
        Eliminar una sesión específica
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            True si se eliminó correctamente
        """
        if session_id not in self.kernels:
            return False
        
        try:
            kernel_info = self.kernels[session_id]
            kc = kernel_info['kernel_client']
            km = kernel_info['kernel_manager']
            
            # Cerrar canales y kernel
            kc.stop_channels()
            km.shutdown_kernel(now=True)
            
            # Remover del diccionario
            del self.kernels[session_id]
            
            logger.info(f"Kernel eliminado: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando kernel {session_id}: {e}")
            return False

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        Listar todas las sesiones activas
        
        Returns:
            Lista de información de sesiones
        """
        sessions = []
        
        for session_id, kernel_info in self.kernels.items():
            sessions.append({
                'session_id': session_id,
                'kernel_name': kernel_info['kernel_name'],
                'created_at': kernel_info['created_at'].isoformat(),
                'last_activity': kernel_info['last_activity'].isoformat(),
                'execution_count': kernel_info['execution_count']
            })
        
        return sessions

    def shutdown_all(self):
        """Cerrar todos los kernels activos"""
        session_ids = list(self.kernels.keys())
        
        for session_id in session_ids:
            self.kill_session(session_id)
        
        logger.info(f"Todos los kernels cerrados ({len(session_ids)} kernels)")

    def get_available_kernels(self) -> List[str]:
        """
        Obtener lista de kernels disponibles
        
        Returns:
            Lista de nombres de kernels
        """
        if not self.available:
            return ['python3']  # Fallback básico
        
        try:
            return list(self.kernel_spec_manager.get_all_specs().keys())
        except Exception as e:
            logger.error(f"Error obteniendo kernels disponibles: {e}")
            return ['python3']