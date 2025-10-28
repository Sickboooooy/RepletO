from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.sandbox import execute_code
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RepletO", description="Entorno de ejecución de código en la nube")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str
    language: str = "python"

class CodeResponse(BaseModel):
    status: str
    output: str
    error: str = None

@app.get("/")
async def root():
    return {"message": "RepletO - Entorno de ejecución de código", "status": "running"}

@app.post("/run", response_model=CodeResponse)
async def run_code(request: CodeRequest):
    """
    Ejecuta código Python en un entorno sandbox seguro
    """
    try:
        logger.info(f"Ejecutando código: {request.code[:50]}...")
        
        result = execute_code(request.code)
        
        return CodeResponse(
            status=result["status"],
            output=result["output"],
            error=result.get("error")
        )
    
    except Exception as e:
        logger.error(f"Error ejecutando código: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Endpoint de salud del servidor"""
    return {"status": "healthy", "service": "RepletO"}