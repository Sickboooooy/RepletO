"""
💾 Gestor SQLite - RepletO v2.0

Sistema de almacenamiento persistente usando SQLite para:
- Historial de ejecuciones de código
- Configuraciones de usuario
- Snippets de código guardados
- Métricas y analytics
- Cache de resultados
"""

import sqlite3
import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import aiosqlite
import hashlib

logger = logging.getLogger(__name__)

class SQLiteManager:
    """
    Gestor de base de datos SQLite para RepletO
    """
    
    def __init__(self, db_path: str = "repleto.db"):
        """
        Inicializar gestor SQLite
        
        Args:
            db_path: Ruta del archivo de base de datos
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configuración de conexión
        self.connection_timeout = 30.0
        self.isolation_level = None  # Autocommit mode
        
        logger.info(f"SQLiteManager inicializado con DB: {self.db_path}")

    async def initialize_database(self) -> Dict[str, Any]:
        """
        Inicializar base de datos y crear tablas
        
        Returns:
            Estado de inicialización
        """
        try:
            async with aiosqlite.connect(
                self.db_path, 
                timeout=self.connection_timeout,
                isolation_level=self.isolation_level
            ) as db:
                # Habilitar foreign keys
                await db.execute("PRAGMA foreign_keys = ON")
                
                # Crear tablas
                await self._create_tables(db)
                
                # Crear índices
                await self._create_indexes(db)
                
                await db.commit()
                
                logger.info("Base de datos inicializada exitosamente")
                
                return {
                    'status': 'success',
                    'message': 'Base de datos inicializada',
                    'db_path': str(self.db_path),
                    'tables_created': True
                }
                
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'db_path': str(self.db_path)
            }

    async def _create_tables(self, db: aiosqlite.Connection):
        """Crear todas las tablas necesarias"""
        
        # Tabla de ejecuciones de código
        await db.execute("""
            CREATE TABLE IF NOT EXISTS code_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                language TEXT NOT NULL,
                code TEXT NOT NULL,
                output TEXT,
                error TEXT,
                execution_time_ms INTEGER,
                memory_used_mb REAL,
                exit_code INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT  -- JSON con datos adicionales
            )
        """)
        
        # Tabla de snippets de código
        await db.execute("""
            CREATE TABLE IF NOT EXISTS code_snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                language TEXT NOT NULL,
                code TEXT NOT NULL,
                tags TEXT,  -- JSON array
                is_favorite BOOLEAN DEFAULT FALSE,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de configuraciones
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,  -- JSON
                category TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de sesiones
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_agent TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                metadata TEXT  -- JSON
            )
        """)
        
        # Tabla de métricas
        await db.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                tags TEXT,  -- JSON
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de cache
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                cache_key TEXT PRIMARY KEY,
                cache_value TEXT NOT NULL,  -- JSON
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de archivos (tracking)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS file_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                file_size INTEGER,
                language TEXT,
                line_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_executed TIMESTAMP
            )
        """)

    async def _create_indexes(self, db: aiosqlite.Connection):
        """Crear índices para optimizar consultas"""
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_executions_session ON code_executions(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_executions_language ON code_executions(language)",
            "CREATE INDEX IF NOT EXISTS idx_executions_created ON code_executions(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_executions_hash ON code_executions(code_hash)",
            
            "CREATE INDEX IF NOT EXISTS idx_snippets_language ON code_snippets(language)",
            "CREATE INDEX IF NOT EXISTS idx_snippets_tags ON code_snippets(tags)",
            "CREATE INDEX IF NOT EXISTS idx_snippets_favorite ON code_snippets(is_favorite)",
            
            "CREATE INDEX IF NOT EXISTS idx_sessions_active ON user_sessions(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_activity ON user_sessions(last_activity)",
            
            "CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_recorded ON metrics(recorded_at)",
            
            "CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache_entries(expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_cache_accessed ON cache_entries(last_accessed)",
            
            "CREATE INDEX IF NOT EXISTS idx_files_path ON file_tracking(file_path)",
            "CREATE INDEX IF NOT EXISTS idx_files_updated ON file_tracking(updated_at)"
        ]
        
        for index_sql in indexes:
            await db.execute(index_sql)

    async def save_code_execution(self,
                                 session_id: str,
                                 code: str,
                                 language: str,
                                 output: Optional[str] = None,
                                 error: Optional[str] = None,
                                 execution_time_ms: Optional[int] = None,
                                 memory_used_mb: Optional[float] = None,
                                 exit_code: Optional[int] = None,
                                 metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Guardar ejecución de código
        
        Args:
            session_id: ID de sesión
            code: Código ejecutado
            language: Lenguaje de programación
            output: Salida de la ejecución
            error: Error de la ejecución
            execution_time_ms: Tiempo de ejecución en ms
            memory_used_mb: Memoria usada en MB
            exit_code: Código de salida
            metadata: Metadatos adicionales
            
        Returns:
            ID de la ejecución guardada
        """
        try:
            # Generar hash del código
            code_hash = hashlib.sha256(code.encode()).hexdigest()[:16]
            
            async with aiosqlite.connect(
                self.db_path, 
                timeout=self.connection_timeout
            ) as db:
                cursor = await db.execute("""
                    INSERT INTO code_executions 
                    (session_id, code_hash, language, code, output, error, 
                     execution_time_ms, memory_used_mb, exit_code, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id, code_hash, language, code, output, error,
                    execution_time_ms, memory_used_mb, exit_code,
                    json.dumps(metadata) if metadata else None
                ))
                
                await db.commit()
                execution_id = cursor.lastrowid
                
                logger.debug(f"Ejecución guardada con ID: {execution_id}")
                return execution_id
                
        except Exception as e:
            logger.error(f"Error guardando ejecución: {e}")
            raise

    async def get_execution_history(self,
                                   session_id: Optional[str] = None,
                                   language: Optional[str] = None,
                                   limit: int = 100,
                                   offset: int = 0) -> List[Dict[str, Any]]:
        """
        Obtener historial de ejecuciones
        
        Args:
            session_id: Filtrar por sesión
            language: Filtrar por lenguaje
            limit: Límite de resultados
            offset: Offset para paginación
            
        Returns:
            Lista de ejecuciones
        """
        try:
            query = """
                SELECT id, session_id, code_hash, language, code, output, error,
                       execution_time_ms, memory_used_mb, exit_code, created_at, metadata
                FROM code_executions
                WHERE 1=1
            """
            params = []
            
            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)
            
            if language:
                query += " AND language = ?"
                params.append(language)
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                
                executions = []
                for row in rows:
                    execution = dict(row)
                    if execution['metadata']:
                        execution['metadata'] = json.loads(execution['metadata'])
                    executions.append(execution)
                
                return executions
                
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []

    async def save_code_snippet(self,
                               title: str,
                               code: str,
                               language: str,
                               description: Optional[str] = None,
                               tags: Optional[List[str]] = None) -> int:
        """
        Guardar snippet de código
        
        Args:
            title: Título del snippet
            code: Código del snippet
            language: Lenguaje de programación
            description: Descripción
            tags: Lista de tags
            
        Returns:
            ID del snippet guardado
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO code_snippets 
                    (title, description, language, code, tags)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    title, description, language, code,
                    json.dumps(tags) if tags else None
                ))
                
                await db.commit()
                snippet_id = cursor.lastrowid
                
                logger.debug(f"Snippet guardado con ID: {snippet_id}")
                return snippet_id
                
        except Exception as e:
            logger.error(f"Error guardando snippet: {e}")
            raise

    async def search_snippets(self,
                             query: Optional[str] = None,
                             language: Optional[str] = None,
                             tags: Optional[List[str]] = None,
                             favorites_only: bool = False) -> List[Dict[str, Any]]:
        """
        Buscar snippets de código
        
        Args:
            query: Texto a buscar en título/descripción
            language: Filtrar por lenguaje
            tags: Filtrar por tags
            favorites_only: Solo favoritos
            
        Returns:
            Lista de snippets encontrados
        """
        try:
            sql = """
                SELECT id, title, description, language, code, tags, 
                       is_favorite, usage_count, created_at, updated_at
                FROM code_snippets
                WHERE 1=1
            """
            params = []
            
            if query:
                sql += " AND (title LIKE ? OR description LIKE ? OR code LIKE ?)"
                search_term = f"%{query}%"
                params.extend([search_term, search_term, search_term])
            
            if language:
                sql += " AND language = ?"
                params.append(language)
            
            if favorites_only:
                sql += " AND is_favorite = TRUE"
            
            sql += " ORDER BY usage_count DESC, updated_at DESC"
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(sql, params)
                rows = await cursor.fetchall()
                
                snippets = []
                for row in rows:
                    snippet = dict(row)
                    if snippet['tags']:
                        snippet['tags'] = json.loads(snippet['tags'])
                    
                    # Filtrar por tags si se especifica
                    if tags:
                        snippet_tags = snippet.get('tags', [])
                        if not any(tag in snippet_tags for tag in tags):
                            continue
                    
                    snippets.append(snippet)
                
                return snippets
                
        except Exception as e:
            logger.error(f"Error buscando snippets: {e}")
            return []

    async def increment_snippet_usage(self, snippet_id: int):
        """Incrementar contador de uso de snippet"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE code_snippets 
                    SET usage_count = usage_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (snippet_id,))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error incrementando uso de snippet: {e}")

    async def save_setting(self, key: str, value: Any, category: Optional[str] = None):
        """
        Guardar configuración de usuario
        
        Args:
            key: Clave de configuración
            value: Valor (se serializa a JSON)
            category: Categoría de la configuración
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO user_settings (key, value, category)
                    VALUES (?, ?, ?)
                """, (key, json.dumps(value), category))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            raise

    async def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Obtener configuración de usuario
        
        Args:
            key: Clave de configuración
            default: Valor por defecto
            
        Returns:
            Valor de configuración
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT value FROM user_settings WHERE key = ?", 
                    (key,)
                )
                row = await cursor.fetchone()
                
                if row:
                    return json.loads(row[0])
                return default
                
        except Exception as e:
            logger.error(f"Error obteniendo configuración: {e}")
            return default

    async def create_session(self, 
                            session_id: str,
                            user_agent: Optional[str] = None,
                            ip_address: Optional[str] = None,
                            metadata: Optional[Dict[str, Any]] = None):
        """
        Crear nueva sesión de usuario
        
        Args:
            session_id: ID único de sesión
            user_agent: User agent del navegador
            ip_address: Dirección IP
            metadata: Metadatos adicionales
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO user_sessions 
                    (session_id, user_agent, ip_address, metadata)
                    VALUES (?, ?, ?, ?)
                """, (
                    session_id, user_agent, ip_address,
                    json.dumps(metadata) if metadata else None
                ))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error creando sesión: {e}")
            raise

    async def update_session_activity(self, session_id: str):
        """Actualizar actividad de sesión"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE user_sessions 
                    SET last_activity = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                """, (session_id,))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error actualizando actividad de sesión: {e}")

    async def record_metric(self,
                           metric_name: str,
                           value: float,
                           unit: Optional[str] = None,
                           tags: Optional[Dict[str, str]] = None):
        """
        Registrar métrica
        
        Args:
            metric_name: Nombre de la métrica
            value: Valor numérico
            unit: Unidad de medida
            tags: Tags adicionales
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO metrics (metric_name, metric_value, metric_unit, tags)
                    VALUES (?, ?, ?, ?)
                """, (
                    metric_name, value, unit,
                    json.dumps(tags) if tags else None
                ))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error registrando métrica: {e}")

    async def get_metrics(self,
                         metric_name: Optional[str] = None,
                         since: Optional[datetime] = None,
                         limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Obtener métricas
        
        Args:
            metric_name: Filtrar por nombre de métrica
            since: Filtrar desde fecha
            limit: Límite de resultados
            
        Returns:
            Lista de métricas
        """
        try:
            query = """
                SELECT metric_name, metric_value, metric_unit, tags, recorded_at
                FROM metrics
                WHERE 1=1
            """
            params = []
            
            if metric_name:
                query += " AND metric_name = ?"
                params.append(metric_name)
            
            if since:
                query += " AND recorded_at >= ?"
                params.append(since.isoformat())
            
            query += " ORDER BY recorded_at DESC LIMIT ?"
            params.append(limit)
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                
                metrics = []
                for row in rows:
                    metric = dict(row)
                    if metric['tags']:
                        metric['tags'] = json.loads(metric['tags'])
                    metrics.append(metric)
                
                return metrics
                
        except Exception as e:
            logger.error(f"Error obteniendo métricas: {e}")
            return []

    async def cache_set(self,
                       key: str,
                       value: Any,
                       expires_in_seconds: Optional[int] = None):
        """
        Guardar en cache
        
        Args:
            key: Clave de cache
            value: Valor a cachear
            expires_in_seconds: Tiempo de expiración en segundos
        """
        try:
            expires_at = None
            if expires_in_seconds:
                expires_at = (datetime.now() + timedelta(seconds=expires_in_seconds)).isoformat()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO cache_entries 
                    (cache_key, cache_value, expires_at)
                    VALUES (?, ?, ?)
                """, (key, json.dumps(value), expires_at))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error guardando en cache: {e}")

    async def cache_get(self, key: str) -> Optional[Any]:
        """
        Obtener del cache
        
        Args:
            key: Clave de cache
            
        Returns:
            Valor cacheado o None si no existe/expiró
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT cache_value, expires_at 
                    FROM cache_entries 
                    WHERE cache_key = ?
                """, (key,))
                row = await cursor.fetchone()
                
                if not row:
                    return None
                
                cache_value, expires_at = row
                
                # Verificar expiración
                if expires_at:
                    expires_datetime = datetime.fromisoformat(expires_at)
                    if datetime.now() > expires_datetime:
                        # Entrada expirada, eliminarla
                        await db.execute(
                            "DELETE FROM cache_entries WHERE cache_key = ?", 
                            (key,)
                        )
                        await db.commit()
                        return None
                
                # Actualizar contador de acceso
                await db.execute("""
                    UPDATE cache_entries 
                    SET access_count = access_count + 1,
                        last_accessed = CURRENT_TIMESTAMP
                    WHERE cache_key = ?
                """, (key,))
                await db.commit()
                
                return json.loads(cache_value)
                
        except Exception as e:
            logger.error(f"Error obteniendo del cache: {e}")
            return None

    async def cleanup_expired_cache(self):
        """Limpiar entradas de cache expiradas"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    DELETE FROM cache_entries 
                    WHERE expires_at IS NOT NULL 
                    AND expires_at < ?
                """, (datetime.now().isoformat(),))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error limpiando cache expirado: {e}")

    async def get_database_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de la base de datos
        
        Returns:
            Estadísticas detalladas
        """
        try:
            stats = {}
            
            async with aiosqlite.connect(self.db_path) as db:
                # Estadísticas de tablas
                tables = [
                    'code_executions', 'code_snippets', 'user_settings',
                    'user_sessions', 'metrics', 'cache_entries', 'file_tracking'
                ]
                
                for table in tables:
                    cursor = await db.execute(f"SELECT COUNT(*) FROM {table}")
                    count = await cursor.fetchone()
                    stats[f"{table}_count"] = count[0] if count else 0
                
                # Tamaño de base de datos
                stats['db_size_bytes'] = self.db_path.stat().st_size
                stats['db_size_mb'] = round(stats['db_size_bytes'] / (1024 * 1024), 2)
                
                # Actividad reciente
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM code_executions 
                    WHERE created_at > datetime('now', '-1 day')
                """)
                count = await cursor.fetchone()
                stats['executions_last_24h'] = count[0] if count else 0
                
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM user_sessions 
                    WHERE is_active = TRUE
                """)
                count = await cursor.fetchone()
                stats['active_sessions'] = count[0] if count else 0
                
                return stats
                
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {'error': str(e)}