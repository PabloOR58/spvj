"""
Función auxiliar para mostrar secciones de plataformas
"""
import pandas as pd
from utils.game_utils import get_platform_icons


def display_platforms_section(appid, lang, df_plataformas):
    """Muestra las plataformas disponibles para un juego"""
    platforms_data = df_plataformas[df_plataformas["AppID"] == appid]
    if not platforms_data.empty:
        platforms_str = platforms_data["Plataformas"].iloc[0]
        platforms_display = get_platform_icons(platforms_str)
    else:
        platforms_display = "No disponible"
    return platforms_display
