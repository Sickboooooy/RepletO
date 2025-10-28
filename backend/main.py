"""
🎨 RepletO v2.0 - Backend Principal
IDE Web Híbrido Autoalojado con Ejecución en Sandbox y IA Integrada

Características:
- FastAPI + WebSockets para tiempo real
- Múltiples lenguajes (Python, Node.js)
- Integración Jupyter nativa
- Asistencia IA orquestada
- Auto-sincronización Git
- Renderizado de visualizaciones
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
import asyncio
import json
import logging
import os
from datetime import datetime
import uuid

# Importar módulos locales
from backend.execution.sandbox import SecureSandbox
from backend.execution.jupyter_kernel import JupyterKernelManager
from backend.ai.assistant import AIAssistant
from backend.storage.git_sync import GitAutoSync
from backend.storage.sqlite_manager import SQLiteManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="RepletO v2.0",
    description="IDE Web Híbrido Autoalojado",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción usar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class CodeExecutionRequest(BaseModel):
    code: str = Field(..., description="Código a ejecutar")
    language: str = Field(default="python", description="Lenguaje de programación")
    mode: str = Field(default="script", description="Modo: script, notebook, repl")
    session_id: Optional[str] = Field(default=None, description="ID de sesión para kernels persistentes")
    timeout: Optional[int] = Field(default=30, ge=1, le=120, description="Timeout en segundos")

class CodeExecutionResponse(BaseModel):
    status: str = Field(..., description="success, error, timeout")
    output: str = Field(default="", description="Salida estándar")
    error: Optional[str] = Field(default=None, description="Mensajes de error")
    execution_time: float = Field(..., description="Tiempo de ejecución en segundos")
    visualizations: List[str] = Field(default=[], description="Imágenes base64")
    data: Dict[str, Any] = Field(default={}, description="Datos estructurados")
    session_id: Optional[str] = Field(default=None, description="ID de sesión")

class AICompletionRequest(BaseModel):
    code: str = Field(..., description="Código actual")
    cursor_position: int = Field(..., description="Posición del cursor")
    language: str = Field(default="python", description="Lenguaje")

class AIExplanationRequest(BaseModel):
    code: str = Field(..., description="Código con error")
    error: str = Field(..., description="Mensaje de error")
    language: str = Field(default="python", description="Lenguaje")

# Instancias globales
sandbox = SecureSandbox()
jupyter_manager = JupyterKernelManager()
ai_assistant = AIAssistant()
git_sync = GitAutoSync(repo_path=".")
db_manager = SQLiteManager()

# Gestionar conexiones WebSocket activas
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket conectado. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket desconectado. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error enviando mensaje WebSocket: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error en broadcast: {e}")
                disconnected.append(connection)
        
        # Remover conexiones muertas
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# === ENDPOINTS REST ===

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página principal - redirige al frontend"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RepletO v2.0</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .logo { font-size: 3em; color: #2196F3; margin-bottom: 20px; }
            .subtitle { color: #666; margin-bottom: 30px; }
            .status { background: #4CAF50; color: white; padding: 10px 20px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="logo">🎨 RepletO v2.0</div>
        <div class="subtitle">IDE Web Híbrido Autoalojado</div>
        <div class="status">✅ Backend Funcionando</div>
        <p><a href="/api/docs">📖 Documentación API</a></p>
        <p><a href="/frontend/">🚀 Abrir Editor</a></p>
    </body>
    </html>
    """

@app.get("/api/health")
async def health_check():
    """Endpoint de salud del sistema"""
    return {
        "status": "healthy",
        "service": "RepletO v2.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "sandbox": "operational",
            "jupyter": "operational",
            "ai_assistant": "operational",
            "git_sync": "operational",
            "database": "operational"
        }
    }

