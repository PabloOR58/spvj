import requests
from datetime import datetime


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
        
        with open("listado_juegos.csv", "w", encoding="utf-8") as fichero:
            fichero.write("Fecha,Posicion,Juego,Jugadores\n")
            
            for i in range(len(juegos)):
                appid = juegos[i].get('appid')
                jugadores = juegos[i].get('concurrent_in_game', 0)

                url_n = f"https://store.steampowered.com/api/appdetails?appids={appid}&filters=basic"
                try:
                    res_n = requests.get(url_n).json()
                    nombre = res_n[str(appid)]['data']['name']
                except:
                    nombre = f"ID: {appid}"

               
                linea = f"{fecha_actual},{i+1},{nombre},{jugadores}\n"
                fichero.write(linea)
                print(f"OK: {nombre}")

        print("\n Proceso completado.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    generar_listado()




    
