
# Proyecto Videojuegos

Analísis de videojuegos para encontrar el juego adecuado para cada usuario.

# Estructura
    - src: código
    - data: ficheros crudos y trabajados
    - notebooks: ficheros de prueba 


# Cómo ejecutar el proyecto

Tienes **dos opciones** para ejecutar esta aplicación. 

## Opción 1: Sin Docker 

La forma más simple de ejecutar el código en tu computadora.

### Requisitos previos:
- **Python 3.9+** instalado en tu sistema

### Pasos:

1. **Clona o descarga el proyecto**
   ```bash
   cd /ruta/del/proyecto
   ```

2. **Crea un entorno virtual** (aislado, sin afectar tu sistema)
   ```bash
   python -m venv .venv
   ```

3. **Activa el entorno virtual:**
   - **En macOS/Linux:**
     ```bash
     source .venv/bin/activate
     ```
   - **En Windows (PowerShell):**
     ```bash
     .venv\Scripts\Activate.ps1
     ```
   - **En Windows (CMD):**
     ```bash
     .venv\Scripts\activate
     ```

4. **Instala las librerías necesarias**
   ```bash
   pip install -r requirements.txt
   ```

5. **Ejecuta la aplicación Streamlit**
   ```bash
   streamlit run web/app.py
   ```

   La app se abrirá en tu navegador en `http://localhost:8501`

6. **Para desactivar el entorno virtual cuando termines:**
   ```bash
   deactivate
   ```

---

## Opción 2: Con Docker 

Ejecuta la aplicación en un contenedor aislado. No necesitas instalar Python.

### Requisitos previos:
- **Docker Desktop** instalado en tu sistema (descarga desde https://www.docker.com/products/docker-desktop)

### Pasos:

1. **Clona o descarga el proyecto**
   ```bash
   cd /ruta/del/proyecto
   ```

2. **Construye la imagen Docker**
   ```bash
   docker build -t spvj .
   ```

3. **Ejecuta el contenedor**
   docker compose up --build.
   La app se abrirá en tu navegador en `http://localhost:8501`

4. **Para detener el contenedor**, presiona `Ctrl+C` en la terminal.

---

## Solución de problemas

- **Puerto 8501 ya en uso**: Ejecuta en otro puerto:
  ```bash
  streamlit run web/app.py --server.port 8502
  ```
  O en Docker: `docker run --rm -p 8502:8501 spvj`

- **Python no reconocido**: Instala Python desde https://www.python.org/

- **Docker no reconocido**: Asegúrate de que Docker Desktop está ejecutándose.

- **No module Named Streamlit** : En caso de que aparezca este error, asegurar de que se esta trabajando en el entorno virtual correcto. Cmd+shift+p 

# URL Juego Online

- https://infosteam.streamlit.app/

