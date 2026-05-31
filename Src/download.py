import requests #Importa la biblioteca requests para realizar solicitudes HTTP a la API de Steam y obtener datos sobre los juegos, como su nombre, plataformas y número de jugadores concurrentes. Esto es esencial para recopilar la información necesaria para generar los archivos CSV con los datos de los juegos más jugados y vendidos en Steam.
from datetime import datetime #Importa la clase datetime del módulo datetime para trabajar con fechas y horas. En este código, se utiliza para obtener la fecha actual en formato "YYYY-MM-DD" para registrar cuándo se recopilaron los datos de los juegos y para eliminar entradas anteriores de los archivos CSV que correspondan a la misma fecha, asegurando que los datos estén actualizados y organizados por fecha.
import csv #Importa el módulo csv para trabajar con archivos CSV (Comma-Separated Values). Este módulo proporciona funciones para leer y escribir archivos CSV de manera sencilla. En este código, se utiliza para crear archivos CSV con encabezados específicos, eliminar filas basadas en la fecha y escribir los datos recopilados sobre los juegos en los archivos CSV correspondientes.                                                                                                   
import os #Importa el módulo os para interactuar con el sistema operativo, como crear directorios y manejar rutas de archivos. En este código, se utiliza para determinar la ruta base del proyecto, crear un directorio "Clean" si no existe y construir las rutas completas para los archivos CSV donde se almacenarán los datos de los juegos. Esto ayuda a organizar los archivos de salida y asegurarse de que se guarden en la ubicación correcta dentro del proyecto.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #Determina la ruta base del proyecto al obtener el directorio del archivo actual (download.py) y luego subir un nivel para llegar al directorio raíz del proyecto. Esto es útil para construir rutas relativas a partir de la ubicación del proyecto, lo que facilita la gestión de archivos y directorios dentro del proyecto sin depender de rutas absolutas que pueden variar entre diferentes entornos o sistemas.
CLEAN_DIR = os.path.join(BASE_DIR, "Clean") #Construye la ruta completa para el directorio "Clean" dentro del proyecto utilizando la ruta base determinada anteriormente. Este directorio se utilizará para almacenar los archivos CSV generados con los datos de los juegos, manteniendo los archivos organizados y separados de otros archivos del proyecto.


def crear_csv(path, headers): #Crea un archivo CSV en la ruta especificada con los encabezados proporcionados si el archivo no existe. Si el archivo ya existe, no realiza ninguna acción. Esto es útil para asegurarse de que los archivos CSV necesarios para almacenar los datos de los juegos estén presentes y tengan la estructura correcta antes de escribir los datos en ellos.
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)


def eliminar_fecha(path, fecha):
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        filas = list(reader)

    if not reader.fieldnames or "Fecha" not in reader.fieldnames:
        return

    filas = [r for r in filas if r.get("Fecha") != fecha]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(filas)


def get_platforms(appid): #Obtiene las plataformas disponibles para un juego específico utilizando su appid. Realiza una solicitud a la API de Steam para obtener los detalles del juego y extrae la información de las plataformas (Windows, Mac, Linux) en las que el juego está disponible. Devuelve una cadena con las plataformas separadas por comas o "windows" como valor predeterminado si no se pueden obtener los datos de la API o si no se encuentran plataformas específicas.
    try:
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        data = requests.get(url, timeout=10).json()
        info = data[str(appid)]["data"]

        p = info.get("platforms", {})

        platforms = []
        if p.get("windows"):
            platforms.append("windows")
        if p.get("mac"):
            platforms.append("mac")
        if p.get("linux"):
            platforms.append("linux")

        return ",".join(platforms) if platforms else "windows"

    except:
        return "windows"


def generar_datos(): #Genera los datos de los juegos más jugados y vendidos en Steam, y los guarda en archivos CSV organizados por fecha. Primero, crea los archivos CSV necesarios con los encabezados adecuados si no existen. Luego, elimina las entradas anteriores correspondientes a la fecha actual para evitar duplicados. A continuación, realiza solicitudes a la API de Steam para obtener información sobre los juegos más jugados y vendidos, y escribe estos datos en los archivos CSV correspondientes. Finalmente, imprime un mensaje indicando que el proceso ha terminado.

    os.makedirs(CLEAN_DIR, exist_ok=True)
    fecha = datetime.now().strftime("%Y-%m-%d")


    path_jugados = os.path.join(CLEAN_DIR, "listado_juegos.csv")
    path_plataformas = os.path.join(CLEAN_DIR, "plataformas_juegos.csv")

    crear_csv(path_jugados, [
        "Fecha",
        "Posicion",
        "AppID",
        "Nombre",
        "JugadoresConcurrentes"
    ])

    crear_csv(path_plataformas, [
        "Fecha",
        "AppID",
        "Plataformas"
    ])

    eliminar_fecha(path_jugados, fecha)
    eliminar_fecha(path_plataformas, fecha)

    url = "https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/"
    try: #Realiza una solicitud a la API de Steam para obtener la lista de juegos ordenados por número de jugadores concurrentes. Si la solicitud es exitosa, se extrae la información relevante (appid, nombre y número de jugadores concurrentes) para cada juego. Si ocurre algún error durante la solicitud o el procesamiento de los datos, se maneja la excepción y se asigna una lista vacía a la variable "juegos", lo que permite que el programa continúe sin interrupciones incluso si no se pueden obtener los datos de la API.
        juegos = requests.get(url, timeout=10).json().get("response", {}).get("ranks", [])
    except Exception:
        juegos = []

    with open(path_jugados, "a", newline="", encoding="utf-8") as f1, \
         open(path_plataformas, "a", newline="", encoding="utf-8") as f2:

        writer1 = csv.writer(f1) #Crea objetos writer para escribir en los archivos CSV correspondientes. "writer1" se utiliza para escribir los datos de los juegos más jugados en el archivo "listado_juegos.csv", mientras que "writer2" se utiliza para escribir la información de las plataformas disponibles para cada juego en el archivo "plataformas_juegos.csv". Estos objetos writer facilitan la escritura de filas de datos en los archivos CSV de manera estructurada y organizada.
        writer2 = csv.writer(f2)

        for i, juego in enumerate(juegos[:100]):
            appid = juego.get("appid")
            players = juego.get("concurrent_in_game", 0)

            try:
                data = requests.get(
                    f"https://store.steampowered.com/api/appdetails?appids={appid}"
                ).json()
                nombre = data[str(appid)]["data"]["name"]
            except:
                nombre = f"ID {appid}"

            plataformas = get_platforms(appid)

            # CSV ranking
            writer1.writerow([
                fecha,
                i + 1,
                appid,
                nombre,
                players
            ])

            # CSV plataformas (SEPARADO)
            writer2.writerow([
                fecha,
                appid,
                plataformas
            ])

            print("OK:", nombre)


    path_vendidos = os.path.join(CLEAN_DIR, "top_vendidos.csv")

    crear_csv(path_vendidos, ["Fecha", "Posicion", "ID", "Nombre"])
    eliminar_fecha(path_vendidos, fecha)

    url = "https://store.steampowered.com/api/featuredcategories"
    try:
        data = requests.get(url, timeout=10).json()
        top = data.get("top_sellers", {}).get("items", [])
    except Exception:
        top = []

    with open(path_vendidos, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for i, juego in enumerate(top[:100]):
            writer.writerow([
                fecha,
                i + 1,
                juego.get("id", ""),
                juego.get("name", "Desconocido")
            ])

    print("Proceso terminado")


if __name__ == "__main__":
    generar_datos()