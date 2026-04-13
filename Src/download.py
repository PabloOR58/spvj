import requests
from datetime import datetime
import csv
import os

# ========================================
# CREAR CSV SI NO EXISTE
# ========================================
def crear_csv(path, headers):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

# ========================================
# ELIMINAR DATOS DE HOY (PARA ACTUALIZAR)
# ========================================
def eliminar_fecha(path, fecha):
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        filas = list(reader)

    # Si el CSV está mal, no hacer nada
    if reader.fieldnames is None or "Fecha" not in reader.fieldnames:
        return

    filas_filtradas = [row for row in filas if row.get("Fecha") != fecha]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(filas_filtradas)

# ========================================
# FUNCIÓN PRINCIPAL
# ========================================
def generar_datos():

    if not os.path.exists("Clean"):
        os.makedirs("Clean")

    fecha = datetime.now().strftime("%Y-%m-%d")

    # ======================================================
    # TOP JUGADOS
    # ======================================================
    path_jugados = "Clean/listado_juegos.csv"

    crear_csv(path_jugados, ["Fecha", "Posicion", "AppID", "Nombre", "JugadoresConcurrentes"])

    # elimina datos de hoy si existen
    eliminar_fecha(path_jugados, fecha)

    url = "https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/"
    juegos = requests.get(url).json().get("response", {}).get("ranks", [])

    with open(path_jugados, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for i, juego in enumerate(juegos[:100]):
            appid = juego.get("appid")
            players = juego.get("concurrent_in_game", 0)

            try:
                data = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}").json()
                nombre = data[str(appid)]["data"]["name"]
            except:
                nombre = f"ID {appid}"

            writer.writerow([fecha, i+1, appid, nombre, players])
            print("OK Jugado:", nombre)

    # ======================================================
    # TOP VENDIDOS
    # ======================================================
    path_vendidos = "Clean/top_vendidos.csv"

    crear_csv(path_vendidos, ["Fecha", "Posicion", "ID", "Nombre"])

    # elimina datos de hoy si existen
    eliminar_fecha(path_vendidos, fecha)

    url = "https://store.steampowered.com/api/featuredcategories"
    data = requests.get(url).json()

    top = data.get("top_sellers", {}).get("items", [])

    with open(path_vendidos, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for i, juego in enumerate(top[:100]):
            nombre = juego.get("name", "Desconocido")
            appid = juego.get("id", "")

            writer.writerow([fecha, i+1, appid, nombre])
            print("OK Vendido:", nombre)

    print("\nProceso terminado")

# ========================================
# EJECUCIÓN
# ========================================
if __name__ == "__main__":
    generar_datos()