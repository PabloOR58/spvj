

# Proyecto Videojuegos

Analísis de videojuegos para crear un videojuego óptimo para la sociedad.



# Estructura
    
    - src: código
    - data: ficheros crudos y trabajados
    - notebooks: ficheros de prueba 


# Instrucciones
    - Virtual env: python -m venv .venv
    - Activarlo: .venv\Scripts\activate
    - Librerías: pip install -r requirements.txt



# Integrantes
    - Sergi Armengol
    - Pablo Orellana Revenko
    - Victor Manuel Camacho Jerez
    - Jorge Sanchez Estudillo


# URL Juego

    -https://infosteam.streamlit.app/


# 
    -streamlit run web\app.py
    docker run --rm -p 8501:8501 mi-web-app
    docker ps -a --filter "publish=8501"



# Arquitectura en Docker

## Descripción
La aplicación utiliza una arquitectura de un solo contenedor Docker para simplicidad y facilidad de despliegue.

- **Contenedor principal**: Ejecuta la app Streamlit en Python 3.9-slim.
- **Imagen base**: `python:3.9-slim` de Docker Hub.
- **Puerto expuesto**: 8501.
- **Volúmenes**: Ninguno por ahora; los datos se manejan dentro del contenedor.
- **Ejecución**: Construye con `docker build -t spvj .` y ejecuta con `docker run -p 8501:8501 spvj`.

## Instalación de Docker Desktop
Descarga e instala Docker Desktop desde [docker.com](https://www.docker.com/products/docker-desktop). Asegúrate de que esté ejecutándose antes de construir imágenes.

## Futuras expansiones
Si se agrega una base de datos (ej. PostgreSQL), usar Docker Compose para múltiples contenedores con volúmenes compartidos.