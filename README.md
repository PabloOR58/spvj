

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

# Arquitectura Docker (Entrega 11/05)
    - Tipo: Contenedor único (Single-container)
    - Abstracción: Entorno aislado con Python 3.9-slim
    - Puertos: Mapeo de puerto 8501:8501

# Comandos Docker
    - Build: docker build -t mi-web-app .
    - Run: docker run -p 8501:8501 mi-web-app
    - Status: docker ps -a --filter "publish=8501"