"""
🎨 RepletO v2.0 - Servidor SIMPLE sin Auto-reload
=================================================

Versión estable sin problemas de uvicorn reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI SIMPLE
app = FastAPI(title="RepletO v2.0", version="2.0.0-simple")

# CORS básico
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    logger.info("Accediendo a la página principal")
    frontend_status = "✅ Frontend encontrado" if os.path.exists("frontend") else "❌ Frontend no encontrado"
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RepletO v2.0 SIMPLE</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 40px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
            }}
            .link {{
                display: inline-block;
                margin: 20px;
                padding: 15px 30px;
                background: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 10px;
                font-size: 18px;
            }}
            .link:hover {{ background: #45a049; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 RepletO v2.0</h1>
            <h2>Servidor Simple Funcionando ✅</h2>
            <a href="/frontend/" class="link">🚀 Abrir Editor</a>
            <a href="/api/health" class="link">💚 Estado</a>
            <p>Frontend path: {frontend_status}</p>
        </div>
    </body>
    </html>
    """

@app.get("/api/health")
async def health():
    logger.info("Health check solicitado")
    return {"status": "healthy", "message": "RepletO v2.0 Simple funcionando"}

@app.get("/test")
async def test_execution():
    """Página de prueba rápida para verificar ejecución"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RepletO - Test de Ejecución</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #f0f8ff; }
            .container { max-width: 800px; margin: 0 auto; }
            button { padding: 10px 20px; margin: 10px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #45a049; }
            #output { background: #333; color: #0f0; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; margin-top: 20px; min-height: 200px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 RepletO v2.0 - Test de Ejecución</h1>
            <p>Prueba rápida para verificar que la ejecución funciona:</p>
            
            <button onclick="testBasico()">Prueba Básica</button>
            <button onclick="testCalculadora()">Calculadora</button>
            <button onclick="testMath()">Matemáticas</button>
            
            <div id="output">Presiona un botón para probar...</div>
        </div>
        
        <script>
        async function ejecutarCodigo(codigo) {
            const output = document.getElementById('output');
            output.textContent = 'Ejecutando...';
            
            try {
                const response = await fetch('/api/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: codigo })
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    output.textContent = `✅ ÉXITO:\\n\\nOUTPUT:\\n${result.output}`;
                } else {
                    output.textContent = `❌ ERROR:\\n\\nSTATUS: ${result.status}\\nOUTPUT: ${result.output || 'N/A'}\\nERROR: ${result.error || 'N/A'}`;
                }
            } catch (error) {
                output.textContent = `❌ ERROR DE CONEXIÓN:\\n\\n${error}`;
            }
        }
        
        function testBasico() {
            const codigo = `print("=== PRUEBA BASICA ===")
print("Hola RepletO v2.0!")
print("Python funcionando correctamente")
print("=== FIN PRUEBA ===")`;
            ejecutarCodigo(codigo);
        }
        
        function testCalculadora() {
            const codigo = `print("=== CALCULADORA REPLETO ===")
a = 15
b = 8
print(f"Suma: {a} + {b} = {a + b}")
print(f"Resta: {a} - {b} = {a - b}")
print(f"Multiplicacion: {a} * {b} = {a * b}")
print(f"Division: {a} / {b} = {a / b:.2f}")
print("=== CALCULOS COMPLETADOS ===")`;
            ejecutarCodigo(codigo);
        }
        
        function testMath() {
            const codigo = `import math
print("=== FUNCIONES MATEMATICAS ===")
print(f"Pi = {math.pi:.6f}")
print(f"e = {math.e:.6f}")
print(f"sin(pi/2) = {math.sin(math.pi/2)}")
print(f"sqrt(25) = {math.sqrt(25)}")
print("=== MATEMATICAS OK ===")`;
            ejecutarCodigo(codigo);
        }
        </script>
    </body>
    </html>
    """)

@app.get("/simple")
async def simple_editor():
    """Editor simple que definitivamente funciona"""
    with open("frontend/simple.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)

@app.post("/api/execute")
async def execute_code(request: dict):
    """Ejecutor básico de código"""
    logger.info(f"Ejecutando código: {request.get('code', '')[:50]}...")
    code = request.get("code", "")
    
    if not code.strip():
        return {
            "status": "error",
            "output": "",
            "error": "No hay código para ejecutar"
        }
    
    try:
        # Ejecución básica y SEGURA con Python del entorno virtual
        import subprocess
        import tempfile
        import sys
        import os
        
        # Usar Python del entorno virtual
        venv_python = os.path.join(os.getcwd(), '.venv', 'Scripts', 'python.exe')
        python_executable = venv_python if os.path.exists(venv_python) else sys.executable
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_path = f.name
        
        # Configurar entorno con UTF-8
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONPATH'] = os.getcwd()
        
        result = subprocess.run(
            [python_executable, temp_path],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            env=env
        )
        
        os.unlink(temp_path)
        
        if result.returncode == 0:
            return {
                "status": "success",
                "output": result.stdout,
                "error": None
            }
        else:
            return {
                "status": "error",
                "output": result.stdout,
                "error": result.stderr
            }
            
    except subprocess.TimeoutExpired:
        try: os.unlink(temp_path)
        except: pass
        return {
            "status": "error",
            "output": "",
            "error": "Tiempo de ejecución excedido (10s)"
        }
    except Exception as e:
        try: os.unlink(temp_path)
        except: pass
        return {
            "status": "error",
            "output": "",
            "error": f"Error: {str(e)}"
        }

# Montar frontend
frontend_path = "frontend"
if os.path.exists(frontend_path):
    logger.info(f"Montando frontend desde: {os.path.abspath(frontend_path)}")
    app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    logger.error(f"Frontend no encontrado en: {os.path.abspath(frontend_path)}")

# Función principal
if __name__ == "__main__":
    import uvicorn
    logger.info("🎨 RepletO v2.0 SIMPLE - Iniciando sin auto-reload...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)