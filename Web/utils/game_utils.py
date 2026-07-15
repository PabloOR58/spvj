"""
Utilidades para procesamiento de juegos, géneros y imágenes
"""
import re
import random
import pandas as pd
import requests
import streamlit as st
from utils.config import (
    IMG_ERROR, GAME_IMAGE_OVERRIDES, NON_STEAM_IMAGE_TOKENS,
    GAME_PLACEHOLDERS, BACKGROUND_PLACEHOLDERS, CACHE_TTL
)


def normalize_genre_token(token):
    """Normaliza un token de género"""
    if pd.isna(token):
        return None
    token_text = str(token).strip()
    if not token_text:
        return None
    token_text = re.sub(r"[\|/;]+", ",", token_text)
    token_text = re.sub(r"\s+", " ", token_text)
    token_text = token_text.title()
    replacements = {
        "Rpg": "RPG",
        "Abenteuer": "Adventure",
        "Kostenlos Spielbar": None,
        "Free To Play": None,
        "Gratis": None,
        "Free": None,
        "N/A": None,
        "None": None,
        "Unknown": None,
    }
    if token_text in replacements:
        return replacements[token_text]
    if token_text.isdigit() or len(token_text) <= 1:
        return None
    return token_text


def get_genre_tokens(genre_text):
    """Extrae tokens de géneros desde un texto"""
    if pd.isna(genre_text):
        return []
    tokens = []
    for raw in re.split(r"[;,|/]+", str(genre_text)):
        normalized = normalize_genre_token(raw)
        if normalized:
            tokens.append(normalized)
    return tokens


def normalize_game_name(game_name):
    """Normaliza el nombre de un juego"""
    if not game_name:
        return ""
    name = str(game_name).strip().lower()
    return re.sub(r"[^a-z0-9\s]", "", name)


def normalize_game_name_compact(game_name):
    """Normaliza el nombre de un juego (compacto)"""
    return normalize_game_name(game_name).replace(" ", "")


def get_special_game_image(game_name):
    """Obtiene una imagen especial si existe para el juego"""
    normalized = normalize_game_name(game_name)
    compact = normalize_game_name_compact(game_name)
    for key, image_url in GAME_IMAGE_OVERRIDES.items():
        if key in normalized or key in compact:
            return image_url
    return None


def should_skip_steam_image(game_name):
    """Determina si se debe saltear la imagen de Steam"""
    normalized = normalize_game_name(game_name)
    compact = normalize_game_name_compact(game_name)
    return any(token in normalized or token in compact for token in NON_STEAM_IMAGE_TOKENS)


@st.cache_data(ttl=CACHE_TTL)
def steam_image_exists(appid):
    """Verifica si existe una imagen en Steam para el AppID"""
    try:
        aid = int(float(appid))
        if aid <= 0:
            return False
        url = f"https://cdn.akamai.steamstatic.com/steam/apps/{aid}/header.jpg"
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except:
        return False


@st.cache_data(ttl=CACHE_TTL)
def steam_video_exists(appid):
    """Obtiene la URL del video del juego en Steam"""
    try:
        aid = int(float(appid))
        if aid <= 0:
            return False
        url = f"https://store.steampowered.com/api/appdetails?appids={aid}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if str(aid) in data and data[str(aid)]['success']:
            app_data = data[str(aid)]['data']
            if 'movies' in app_data and len(app_data['movies']) > 0:
                first_movie = app_data['movies'][0]
                if 'hls_h264' in first_movie:
                    return first_movie['hls_h264']
        return False
    except:
        return False


def get_game_image(appid):
    """Obtiene la imagen del juego"""
    try:
        aid = int(float(appid))
        if aid <= 0:
            return get_fallback_game_image()
        return f"https://cdn.akamai.steamstatic.com/steam/apps/{aid}/header.jpg"
    except:
        return get_fallback_game_image()


def get_fallback_game_image():
    """Obtiene una imagen fallback para juegos"""
    return random.choice(GAME_PLACEHOLDERS)


def get_fallback_game_background():
    """Obtiene un fondo fallback para juegos"""
    return random.choice(BACKGROUND_PLACEHOLDERS)


def get_game_background(appid):
    """Obtiene el fondo del juego"""
    try:
        aid = int(float(appid))
        if aid <= 0:
            return get_fallback_game_background()
        steam_bg = f"https://cdn.akamai.steamstatic.com/steam/apps/{aid}/page_bg_generated_v6b.jpg"
        return steam_bg
    except:
        return get_fallback_game_background()


