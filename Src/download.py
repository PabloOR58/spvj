import requests
from datetime import datetime
import csv
import os
import time

# ----------------------------------------------------------
# UTILIDADES
# ----------------------------------------------------------
def ensure_header(path, headers):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)


def datos_ya_guardados(path, fecha_actual):
    if not os.path.exists(path):
        return False

    with open(path, "r", encoding="utf-8", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Fecha") == fecha_actual:
                return True
    return False


# ----------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ----------------------------------------------------------
def generar_listado():

    if not os.path.exists("Clean"):
        os.makedirs("Clean")

    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    path_listado = "Clean/listado_juegos.csv"

    ensure_header(path_listado, ["Fecha", "Posicion", "AppID", "Nombre", "JugadoresConcurrentes"])

    # Evitar duplicados
    if datos_ya_guardados(path_listado, fecha_actual):
        print(f"Ya existen datos para hoy ({fecha_actual}). No se duplican.")
        return

    print("Descargando datos de Steam...")

    try:
        url = "https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/"
        response = requests.get(url, timeout=10)
        data = response.json()
        juegos = data.get('response', {}).get('ranks', [])
    except Exception as e:
        print("Error al conectar con Steam:", e)
        return

    if not juegos:
        print("No se recibieron datos")
        return

    # Solo top 100
    juegos = juegos[:100]

    with open(path_listado, "a", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)

        for i, juego in enumerate(juegos, start=1):
            appid = juego.get('appid')
            jugadores = juego.get('concurrent_in_game', 0)

            # Obtener nombre del juego
            try:
                url_name = f"https://store.steampowered.com/api/appdetails?appids={appid}"
                res = requests.get(url_name, timeout=10).json()

                if res[str(appid)]["success"]:
                    nombre = res[str(appid)]['data']['name']
                else:
                    nombre = f"ID: {appid}"

                time.sleep(0.2)

            except:
                nombre = f"ID: {appid}"

            writer.writerow([fecha_actual, i, appid, nombre, jugadores])
            print(f"{i}/100 - {nombre}")

    print("\nDatos guardados correctamente (Top 100 del día)")


# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------
if __name__ == "__main__":
    generar_listado()