# 🚀 RepletO v2.0 - Multi-stage Docker Build
# ================================================

# 🔨 Builder stage - Compilar dependencias
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependencias del sistema para build
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 🎯 Runtime stage - Imagen final optimizada
FROM python:3.11-slim

# Metadatos
LABEL maintainer="RepletO Team"
LABEL version="2.0"
LABEL description="RepletO - IDE Web Híbrido Autoalojado"

# Variables de entorno
ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000
ENV UVICORN_WORKERS=1

# Crear usuario no-root para seguridad
RUN groupadd -r repleto && useradd -r -g repleto repleto

# Instalar dependencias del sistema runtime
RUN apt-get update && apt-get install -y \
    git \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Crear directorios de trabajo
WORKDIR /app
RUN mkdir -p /app/data /app/logs /app/temp && \
    chown -R repleto:repleto /app

# Copiar dependencias Python desde builder
COPY --from=builder /root/.local /home/repleto/.local
ENV PATH=/home/repleto/.local/bin:$PATH

# Copiar código de la aplicación
COPY --chown=repleto:repleto backend/ ./backend/
COPY --chown=repleto:repleto frontend/ ./frontend/
COPY --chown=repleto:repleto serve-frontend.py ./
COPY --chown=repleto:repleto README.md ./

# Cambiar a usuario no-root
USER repleto

# Exponer puertos
EXPOSE 8000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 🚀 Comando por defecto
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]