def get_enhanced_game_image(appid, game_name=None):
    """Obtiene la mejor imagen disponible del juego"""
    if game_name:
        special_image = get_special_game_image(game_name)
        if special_image:
            return special_image

    if steam_image_exists(appid):
        return get_game_image(appid)

    return get_fallback_game_image()


def get_enhanced_game_background(appid, game_name=None):
    """Obtiene el mejor fondo disponible del juego"""
    try:
        aid = int(float(appid)) if appid and str(appid).strip() else 0

        skip_steam_games = [
            'fivem', 'fife', 'gta v fivem', 'grand theft auto v fivem',
            'multiplayer', 'server', 'custom', 'mod'
        ]

        should_check_steam = True
        if game_name and any(skip.lower() in game_name.lower() for skip in skip_steam_games):
            should_check_steam = False
        elif aid <= 0 or aid > 99999999:
            should_check_steam = False

        if should_check_steam and steam_image_exists(appid):
            steam_bg = f"https://cdn.akamai.steamstatic.com/steam/apps/{aid}/page_bg_generated_v6b.jpg"
            return steam_bg

    except Exception as e:
        pass

    return get_fallback_game_background()


def get_game_video(appid):
    """Obtiene la URL del video del juego"""
    try:
        aid = int(float(appid))
        if aid <= 0:
            return None
        video_url = steam_video_exists(appid)
        if video_url:
            return video_url
        return None
    except:
        return None


@st.cache_data(ttl=CACHE_TTL)
def get_steam_app_details(appid):
    """Obtiene los detalles del juego desde Steam API"""
    try:
        from utils.data_utils import safe_appid
        aid = safe_appid(appid)
        if not aid:
            return {}
        url = f"https://store.steampowered.com/api/appdetails?appids={aid}&cc=us&l=en"
        response = requests.get(url, timeout=10, headers={"User-Agent": "infosteam-pro-dashboard/1.0"})
        data = response.json()
        if str(aid) in data and data[str(aid)].get("success"):
            return data[str(aid)]["data"] or {}
    except Exception:
        pass
    return {}


def get_steam_store_tags(appid):
    """Obtiene las etiquetas del juego desde Steam"""
    details = get_steam_app_details(appid)
    tags = []
    for section in ("genres", "categories"):
        for item in details.get(section, []):
            label = item.get("description") or item.get("title") or item.get("name")
            if label and label not in tags:
                tags.append(label)
    return tags[:10]


def get_platform_icons(platforms_str):
    """Convierte string de plataformas a texto visual"""
    if not platforms_str or pd.isna(platforms_str):
        return "No disponible"

    platforms = [p.strip().lower() for p in str(platforms_str).split(',')]

    platform_icons = {
        'windows': 'Windows',
        'mac': 'macOS',
        'linux': 'Linux',
        'android': 'Android',
        'ios': 'iOS'
    }

    icons = []
    for platform in platforms:
        if platform in platform_icons:
            icons.append(platform_icons[platform])
        else:
            icons.append(f"{platform.title()}")

    return " | ".join(icons)


def format_game_name_for_twitch(game_name):
    """Formatea el nombre del juego para URL de Twitch"""
    if not game_name:
        return ""

    import urllib.parse
    clean_name = re.sub(r'[^\w\s-]', '', game_name).strip()
    return urllib.parse.quote(clean_name)


def generate_review_snippets(game_name, rating, reviews):
    """Genera snippets de reseñas basados en rating y cantidad"""
    try:
        rating_val = float(rating)
        reviews_val = int(float(reviews))
    except Exception:
        return []

    if reviews_val <= 0:
        return []

    if rating_val >= 85:
        return [
            f"Los jugadores valoran {game_name} muy positivamente: {int(rating_val)}/100.",
            "Destacan especialmente su jugabilidad fluida y equilibrio.",
            f"Con más de {reviews_val:,} opiniones, se nota una comunidad activa y satisfecha."
        ]
    if rating_val >= 70:
        return [
            f"{game_name} mantiene una buena valoración: {int(rating_val)}/100.",
            "Muchos usuarios destacan su contenido y experiencia general.",
            f"Las {reviews_val:,} reseñas muestran interés y opiniones mayoritariamente positivas."
        ]
    return [
        f"{game_name} tiene una puntuación de {int(rating_val)}/100.",
        "Algunos usuarios aprecian su propuesta, aunque piden mejoras en ciertos aspectos.",
        f"Con {reviews_val:,} reseñas, hay una base suficiente para obtener una idea general del juego."
    ]
