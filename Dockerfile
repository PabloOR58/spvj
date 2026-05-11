FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN ls -la /app

EXPOSE 8501
   
# Comando para ejecutar la app con Streamlit
CMD ["streamlit", "run", "Web/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]