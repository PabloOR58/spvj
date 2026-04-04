import requests
from datetime import datetime
import csv
import os

def ensure_header(path, headers):
    """Crea un CSV con cabecera si no existe"""
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)


def datos_ya_guardados(path, fecha_actual, columna_fecha="Fecha"):
    """Devuelve True si ya existen datos para la fecha indicada"""
    if not os.path.exists(path):
        return False
    with open(path, "r", encoding="utf-8", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get(columna_fecha) == fecha_actual:
                return True
    return False


def generar_listado():
    """Descarga datos de Steam y los guarda en CSV, sin duplicar datos del mismo día"""

    # Carpeta Clean
    if not os.path.exists("Clean"):
        os.makedirs("Clean")

    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    # ----------------------------------------------------------------------------------------------------------------------
    #  Listado de juegos por jugadores concurrentes
    # ----------------------------------------------------------------------------------------------------------------------
    path_listado = "Clean/listado_juegos.csv"
    ensure_header(path_listado, ["Fecha", "Posicion", "AppID", "Nombre", "JugadoresConcurrentes"])

    # Evitar duplicados por fecha
    if datos_ya_guardados(path_listado, fecha_actual):
        print(f"Ya existen datos para {fecha_actual} en listado_juegos.csv. Saltando esta sección.")
    else:
        url_top = "https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/"
        respuesta = requests.get(url_top)
        datos = respuesta.json()
        juegos = datos.get('response', {}).get('ranks', [])

        if not juegos:
            print("No hay datos de jugadores concurrentes.")
            return

        with open(path_listado, "a", encoding="utf-8", newline='') as fichero:
            writer = csv.writer(fichero)
            for i, juego_data in enumerate(juegos):
                appid = juego_data.get('appid')
                jugadores = juego_data.get('concurrent_in_game', 0)

                # Obtener nombre
                try:
                    res_n = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}").json()
                    nombre = res_n[str(appid)]['data']['name']
                except:
                    nombre = f"ID: {appid}"

                writer.writerow([fecha_actual, i+1, appid, nombre, jugadores])
                print(f"OK Top: {nombre}")

    # ----------------------------------------------------------------------------------------------------------------------
    #  Información general de juegos
    # ----------------------------------------------------------------------------------------------------------------------
    info_path = "Clean/info_juegos.csv"
    ensure_header(info_path, ["AppID", "Nombre", "Fecha_Lanzamiento", "Géneros", "Desarrollador"])

    existing_appids = set()
    if os.path.exists(info_path):
        with open(info_path, "r", encoding="utf-8", newline='') as fcheck:
            reader_check = csv.DictReader(fcheck)
            for row in reader_check:
                if row.get("AppID"):
                    existing_appids.add(row["AppID"])

    with open(info_path, "a", encoding="utf-8", newline='') as fichero_info:
        writer_info = csv.writer(fichero_info)
        url_top = "https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/"
        juegos = requests.get(url_top).json().get('response', {}).get('ranks', [])

        for juego_data in juegos:
            appid = str(juego_data.get('appid'))
            if appid in existing_appids:
                continue

            try:
                res_n = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}").json()
                data = res_n[str(appid)]['data']
                nombre = data['name']
                fecha_lanzamiento = data['release_date']['date']
                generos = ", ".join([g['description'] for g in data.get('genres', [])])
                desarrollador = ", ".join(data.get('developers', []))
            except:
                nombre = f"ID: {appid}"
                fecha_lanzamiento = "Desconocida"
                generos = ""
                desarrollador = ""

            writer_info.writerow([appid, nombre, fecha_lanzamiento, generos, desarrollador])
            print(f"OK Info: {nombre}")

    # ----------------------------------------------------------------------------------------------------------------------
    # Top vendidos
    # ----------------------------------------------------------------------------------------------------------------------
    vendidos_path = "Clean/Top_vendidos.csv"
    ensure_header(vendidos_path, ["Fecha", "Nombre", "ID"])

    if datos_ya_guardados(vendidos_path, fecha_actual):
        print(f"Ya existen datos para {fecha_actual} en Top_vendidos.csv. Saltando esta sección.")
    else:
        url_vendidos = "https://store.steampowered.com/api/featuredcategories"
        vendidos = requests.get(url_vendidos).json()
        top_vendidos = vendidos["top_sellers"]["items"]

        with open(vendidos_path, "a", encoding="utf-8", newline='') as fichero_vendidos:
            writer_vendidos = csv.writer(fichero_vendidos)
            for juego in top_vendidos:
                nombre = juego.get("name")
                ID = juego.get("id")
                writer_vendidos.writerow([fecha_actual, nombre, ID])
                print(f"OK Vendidos: {nombre}")

    print("\n Proceso completado correctamente.")


if __name__ == "__main__":
    generar_listado()