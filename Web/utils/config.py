"""
Configuración central de la aplicación
"""
import os

# Directorio base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEAN_DIR = os.path.join(BASE_DIR, "Clean")
SRC_DIR = os.path.join(BASE_DIR, "Src")
DOWNLOAD_SCRIPT = os.path.join(SRC_DIR, "download.py")

# Archivos de datos
USERS_FILE = "users.csv"
FAV_FILE = "favoritos.csv"

# Rutas de datos CSV
DATA_FILES = {
    "listado": os.path.join(CLEAN_DIR, "listado_juegos.csv"),
    "info": os.path.join(CLEAN_DIR, "info_juegos.csv"),
    "detalles": os.path.join(CLEAN_DIR, "detalles_juegos.csv"),
    "plataformas": os.path.join(CLEAN_DIR, "plataformas_juegos.csv"),
}

# URLs de imágenes
IMG_ERROR = "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=460&h=215&fit=crop"

GAME_IMAGE_OVERRIDES = {
    "fivem": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=460&h=215&fit=crop",
    "windrose": "https://images.unsplash.com/photo-1556438064-2d7646166914?w=460&h=215&fit=crop",
}

NON_STEAM_IMAGE_TOKENS = [
    "fivem", "windrose", "mod", "server", "custom", "roleplay", "private", "rp"
]

# Logos
LOGOS = {
    "windows": "https://img.icons8.com/color/48/000000/windows-10.png",
    "mac": "https://img.icons8.com/ios-filled/50/ffffff/mac-os.png",
    "linux": "https://img.icons8.com/color/48/000000/tux.png"
}

# Game placeholders
GAME_PLACEHOLDERS = [
    "https://images.unsplash.com/photo-1556438064-2d7646166914?w=460&h=215&fit=crop",
    "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=460&h=215&fit=crop",
    "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=460&h=215&fit=crop",
    "https://images.unsplash.com/photo-1593305841991-05c297ba4575?w=460&h=215&fit=crop",
    "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=460&h=215&fit=crop",
    "https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=460&h=215&fit=crop",
    "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=460&h=215&fit=crop",
    "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=460&h=215&fit=crop",
    "https://images.unsplash.com/photo-1556438064-2d7646166914?w=460&h=215&fit=crop",
    "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=460&h=215&fit=crop",
    "https://images.unsplash.com/photo-1560419015-7c427e8ae5ba?w=460&h=215&fit=crop",
    "https://images.unsplash.com/photo-1592478411213-6153e4ebc696?w=460&h=215&fit=crop",
    "https://images.unsplash.com/photo-1556438064-2d7646166914?w=460&h=215&fit=crop",
    "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=460&h=215&fit=crop",
    "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=460&h=215&fit=crop",
]

BACKGROUND_PLACEHOLDERS = [
    "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=1600&h=900&fit=crop",
    "https://images.unsplash.com/photo-1556438064-2d7646166914?w=1600&h=900&fit=crop",
    "https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=1600&h=900&fit=crop",
    "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1600&h=900&fit=crop",
    "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1600&h=900&fit=crop",
]

# Currency configuration
CURRENCY_CONFIG = {
    "es": {"symbol": "€", "rate": 0.92},
    "fr": {"symbol": "€", "rate": 0.92},
    "pt": {"symbol": "€", "rate": 0.92},
    "en": {"symbol": "$", "rate": 1.00},
}

# Cache TTL en segundos
CACHE_TTL = 86400  # 24 horas para datos
CACHE_TTL_SHORT = 300  # 5 minutos para datos en vivo
