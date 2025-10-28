# 🚀 RepletO

Entorno de ejecución de código en la nube similar a Replit.

## 📋 Descripción

RepletO es una plataforma web que permite ejecutar código Python de forma segura en un entorno sandbox controlado.

## 🛠️ Instalación

### Prerrequisitos
- Python 3.12+
- pip

### Pasos de instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/RepletO.git
cd RepletO
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

3. **Instalar dependencias:**
```bash
pip install -r backend/requirements.txt
```

## 🧪 Ejemplos de Uso

### � Usando el Frontend (Recomendado):
1. Abre http://localhost:3000 en tu navegador
2. El código de ejemplo se carga automáticamente
3. Presiona `Ctrl+Enter` para ejecutar
4. ¡Experimenta con tu propio código Python!

### 🔧 Usando el API directamente:

### Método 1: Desarrollo Completo (Frontend + Backend)

#### 1. **Iniciar el Backend:**
```bash
# Terminal 1 - Backend API
cd RepletO
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

#### 2. **Iniciar el Frontend:**
```bash
# Terminal 2 - Frontend Server
cd RepletO
python serve-frontend.py
```

#### 3. **Acceder a la aplicación:**
- **Frontend completo:** http://localhost:3000
- **API Backend:** http://127.0.0.1:8000
- **Documentación API:** http://127.0.0.1:8000/docs

### Método 2: Solo Backend (para testing API)

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: `http://localhost:8000`

## 📡 API Endpoints

### `GET /`
Información básica del servicio.

### `POST /run`
Ejecuta código Python.

**Request Body:**
```json
{
  "code": "print('Hola RepletO!')",
  "language": "python"
}
```

**Response:**
```json
{
  "status": "success",
  "output": "Hola RepletO!\n",
  "error": null
}
```

### `GET /health`
Verificación de salud del servidor.

## 🎨 Frontend Interactivo

### ✨ Características del Frontend:
- **🖥️ Editor Monaco:** Syntax highlighting para Python (mismo que VS Code)
- **🎯 Interfaz tipo Replit:** Layout de 2 paneles con diseño profesional
- **⚡ Ejecución en tiempo real:** Resultados instantáneos con timestamps
- **🎹 Atajos de teclado:** 
  - `Ctrl+Enter` / `Cmd+Enter` → Ejecutar código
  - `Ctrl+L` / `Cmd+L` → Limpiar output
- **📱 Responsive:** Funciona en desktop, tablet y móvil
- **🌙 Tema oscuro:** Optimizado para programación
- **🔄 Auto-scroll:** Output panel se actualiza automáticamente
- **💾 Auto-guardado:** El código se guarda automáticamente

### 🎮 Cómo usar:
1. Escribe código Python en el editor izquierdo
2. Presiona `Ctrl+Enter` o el botón "Ejecutar"
3. Ve los resultados en el panel derecho
4. Usa el botón "Limpiar" para resetear el output

### 🌐 URLs del Frontend:
- **Aplicación principal:** http://localhost:3000
- **Panel de desarrollo:** F12 para DevTools
- **Estado del servidor:** Indicador visual en tiempo real

### Con curl:
```bash
# Ejemplo básico
curl -X POST "http://localhost:8000/run" \
     -H "Content-Type: application/json" \
     -d '{"code": "print(\"Hola mundo\")"}'

# Ejemplo con cálculos
curl -X POST "http://localhost:8000/run" \
     -H "Content-Type: application/json" \
     -d '{"code": "result = 2 + 2\nprint(f\"2 + 2 = {result}\")"}'

# Ejemplo con bucles
curl -X POST "http://localhost:8000/run" \
     -H "Content-Type: application/json" \
     -d '{"code": "for i in range(5):\n    print(f\"Número: {i}\")"}'
```

### Con PowerShell (Windows):
```powershell
# Ejemplo básico
Invoke-RestMethod -Uri "http://localhost:8000/run" -Method Post -ContentType "application/json" -Body '{"code": "print(\"Hola desde PowerShell!\")"}'

# Ejemplo con variables
$body = @{
    code = "x = 10; y = 20; print(f'La suma es: {x + y}')"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/run" -Method Post -ContentType "application/json" -Body $body
```

## 🔒 Seguridad

- Ejecuta código en entorno sandbox
- Timeout de 5 segundos por ejecución
- Bloquea importaciones peligrosas (os, sys, subprocess, etc.)
- Entorno aislado sin acceso al sistema de archivos
- Captura tanto stdout como stderr

## 🏗️ Estructura del Proyecto

```
RepletO/
├── backend/
│   ├── main.py          # Servidor FastAPI
│   ├── sandbox.py       # Sistema de ejecución segura
│   ├── requirements.txt # Dependencias Python
│   └── __init__.py
├── frontend/            # 🆕 Interface web interactiva
│   ├── index.html       # Página principal
│   ├── css/
│   │   ├── styles.css   # Estilos principales
│   │   └── editor.css   # Estilos del Monaco Editor
│   ├── js/
│   │   ├── main.js      # Lógica principal de la app
│   │   ├── api.js       # Cliente API para backend
│   │   ├── editor.js    # Configuración Monaco Editor
│   │   └── resizer.js   # Manejo de paneles (futuro)
│   └── assets/          # Recursos estáticos
├── serve-frontend.py    # 🆕 Servidor HTTP para frontend
├── .gitignore
├── README.md
└── docker-compose.yml   # Configuración Docker (próximamente)
```

## 🎯 Roadmap

- [x] Backend FastAPI básico
- [x] Sistema sandbox seguro
- [x] Endpoint /run funcional
- [x] Validación de código malicioso
- [x] **🆕 Frontend web interactivo**
- [x] **🆕 Editor Monaco con syntax highlighting**
- [x] **🆕 Interfaz tipo VSCode/Replit**
- [x] **🆕 Atajos de teclado y responsive design**
- [ ] Soporte para múltiples lenguajes (JavaScript, Node.js)
- [ ] Sistema de autenticación y usuarios
- [ ] Persistencia de proyectos y archivos
- [ ] Colaboración en tiempo real
- [ ] Integración con GitHub
- [ ] Containerización con Docker
- [ ] Deploy en la nube

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 🔥 Quick Start

```bash
# 🚀 Setup completo (una sola vez)
git clone https://github.com/Sickboooooy/RepletO.git
cd RepletO
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r backend/requirements.txt

# ⚡ Ejecutar (2 terminales)
# Terminal 1 - Backend:
uvicorn backend.main:app --reload

# Terminal 2 - Frontend:
python serve-frontend.py

# 🌐 Abrir navegador:
# http://localhost:3000
```

## 🎮 Demo en Vivo

![RepletO Screenshot](https://via.placeholder.com/800x400/1e1e1e/4CAF50?text=RepletO%20-%20Editor%20Python%20Online)

### 🔥 Características destacadas:
- ⚡ **Ejecución instantánea** de código Python
- 🎨 **Editor profesional** con syntax highlighting
- 🛡️ **Sandbox seguro** con timeout automático
- 📱 **Responsive design** para todos los dispositivos
- ⌨️ **Atajos de teclado** como en VS Code
- 🌙 **Tema oscuro** optimizado para programación

¡Listo para programar en la nube! 🚀