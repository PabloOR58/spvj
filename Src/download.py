import requests
from datetime import datetime
import csv
import os

def generar_listado():
    if not os.path.exists("Clean"):
        os.makedirs("Clean")
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    # 1️⃣ Top jugadores
    url_top = "https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/"
    respuesta = requests.get(url_top)
    datos = respuesta.json()
    juegos = datos.get('response', {}).get('ranks', [])

    if not juegos:
        print("No hay datos de jugadores concurrentes.")
        return

    # CSV Top jugadores
    with open("Clean/listado_juegos.csv", "w", encoding="utf-8", newline='') as fichero:
        writer = csv.writer(fichero)
        writer.writerow(["Fecha", "Posicion", "AppID", "Nombre", "JugadoresConcurrentes"])
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

    # 2️⃣ Info de juegos
    with open("Clean/info_juegos.csv", "w", encoding="utf-8", newline='') as fichero_info:
        writer_info = csv.writer(fichero_info)
        writer_info.writerow(["AppID", "Nombre", "Fecha_Lanzamiento", "Géneros", "Desarrollador"])
        for i, juego_data in enumerate(juegos):
            appid = juego_data.get('appid')

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

    # 3️⃣ Top sellers
    url_vendidos = "https://store.steampowered.com/api/featuredcategories"
    vendidos = requests.get(url_vendidos)
    datos_vendidos = vendidos.json()
    top_vendidos = datos_vendidos["top_sellers"]["items"]

    with open("Clean/Top_vendidos.csv", "w", encoding="utf-8", newline='') as fichero_vendidos:
        writer_vendidos = csv.writer(fichero_vendidos)
        writer_vendidos.writerow(["Nombre", "ID"])
        for juego in top_vendidos:
            nombre = juego.get("name")
            ID = juego.get("id")
            writer_vendidos.writerow([nombre, ID])
            print(f"OK Vendidos: {nombre}")

    print("\nProceso completado correctamente.")


if __name__ == "__main__":
    generar_listado()