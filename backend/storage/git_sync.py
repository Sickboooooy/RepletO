"""
🔄 Sincronización Git Automática - RepletO v2.0

Sistema de sincronización automática con Git que permite:
- Auto-commit de cambios cada cierto tiempo
- Push/pull automático a repositorio remoto
- Seguimiento de historial de cambios
- Branching automático para experimentos
- Integración con GitHub/GitLab
"""

import asyncio
import logging
import subprocess
import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

class GitSyncManager:
    """
    Gestor de sincronización automática con Git
    """
    
    def __init__(self, 
                 repo_path: str,
                 auto_commit_interval: int = 300,  # 5 minutos
                 auto_push_interval: int = 1800,   # 30 minutos
                 enable_auto_branch: bool = True,
                 branch_prefix: str = "repleto-auto"):
        """
        Inicializar gestor de Git
        
        Args:
            repo_path: Ruta del repositorio Git
            auto_commit_interval: Intervalo de auto-commit en segundos
            auto_push_interval: Intervalo de auto-push en segundos
            enable_auto_branch: Crear branches automáticos para experimentos
            branch_prefix: Prefijo para branches automáticos
        """
        self.repo_path = Path(repo_path).resolve()
        self.auto_commit_interval = auto_commit_interval
        self.auto_push_interval = auto_push_interval
        self.enable_auto_branch = enable_auto_branch
        self.branch_prefix = branch_prefix
        
        # Estado interno
        self.last_commit_hash = None
        self.last_push_time = None
        self.auto_sync_enabled = False
        self.current_experiment_branch = None
        
        # Archivos a ignorar en auto-commits
        self.ignore_patterns = {
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '.DS_Store',
            'Thumbs.db',
            '*.tmp',
            '*.log',
            '.env',
            'node_modules'
        }
        
        logger.info(f"GitSyncManager inicializado para {self.repo_path}")

    async def initialize_repo(self) -> Dict[str, any]:
        """
        Inicializar repositorio Git si no existe
        
        Returns:
            Estado de inicialización
        """
        try:
            if not self._is_git_repo():
                await self._run_git_command(['init'])
                
                # Crear .gitignore básico
                gitignore_path = self.repo_path / '.gitignore'
                if not gitignore_path.exists():
                    gitignore_content = """# RepletO Generated Files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment
.env
.venv/
env/
venv/

# RepletO specific
repleto_temp/
*.repleto.bak
"""
                    gitignore_path.write_text(gitignore_content)
                    await self._run_git_command(['add', '.gitignore'])
                    await self._run_git_command(['commit', '-m', 'Initial RepletO setup'])
                
                logger.info("Repositorio Git inicializado")
                return {'status': 'initialized', 'message': 'Repositorio Git creado exitosamente'}
            
            else:
                status = await self.get_repo_status()
                logger.info("Repositorio Git existente detectado")
                return {'status': 'existing', 'repo_status': status}
                
        except Exception as e:
            logger.error(f"Error inicializando repositorio: {e}")
            return {'status': 'error', 'message': str(e)}

    def _is_git_repo(self) -> bool:
        """Verificar si la ruta es un repositorio Git"""
        return (self.repo_path / '.git').exists()

    async def _run_git_command(self, 
                              command: List[str], 
                              capture_output: bool = True) -> Tuple[bool, str]:
        """
        Ejecutar comando Git de forma asíncrona
        
        Args:
            command: Lista de argumentos del comando git
            capture_output: Si capturar la salida
            
        Returns:
            Tupla (éxito, salida)
        """
        try:
            full_command = ['git'] + command
            
            process = await asyncio.create_subprocess_exec(
                *full_command,
                cwd=self.repo_path,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                output = stdout.decode() if stdout else ""
                return True, output.strip()
            else:
                error = stderr.decode() if stderr else "Unknown git error"
                logger.warning(f"Git command failed: {' '.join(command)} - {error}")
                return False, error
                
        except Exception as e:
            logger.error(f"Error ejecutando git {' '.join(command)}: {e}")
            return False, str(e)

    async def get_repo_status(self) -> Dict[str, any]:
        """
        Obtener estado actual del repositorio
        
        Returns:
            Estado detallado del repositorio
        """
        try:
            if not self._is_git_repo():
                return {'status': 'not_git_repo'}
            
            # Estado de archivos
            success, status_output = await self._run_git_command(['status', '--porcelain'])
            if not success:
                return {'status': 'error', 'message': status_output}
            
            # Branch actual
            success, branch_output = await self._run_git_command(['branch', '--show-current'])
            current_branch = branch_output if success else 'unknown'
            
            # Último commit
            success, commit_output = await self._run_git_command(['log', '-1', '--oneline'])
            last_commit = commit_output if success else 'No commits'
            
            # Archivos modificados
            modified_files = []
            untracked_files = []
            staged_files = []
            
            for line in status_output.split('\n'):
                if line.strip():
                    status_code = line[:2]
                    filename = line[3:]
                    
                    if status_code == '??':
                        untracked_files.append(filename)
                    elif status_code[0] != ' ':
                        staged_files.append(filename)
                    elif status_code[1] != ' ':
                        modified_files.append(filename)
            
            # Información de remoto
            success, remote_output = await self._run_git_command(['remote', '-v'])
            remotes = {}
            if success:
                for line in remote_output.split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            url = parts[1]
                            remotes[name] = url
            
            return {
                'status': 'ok',
                'current_branch': current_branch,
                'last_commit': last_commit,
                'modified_files': modified_files,
                'untracked_files': untracked_files,
                'staged_files': staged_files,
                'remotes': remotes,
                'auto_sync_enabled': self.auto_sync_enabled,
                'last_push_time': self.last_push_time.isoformat() if self.last_push_time else None
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado del repo: {e}")
            return {'status': 'error', 'message': str(e)}

    async def stage_and_commit(self, 
                              message: Optional[str] = None,
                              files: Optional[List[str]] = None) -> Dict[str, any]:
        """
        Hacer stage y commit de archivos
        
        Args:
            message: Mensaje de commit (si None, se genera automático)
            files: Lista de archivos (si None, todos los modificados)
            
        Returns:
            Resultado del commit
        """
        try:
            if not self._is_git_repo():
                return {'status': 'error', 'message': 'No es un repositorio Git'}
            
            # Determinar archivos a commitear
            if files is None:
                # Auto-detectar archivos modificados (excluyendo patrones ignorados)
                status = await self.get_repo_status()
                if status['status'] != 'ok':
                    return status
                
                files_to_add = []
                all_files = status['modified_files'] + status['untracked_files']
                
                for file in all_files:
                    if not any(pattern in file for pattern in self.ignore_patterns):
                        files_to_add.append(file)
                
                if not files_to_add:
                    return {'status': 'no_changes', 'message': 'No hay cambios para commitear'}
                
                files = files_to_add
            
            # Hacer stage de archivos
            for file in files:
                success, output = await self._run_git_command(['add', file])
                if not success:
                    return {'status': 'error', 'message': f'Error adding {file}: {output}'}
            
            # Generar mensaje automático si no se proporciona
            if message is None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file_count = len(files)
                message = f"RepletO auto-commit: {file_count} file(s) updated at {timestamp}"
            
            # Hacer commit
            success, output = await self._run_git_command(['commit', '-m', message])
            if not success:
                return {'status': 'error', 'message': f'Error en commit: {output}'}
            
            # Obtener hash del commit
            success, hash_output = await self._run_git_command(['rev-parse', 'HEAD'])
            commit_hash = hash_output if success else 'unknown'
            
            self.last_commit_hash = commit_hash
            
            logger.info(f"Commit exitoso: {commit_hash[:8]} - {message}")
            
            return {
                'status': 'success',
                'commit_hash': commit_hash,
                'message': message,
                'files_committed': files
            }
            
        except Exception as e:
            logger.error(f"Error en stage_and_commit: {e}")
            return {'status': 'error', 'message': str(e)}

    async def push_to_remote(self, 
                            remote: str = 'origin',
                            branch: Optional[str] = None) -> Dict[str, any]:
        """
        Push a repositorio remoto
        
        Args:
            remote: Nombre del remoto
            branch: Branch a pushear (si None, usar actual)
            
        Returns:
            Resultado del push
        """
        try:
            if not self._is_git_repo():
                return {'status': 'error', 'message': 'No es un repositorio Git'}
            
            # Obtener branch actual si no se especifica
            if branch is None:
                success, branch_output = await self._run_git_command(['branch', '--show-current'])
                if not success:
                    return {'status': 'error', 'message': 'No se pudo determinar el branch actual'}
                branch = branch_output
            
            # Verificar si hay commits pendientes
            success, status = await self._run_git_command(['status', '--porcelain'])
            if success and status.strip():
                logger.info("Hay cambios pendientes, haciendo auto-commit antes del push")
                commit_result = await self.stage_and_commit()
                if commit_result['status'] != 'success':
                    return {'status': 'error', 'message': f'Auto-commit falló: {commit_result.get("message")}'}
            
            # Push
            success, output = await self._run_git_command(['push', remote, branch])
            if not success:
                # Si falla, podría ser porque el branch no existe en remoto
                if 'has no upstream branch' in output:
                    logger.info(f"Branch {branch} no existe en remoto, creando upstream")
                    success, output = await self._run_git_command(['push', '--set-upstream', remote, branch])
                
                if not success:
                    return {'status': 'error', 'message': f'Error en push: {output}'}
            
            self.last_push_time = datetime.now()
            
            logger.info(f"Push exitoso a {remote}/{branch}")
            
            return {
                'status': 'success',
                'remote': remote,
                'branch': branch,
                'push_time': self.last_push_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en push_to_remote: {e}")
            return {'status': 'error', 'message': str(e)}

    async def pull_from_remote(self, 
                              remote: str = 'origin',
                              branch: Optional[str] = None) -> Dict[str, any]:
        """
        Pull desde repositorio remoto
        
        Args:
            remote: Nombre del remoto
            branch: Branch a pullear (si None, usar actual)
            
        Returns:
            Resultado del pull
        """
        try:
            if not self._is_git_repo():
                return {'status': 'error', 'message': 'No es un repositorio Git'}
            
            # Obtener branch actual si no se especifica
            if branch is None:
                success, branch_output = await self._run_git_command(['branch', '--show-current'])
                if not success:
                    return {'status': 'error', 'message': 'No se pudo determinar el branch actual'}
                branch = branch_output
            
            # Pull
            success, output = await self._run_git_command(['pull', remote, branch])
            if not success:
                return {'status': 'error', 'message': f'Error en pull: {output}'}
            
            logger.info(f"Pull exitoso desde {remote}/{branch}")
            
            return {
                'status': 'success',
                'remote': remote,
                'branch': branch,
                'output': output
            }
            
        except Exception as e:
            logger.error(f"Error en pull_from_remote: {e}")
            return {'status': 'error', 'message': str(e)}

    async def create_experiment_branch(self, experiment_name: Optional[str] = None) -> Dict[str, any]:
        """
        Crear branch para experimento
        
        Args:
            experiment_name: Nombre del experimento (si None, se genera automático)
            
        Returns:
            Información del branch creado
        """
        try:
            if not self._is_git_repo():
                return {'status': 'error', 'message': 'No es un repositorio Git'}
            
            if not self.enable_auto_branch:
                return {'status': 'disabled', 'message': 'Auto-branching está deshabilitado'}
            
            # Generar nombre automático si no se proporciona
            if experiment_name is None:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                experiment_name = f"experiment-{timestamp}"
            
            branch_name = f"{self.branch_prefix}-{experiment_name}"
            
            # Crear y cambiar al nuevo branch
            success, output = await self._run_git_command(['checkout', '-b', branch_name])
            if not success:
                return {'status': 'error', 'message': f'Error creando branch: {output}'}
            
            self.current_experiment_branch = branch_name
            
            logger.info(f"Branch de experimento creado: {branch_name}")
            
            return {
                'status': 'success',
                'branch_name': branch_name,
                'experiment_name': experiment_name
            }
            
        except Exception as e:
            logger.error(f"Error creando experiment branch: {e}")
            return {'status': 'error', 'message': str(e)}

    async def merge_experiment(self, 
                              experiment_branch: str,
                              target_branch: str = 'main',
                              delete_after_merge: bool = True) -> Dict[str, any]:
        """
        Mergear branch de experimento
        
        Args:
            experiment_branch: Branch de experimento a mergear
            target_branch: Branch destino
            delete_after_merge: Eliminar branch después del merge
            
        Returns:
            Resultado del merge
        """
        try:
            if not self._is_git_repo():
                return {'status': 'error', 'message': 'No es un repositorio Git'}
            
            # Cambiar al branch destino
            success, output = await self._run_git_command(['checkout', target_branch])
            if not success:
                return {'status': 'error', 'message': f'Error cambiando a {target_branch}: {output}'}
            
            # Mergear
            success, output = await self._run_git_command(['merge', experiment_branch])
            if not success:
                return {'status': 'error', 'message': f'Error en merge: {output}'}
            
            # Eliminar branch si se solicita
            if delete_after_merge:
                success, del_output = await self._run_git_command(['branch', '-d', experiment_branch])
                if not success:
                    logger.warning(f"No se pudo eliminar branch {experiment_branch}: {del_output}")
            
            if self.current_experiment_branch == experiment_branch:
                self.current_experiment_branch = None
            
            logger.info(f"Experiment branch {experiment_branch} mergeado exitosamente")
            
            return {
                'status': 'success',
                'experiment_branch': experiment_branch,
                'target_branch': target_branch,
                'deleted': delete_after_merge
            }
            
        except Exception as e:
            logger.error(f"Error en merge_experiment: {e}")
            return {'status': 'error', 'message': str(e)}

    async def start_auto_sync(self) -> Dict[str, any]:
        """
        Iniciar sincronización automática
        
        Returns:
            Estado de inicio
        """
        try:
            if self.auto_sync_enabled:
                return {'status': 'already_running', 'message': 'Auto-sync ya está activo'}
            
            self.auto_sync_enabled = True
            
            # Iniciar tareas en background
            asyncio.create_task(self._auto_commit_task())
            asyncio.create_task(self._auto_push_task())
            
            logger.info("Auto-sync iniciado")
            
            return {
                'status': 'started',
                'commit_interval': self.auto_commit_interval,
                'push_interval': self.auto_push_interval
            }
            
        except Exception as e:
            logger.error(f"Error iniciando auto-sync: {e}")
            return {'status': 'error', 'message': str(e)}

    async def stop_auto_sync(self) -> Dict[str, any]:
        """
        Detener sincronización automática
        
        Returns:
            Estado de parada
        """
        self.auto_sync_enabled = False
        logger.info("Auto-sync detenido")
        
        return {'status': 'stopped'}

    async def _auto_commit_task(self):
        """Tarea de auto-commit en background"""
        while self.auto_sync_enabled:
            try:
                await asyncio.sleep(self.auto_commit_interval)
                
                if not self.auto_sync_enabled:
                    break
                
                # Verificar si hay cambios
                status = await self.get_repo_status()
                if status['status'] == 'ok':
                    has_changes = (status['modified_files'] or 
                                 status['untracked_files'])
                    
                    if has_changes:
                        result = await self.stage_and_commit()
                        if result['status'] == 'success':
                            logger.info(f"Auto-commit exitoso: {result['commit_hash'][:8]}")
                        else:
                            logger.warning(f"Auto-commit falló: {result.get('message')}")
                
            except Exception as e:
                logger.error(f"Error en auto-commit task: {e}")

    async def _auto_push_task(self):
        """Tarea de auto-push en background"""
        while self.auto_sync_enabled:
            try:
                await asyncio.sleep(self.auto_push_interval)
                
                if not self.auto_sync_enabled:
                    break
                
                # Solo push si hay commits locales pendientes
                success, output = await self._run_git_command(['status', '--ahead-behind'])
                if success and 'ahead' in output:
                    result = await self.push_to_remote()
                    if result['status'] == 'success':
                        logger.info("Auto-push exitoso")
                    else:
                        logger.warning(f"Auto-push falló: {result.get('message')}")
                
            except Exception as e:
                logger.error(f"Error en auto-push task: {e}")

    async def get_commit_history(self, limit: int = 10) -> List[Dict[str, any]]:
        """
        Obtener historial de commits
        
        Args:
            limit: Número máximo de commits
            
        Returns:
            Lista de commits
        """
        try:
            if not self._is_git_repo():
                return []
            
            # Obtener commits con formato personalizado
            success, output = await self._run_git_command([
                'log', 
                f'--max-count={limit}',
                '--pretty=format:%H|%an|%ae|%ad|%s',
                '--date=iso'
            ])
            
            if not success:
                return []
            
            commits = []
            for line in output.split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 5:
                        commits.append({
                            'hash': parts[0],
                            'author_name': parts[1],
                            'author_email': parts[2],
                            'date': parts[3],
                            'message': '|'.join(parts[4:])  # En caso de que el mensaje tenga |
                        })
            
            return commits
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []