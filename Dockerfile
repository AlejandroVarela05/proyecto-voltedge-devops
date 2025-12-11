# Usa imagen oficial de Python 3.12 slim (ligera)
FROM python:3.12-slim

# Metadata
LABEL maintainer="alejandro.varela.01@uie.edu"
LABEL description="VoltEdge - EV Charging Station Management API"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear directorio de trabajo
WORKDIR /app

# Copiar solo requirements.txt primero (cache layer)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY models/ ./models/
COPY services/ ./services/
COPY schemas/ ./schemas/
COPY main.py main_demo.py ./

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 voltedge && \
    chown -R voltedge:voltedge /app

# Cambiar al usuario no-root
USER voltedge

# Exponer puerto de la API
EXPOSE 8000

<<<<<<< Updated upstream
# Health check (opcional pero profesional)
=======
# Health check
>>>>>>> Stashed changes
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

# Comando por defecto: ejecutar la API con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
