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

## 🚀 Ejecución

### Iniciar el servidor de desarrollo:
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

## 🧪 Ejemplos de Uso

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
├── frontend/            # Interface web (próximamente)
│   ├── js/
│   └── css/
├── .gitignore
├── README.md
└── docker-compose.yml   # Configuración Docker (próximamente)
```

## 🎯 Roadmap

- [x] Backend FastAPI básico
- [x] Sistema sandbox seguro
- [x] Endpoint /run funcional
- [x] Validación de código malicioso
- [ ] Frontend web interactivo
- [ ] Soporte para múltiples lenguajes
- [ ] Sistema de autenticación
- [ ] Persistencia de proyectos
- [ ] Colaboración en tiempo real

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
# Clonar e instalar
git clone https://github.com/tu-usuario/RepletO.git
cd RepletO
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r backend/requirements.txt

# Ejecutar
uvicorn backend.main:app --reload

# Probar
curl -X POST "http://localhost:8000/run" -H "Content-Type: application/json" -d '{"code": "print(\"RepletO funcionando!\")"}'
```

¡Listo para programar en la nube! 🚀