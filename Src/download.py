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
# ELIMINAR DATOS DE HOY
# ========================================
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

# ========================================
# PLATAFORMAS
# ========================================
def get_platforms(appid):
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

# ========================================
# FUNCIÓN PRINCIPAL
# ========================================
def generar_datos():

    os.makedirs("Clean", exist_ok=True)
    fecha = datetime.now().strftime("%Y-%m-%d")

    # =========================
    # TOP JUGADOS
    # =========================
    path_jugados = "Clean/listado_juegos.csv"
    path_plataformas = "Clean/plataformas_juegos.csv"

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
    juegos = requests.get(url).json().get("response", {}).get("ranks", [])

    with open(path_jugados, "a", newline="", encoding="utf-8") as f1, \
         open(path_plataformas, "a", newline="", encoding="utf-8") as f2:

        writer1 = csv.writer(f1)
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

    # =========================
    # TOP VENDIDOS
    # =========================
    path_vendidos = "Clean/top_vendidos.csv"

    crear_csv(path_vendidos, ["Fecha", "Posicion", "ID", "Nombre"])
    eliminar_fecha(path_vendidos, fecha)

    url = "https://store.steampowered.com/api/featuredcategories"
    data = requests.get(url).json()

    top = data.get("top_sellers", {}).get("items", [])

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

# ========================================
# EJECUCIÓN
# ========================================
if __name__ == "__main__":
    generar_datos()