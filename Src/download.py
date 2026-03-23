import requests
from datetime import datetime
import csv
import os

def generar_listado():
    if not os.path.exists("Clean"):
        os.makedirs("Clean")
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    def ensure_header(path, headers):
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)

    url_top = "https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/"
    respuesta = requests.get(url_top)
    datos = respuesta.json()
    juegos = datos.get('response', {}).get('ranks', [])

    if not juegos:
        print("No hay datos de jugadores concurrentes.")
        return

    ensure_header("Clean/listado_juegos.csv", ["Fecha", "Posicion", "AppID", "Nombre", "JugadoresConcurrentes"])

    with open("Clean/listado_juegos.csv", "a", encoding="utf-8", newline='') as fichero:
        writer = csv.writer(fichero)
        for i, juego_data in enumerate(juegos):
            appid = juego_data.get('appid')
            jugadores = juego_data.get('concurrent_in_game', 0)

            url_n = f"https://store.steampowered.com/api/appdetails?appids={appid}"
            try:
                res_n = requests.get(url_n).json()
                nombre = res_n[str(appid)]['data']['name']
            except:
                nombre = f"ID: {appid}"

            writer.writerow([fecha_actual, i+1, appid, nombre, jugadores])
            print(f"OK Top: {nombre}")

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
        for i, juego_data in enumerate(juegos):
            appid = str(juego_data.get('appid'))
            if appid in existing_appids:
                continue

            url_n = f"https://store.steampowered.com/api/appdetails?appids={appid}"
            try:
                res_n = requests.get(url_n).json()
                nombre = res_n[str(appid)]['data']['name']
                fecha_lanzamiento = res_n[str(appid)]['data']['release_date']['date']
                generos = ", ".join([g['description'] for g in res_n[str(appid)]['data'].get('genres', [])])
                desarrollador = ", ".join(res_n[str(appid)]['data'].get('developers', []))
            except:
                nombre = f"ID: {appid}"
                fecha_lanzamiento = "Desconocida"
                generos = ""
                desarrollador = ""

            writer_info.writerow([appid, nombre, fecha_lanzamiento, generos, desarrollador])
            print(f"OK Info: {nombre}")

    url_vendidos = "https://store.steampowered.com/api/featuredcategories"
    vendidos = requests.get(url_vendidos)
    datos_vendidos = vendidos.json()
    top_vendidos = datos_vendidos["top_sellers"]["items"]

    vendidos_path = "Clean/Top_vendidos.csv"
    ensure_header(vendidos_path, ["Fecha", "Nombre", "ID"])

    with open(vendidos_path, "a", encoding="utf-8", newline='') as fichero_vendidos:
        writer_vendidos = csv.writer(fichero_vendidos)
        for juego in top_vendidos:
            nombre = juego.get("name")
            ID = juego.get("id")
            writer_vendidos.writerow([fecha_actual, nombre, ID])
            print(f"OK Vendidos: {nombre}")

    print("\nProceso completado correctamente.")


if __name__ == "__main__":
    generar_listado()