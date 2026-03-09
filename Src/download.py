import requests
from datetime import datetime
import csv
import pandas as pd
import matplotlib.pyplot as plt

def generar_listado():
    url_top = "https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/"
    
    try:
        
        respuesta = requests.get(url_top)
        datos = respuesta.json()
        juegos = datos.get('response', {}).get('ranks', [])

        if not juegos:
            print("No hay datos.")
            return
        
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        
        with open("Clean/listado_juegos.csv", "w", encoding="utf-8", newline='') as fichero:
            writer = csv.writer(fichero)
            writer.writerow(["Fecha", "Posicion", "AppID", "Nombre", "JugadoresConcurrentes"])
            
            
            with open("Clean/info_juegos.csv", "w", encoding="utf-8", newline='') as fichero_info:
                writer_info = csv.writer(fichero_info)
                writer_info.writerow(["AppID", "Nombre", "Fecha_Lanzamiento", "Géneros", "Desarrollador"])
                
                for i in range(len(juegos)):
                    appid = juegos[i].get('appid')
                    jugadores = juegos[i].get('concurrent_in_game', 0)

                  
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

                  
                    writer.writerow([fecha_actual, i+1, appid, nombre, jugadores])
                    print(f"OK Top: {nombre}")

                    
                    writer_info.writerow([appid, nombre, fecha_lanzamiento, generos, desarrollador])
                    print(f"OK Info: {nombre}")

        print("\nProceso completado.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    generar_listado()
    
