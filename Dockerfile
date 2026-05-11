# Usamos una imagen ligera de Python
FROM python:3.11-slim

# Instalamos dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos los requisitos e instalamos (ajusta el nombre si es requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del proyecto
COPY . .

# Exponemos el puerto de Streamlit
EXPOSE 8501