@app.post("/api/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """
    Ejecuta código en sandbox seguro
    
    Soporta múltiples modos:
    - script: Ejecución única sin estado
    - notebook: Kernel persistente estilo Jupyter
    - repl: REPL interactivo
    """
    try:
        logger.info(f"Ejecutando código {request.language} en modo {request.mode}")
        
        # Generar session_id si no se proporciona
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        # Elegir método de ejecución según el modo
        if request.mode == "notebook":
            result = await jupyter_manager.execute_cell(
                session_id=request.session_id,
                code=request.code,
                timeout=request.timeout
            )
        elif request.mode == "repl":
            # TODO: Implementar REPL mode
            result = await sandbox.execute_python(
                code=request.code,
                timeout=request.timeout
            )
        else:  # script mode
            if request.language == "python":
                result = await sandbox.execute_python(
                    code=request.code,
                    timeout=request.timeout
                )
            elif request.language == "javascript":
                result = await sandbox.execute_javascript(
                    code=request.code,
                    timeout=request.timeout
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Lenguaje no soportado: {request.language}"
                )
        
        # Guardar ejecución en base de datos
        db_manager.save_execution(
            session_id=request.session_id,
            code=request.code,
            language=request.language,
            result=result
        )
        
        # Auto-commit si hay cambios
        if git_sync.has_changes():
            await git_sync.auto_commit(f"Ejecución {request.language}: {datetime.now()}")
        
        return CodeExecutionResponse(
            **result,
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Error ejecutando código: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )

@app.post("/api/ai/complete")
async def ai_code_completion(request: AICompletionRequest):
    """Autocompletado de código con IA"""
    try:
        suggestions = await ai_assistant.complete_code(
            code=request.code,
            cursor_position=request.cursor_position,
            language=request.language
        )
        
        return {
            "suggestions": suggestions,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error en AI completion: {str(e)}")
        return {
            "suggestions": [],
            "status": "error",
            "error": str(e)
        }

@app.post("/api/ai/explain")
async def ai_error_explanation(request: AIExplanationRequest):
    """Explicación de errores con IA"""
    try:
        explanation = await ai_assistant.explain_error(
            code=request.code,
            error=request.error,
            language=request.language
        )
        
        return {
            "explanation": explanation,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error en AI explanation: {str(e)}")
        return {
            "explanation": {
                "summary": "Error al analizar el código",
                "suggestion": "Verifica la sintaxis y vuelve a intentar"
            },
            "status": "error",
            "error": str(e)
        }

@app.get("/api/git/status")
async def git_status():
    """Estado del repositorio Git"""
    try:
        status = git_sync.get_status()
        return {
            "status": "success",
            "git_status": status
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/api/git/sync")
async def git_sync_now():
    """Sincronizar con repositorio remoto"""
    try:
        result = await git_sync.sync()
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/api/sessions")
async def get_sessions():
    """Listar sesiones activas"""
    sessions = jupyter_manager.list_sessions()
    return {
        "sessions": sessions,
        "total": len(sessions)
    }

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Eliminar sesión específica"""
    try:
        jupyter_manager.kill_session(session_id)
        return {"status": "success", "message": f"Sesión {session_id} eliminada"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# === WEBSOCKET ENDPOINTS ===

@app.websocket("/api/ws/execute")
async def websocket_execute(websocket: WebSocket):
    """
    WebSocket para ejecución en tiempo real
    
    Permite:
    - Streaming de output
    - Control de ejecución (pause/resume/stop)
    - Visualizaciones progresivas
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Recibir mensaje del cliente
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "execute":
                # Ejecutar código con streaming
                await stream_execution(websocket, message)
            
            elif message["type"] == "interrupt":
                # Interrumpir ejecución
                session_id = message.get("session_id")
                if session_id:
                    jupyter_manager.interrupt_session(session_id)
                    await websocket.send_text(json.dumps({
                        "type": "interrupted",
                        "session_id": session_id
                    }))
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Cliente WebSocket desconectado")
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        manager.disconnect(websocket)

async def stream_execution(websocket: WebSocket, message: dict):
    """Ejecuta código con streaming de output"""
    try:
        code = message["code"]
        language = message.get("language", "python")
        session_id = message.get("session_id", str(uuid.uuid4()))
        
        # Enviar confirmación de inicio
        await websocket.send_text(json.dumps({
            "type": "execution_started",
            "session_id": session_id
        }))
        
        # Ejecutar con callback para streaming
        async def output_callback(output_type: str, content: str):
            await websocket.send_text(json.dumps({
                "type": "output",
                "output_type": output_type,
                "content": content,
                "session_id": session_id
            }))
        
        # Ejecutar código
        if language == "python":
            result = await jupyter_manager.execute_cell_streaming(
                session_id=session_id,
                code=code,
                output_callback=output_callback
            )
        else:
            result = await sandbox.execute_streaming(
                code=code,
                language=language,
                output_callback=output_callback
            )
        
        # Enviar resultado final
        await websocket.send_text(json.dumps({
            "type": "execution_complete",
            "result": result,
            "session_id": session_id
        }))
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "execution_error",
            "error": str(e),
            "session_id": session_id
        }))

# === EVENTOS DE STARTUP/SHUTDOWN ===

@app.on_event("startup")
async def startup_event():
    """Inicialización del sistema"""
    logger.info("🚀 Iniciando RepletO v2.0...")
    
    # Inicializar base de datos
    db_manager.initialize()
    
    # Configurar Git auto-sync
    git_sync.start_auto_sync(interval_minutes=5)
    
    # Verificar extensiones VS Code
    # TODO: Integrar con VS Code extensions API
    
    logger.info("✅ RepletO v2.0 iniciado correctamente")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar"""
    logger.info("🔄 Cerrando RepletO v2.0...")
    
    # Cerrar kernels Jupyter
    jupyter_manager.shutdown_all()
    
    # Commit final
    if git_sync.has_changes():
        await git_sync.auto_commit("Auto-save al cerrar RepletO")
    
    logger.info("✅ RepletO v2.0 cerrado correctamente")

# Montar archivos estáticos
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )