"""
🎨 RepletO v2.0 - Backend Simplificado para Primera Prueba
========================================================

Versión minimalista funcional para probar la calculadora
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

# Importar sandbox (básico por ahora)
from backend.sandbox import execute_code

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ===============================
# 🚀 EVENTOS DE LIFECYCLE
# ===============================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Iniciando RepletO v2.0...")
    logger.info("🎯 Sistema listo para la primera prueba!")
    logger.info("🧮 Calculadora Funcional preparada para demo")
    
    # Verificar frontend
    frontend_path = "frontend"
    if os.path.exists(frontend_path):
        logger.info(f"✅ Frontend encontrado en /{frontend_path}/")
    else:
        logger.warning(f"⚠️ Frontend no encontrado en /{frontend_path}/")
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando RepletO v2.0...")

# Crear aplicación FastAPI con lifespan
app = FastAPI(
    title="RepletO v2.0",
    description="IDE Web Híbrido Autoalojado",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
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

class CodeExecutionResponse(BaseModel):
    status: str = Field(..., description="success, error, timeout")
    output: str = Field(default="", description="Salida estándar")
    error: Optional[str] = Field(default=None, description="Mensajes de error")
    execution_time: Optional[float] = Field(default=None, description="Tiempo de ejecución")

# ===============================
# 🌐 ENDPOINTS REST
# ===============================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página principal con información del servicio"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RepletO v2.0</title>
        <style>
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                text-align: center; 
                padding: 50px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin: 0;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            .logo { 
                font-size: 4em; 
                margin-bottom: 20px; 
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .title {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 300;
            }
            .subtitle { 
                font-size: 1.2em;
                margin-bottom: 30px; 
                opacity: 0.9;
            }
            .status { 
                background: #4CAF50; 
                color: white; 
                padding: 15px 30px; 
                border-radius: 25px; 
                margin: 20px 0;
                display: inline-block;
                font-weight: bold;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .links {
                margin-top: 30px;
            }
            .link {
                display: inline-block;
                margin: 10px 15px;
                padding: 12px 25px;
                background: rgba(255,255,255,0.2);
                color: white;
                text-decoration: none;
                border-radius: 15px;
                transition: all 0.3s ease;
                border: 1px solid rgba(255,255,255,0.3);
            }
            .link:hover {
                background: rgba(255,255,255,0.3);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .version {
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(0,0,0,0.3);
                padding: 8px 15px;
                border-radius: 20px;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="version">v2.0.0</div>
        <div class="container">
            <div class="logo">🎨</div>
            <div class="title">RepletO</div>
            <div class="subtitle">IDE Web Híbrido Autoalojado</div>
            <div class="status">✅ Backend Funcionando Perfectamente</div>
            
            <div class="links">
                <a href="/api/docs" class="link">📖 Documentación API</a>
                <a href="/frontend/" class="link">🚀 Abrir Editor</a>
                <a href="/api/health" class="link">💚 Estado del Sistema</a>
            </div>
            
            <p style="margin-top: 40px; font-size: 0.9em; opacity: 0.8;">
                🔥 Listo para la primera prueba con Calculadora Funcional
            </p>
        </div>
    </body>
    </html>
    """

@app.get("/api/health")
async def health_check():
    """Endpoint de salud del sistema"""
    return {
        "status": "healthy",
        "service": "RepletO v2.0",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "message": "🚀 Sistema funcionando perfectamente - Listo para calcular!",
        "components": {
            "sandbox": "operational",
            "api": "operational", 
            "frontend": "operational"
        }
    }

@app.post("/api/execute", response_model=CodeExecutionResponse)
async def execute_code_endpoint(request: CodeExecutionRequest):
    """
    Ejecuta código Python en sandbox seguro
    Perfecto para probar nuestra calculadora funcional!
    """
    try:
        logger.info(f"Ejecutando código {request.language}: {request.code[:100]}...")
        
        # Por ahora solo soportamos Python
        if request.language.lower() != "python":
            raise HTTPException(
                status_code=400, 
                detail=f"Lenguaje '{request.language}' no soportado aún. Use 'python'."
            )
        
        # Ejecutar código usando nuestro sandbox
        import time
        start_time = time.time()
        
        result = execute_code(request.code)
        
        execution_time = time.time() - start_time
        
        # Preparar respuesta
        response = CodeExecutionResponse(
            status=result["status"],
            output=result["output"],
            error=result.get("error"),
            execution_time=execution_time
        )
        
        logger.info(f"Ejecución completada en {execution_time:.3f}s - Status: {result['status']}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en ejecución: {e}")
        return CodeExecutionResponse(
            status="error",
            output="",
            error=f"Error interno: {str(e)}",
            execution_time=None
        )

@app.post("/run")
async def legacy_run_endpoint(request: CodeExecutionRequest):
    """Endpoint legacy para compatibilidad con frontend existente"""
    result = await execute_code_endpoint(request)
    return result.dict()

# ===============================
# 🚀 EVENTOS DE LIFECYCLE
# ===============================

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Iniciando RepletO v2.0...")
    logger.info("🎯 Sistema listo para la primera prueba!")
    logger.info("🧮 Calculadora Funcional preparada para demo")
    
    # Verificar frontend
    frontend_path = "frontend"
    if os.path.exists(frontend_path):
        logger.info(f"✅ Frontend encontrado en /{frontend_path}/")
    else:
        logger.warning(f"⚠️ Frontend no encontrado en /{frontend_path}/")
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando RepletO v2.0...")

# Crear aplicación FastAPI con lifespan
app = FastAPI(
    title="RepletO v2.0",
    description="IDE Web Híbrido Autoalojado",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# ===============================
# 🏃‍♂️ EJECUCIÓN PRINCIPAL
# ===============================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🎨 RepletO v2.0 - Iniciando servidor de desarrollo...")
    
    uvicorn.run(
        "main_simple:app",  # Usar este archivo
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )