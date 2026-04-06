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
    # LISTADO JUEGOS
    # ----------------------------------------------------------------------------------------------------------------------
    path_listado = "Clean/listado_juegos.csv"
    ensure_header(path_listado, ["Fecha", "Posicion", "AppID", "Nombre", "JugadoresConcurrentes"])

    if not datos_ya_guardados(path_listado, fecha_actual):
        url_top = "https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/"
        juegos = requests.get(url_top).json().get('response', {}).get('ranks', [])

        with open(path_listado, "a", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)

            for i, juego in enumerate(juegos):
                appid = juego.get('appid')
                jugadores = juego.get('concurrent_in_game', 0)

                try:
                    data = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}").json()
                    nombre = data[str(appid)]['data']['name']
                except:
                    nombre = f"ID: {appid}"

                writer.writerow([fecha_actual, i+1, appid, nombre, jugadores])
                print(f"OK Top: {nombre}")

    # ----------------------------------------------------------------------------------------------------------------------
    # INFO JUEGOS
    # ----------------------------------------------------------------------------------------------------------------------
    info_path = "Clean/info_juegos.csv"
    ensure_header(info_path, ["AppID", "Nombre", "Fecha_Lanzamiento", "Géneros", "Desarrollador"])

    existing_ids = set()
    if os.path.exists(info_path):
        with open(info_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_ids.add(row["AppID"])

    with open(info_path, "a", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)

        url_top = "https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/"
        juegos = requests.get(url_top).json().get('response', {}).get('ranks', [])

        for juego in juegos:
            appid = str(juego.get('appid'))

            if appid in existing_ids:
                continue

            try:
                data = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}").json()
                data = data[str(appid)]['data']

                nombre = data.get('name')
                fecha = data['release_date']['date']
                generos = ", ".join([g['description'] for g in data.get('genres', [])])
                dev = ", ".join(data.get('developers', []))
            except:
                nombre = f"ID: {appid}"
                fecha = "Desconocida"
                generos = ""
                dev = ""

            writer.writerow([appid, nombre, fecha, generos, dev])
            print(f"OK Info: {nombre}")

    # ----------------------------------------------------------------------------------------------------------------------
    # TOP VENDIDOS
    # ----------------------------------------------------------------------------------------------------------------------
    vendidos_path = "Clean/Top_vendidos.csv"
    ensure_header(vendidos_path, ["Fecha", "Nombre", "ID"])

    if not datos_ya_guardados(vendidos_path, fecha_actual):
        vendidos = requests.get("https://store.steampowered.com/api/featuredcategories").json()
        top = vendidos["top_sellers"]["items"]

        with open(vendidos_path, "a", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            for j in top:
                writer.writerow([fecha_actual, j.get("name"), j.get("id")])
                print(f"OK Vendidos: {j.get('name')}")

    # ----------------------------------------------------------------------------------------------------------------------
    # 🔥 DETALLES AVANZADOS
    # ----------------------------------------------------------------------------------------------------------------------
    detalles_path = "Clean/detalles_juegos.csv"
    ensure_header(detalles_path, [
        "AppID", "Nombre", "Precio", "Rating", "Reviews",
        "Generos", "Desarrollador", "Publisher",
        "Plataformas", "Edad", "Categorias"
    ])

    existing_ids = set()
    if os.path.exists(detalles_path):
        with open(detalles_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_ids.add(row["AppID"])

    with open(detalles_path, "a", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)

        url_top = "https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/"
        juegos = requests.get(url_top).json().get('response', {}).get('ranks', [])

        for juego in juegos:
            appid = str(juego.get('appid'))

            if appid in existing_ids:
                continue

            try:
                data = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}").json()
                data = data[str(appid)]['data']

                nombre = data.get("name")

                precio = "Gratis" if data.get("is_free") else data.get("price_overview", {}).get("final_formatted", "N/A")
                rating = data.get("metacritic", {}).get("score", "N/A")
                reviews = data.get("recommendations", {}).get("total", "N/A")

                generos = ", ".join([g['description'] for g in data.get('genres', [])])
                dev = ", ".join(data.get("developers", []))
                pub = ", ".join(data.get("publishers", []))

                plataformas = ", ".join([k for k, v in data.get("platforms", {}).items() if v])
                edad = data.get("required_age", "0")
                categorias = ", ".join([c['description'] for c in data.get("categories", [])])

            except:
                nombre = f"ID: {appid}"
                precio = rating = reviews = "N/A"
                generos = dev = pub = ""
                plataformas = categorias = ""
                edad = "0"

            writer.writerow([
                appid, nombre, precio, rating, reviews,
                generos, dev, pub, plataformas, edad, categorias
            ])

            print(f"OK Detalles: {nombre}")

    print("\nProceso completado correctamente.")
if __name__ == "__main__":
    generar_listado()