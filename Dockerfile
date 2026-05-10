FROM python:3.9-slim

# [span_1](start_span)Directorio de trabajo dentro del contenedor[span_1](end_span)
WORKDIR /app

# [span_2](start_span)Instalamos dependencias[span_2](end_span)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# [span_3](start_span)Copiamos todo el contenido de la carpeta actual[span_3](end_span)
COPY . .

# EXTREMADAMENTE IMPORTANTE: 
# Verificamos qué archivos se han copiado durante el build
RUN ls -la /app

# Exponemos el puerto que usas
EXPOSE 8501

# Comando para ejecutar la app con Streamlit
CMD ["streamlit", "run", "Web/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]