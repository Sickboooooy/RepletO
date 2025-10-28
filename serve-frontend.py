#!/usr/bin/env python3
"""
RepletO Frontend Server
Servidor HTTP simple para servir el frontend en el puerto 3000
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

# Configuración del servidor
PORT = 3000
HOST = "127.0.0.1"
FRONTEND_DIR = "frontend"

class RepletOHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler personalizado para el servidor RepletO"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)
    
    def end_headers(self):
        # Agregar headers de seguridad y CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Manejar preflight requests de CORS
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        # Personalizar logs del servidor
        timestamp = self.log_date_time_string()
        print(f"[{timestamp}] {format % args}")

def check_frontend_directory():
    """Verifica que el directorio frontend existe y tiene los archivos necesarios"""
    frontend_path = Path(FRONTEND_DIR)
    
    if not frontend_path.exists():
        print(f"❌ Error: El directorio '{FRONTEND_DIR}' no existe")
        print(f"   Asegúrate de ejecutar este script desde el directorio raíz del proyecto")
        return False
    
    index_file = frontend_path / "index.html"
    if not index_file.exists():
        print(f"❌ Error: No se encuentra 'index.html' en '{FRONTEND_DIR}'")
        return False
    
    # Verificar archivos importantes
    important_files = [
        "css/styles.css",
        "js/main.js",
        "js/api.js",
        "js/editor.js"
    ]
    
    missing_files = []
    for file in important_files:
        if not (frontend_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Advertencia: Faltan algunos archivos:")
        for file in missing_files:
            print(f"   - {file}")
        print("   El frontend puede no funcionar correctamente")
    
    return True

def start_server():
    """Inicia el servidor HTTP para el frontend"""
    
    # Verificar directorio frontend
    if not check_frontend_directory():
        sys.exit(1)
    
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    try:
        # Crear servidor
        with socketserver.TCPServer((HOST, PORT), RepletOHTTPRequestHandler) as httpd:
            server_url = f"http://{HOST}:{PORT}"
            
            print("🚀 RepletO Frontend Server")
            print("=" * 50)
            print(f"📁 Sirviendo: {Path(FRONTEND_DIR).absolute()}")
            print(f"🌐 URL: {server_url}")
            print(f"📡 Backend: http://127.0.0.1:8000")
            print("=" * 50)
            print("💡 Consejos:")
            print("   • Asegúrate de que el backend esté corriendo en el puerto 8000")
            print("   • Usa Ctrl+C para detener el servidor")
            print("   • El navegador debería abrirse automáticamente")
            print("=" * 50)
            
            # Intentar abrir el navegador automáticamente
            try:
                print(f"🌐 Abriendo navegador en {server_url}...")
                webbrowser.open(server_url)
            except Exception as e:
                print(f"⚠️  No se pudo abrir el navegador automáticamente: {e}")
                print(f"   Abre manualmente: {server_url}")
            
            print(f"\n🎯 Servidor iniciado. Presiona Ctrl+C para detener...")
            
            # Iniciar servidor
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
        print("👋 ¡Gracias por usar RepletO!")
        
    except PermissionError:
        print(f"❌ Error: No se puede usar el puerto {PORT}")
        print("   Prueba con un puerto diferente o ejecuta como administrador")
        sys.exit(1)
        
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Error: El puerto {PORT} ya está en uso")
            print("   Detén el otro servidor o usa un puerto diferente")
        else:
            print(f"❌ Error del sistema operativo: {e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

def main():
    """Función principal"""
    print("🔧 Iniciando RepletO Frontend Server...")
    
    # Verificar versión de Python
    if sys.version_info < (3, 6):
        print("❌ Error: Se requiere Python 3.6 o superior")
        sys.exit(1)
    
    # Mostrar información del sistema
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📂 Directorio: {os.getcwd()}")
    
    # Iniciar servidor
    start_server()

if __name__ == "__main__":
    main()