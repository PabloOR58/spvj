import streamlit as st
import pandas as pd
import os
import re
import base64

# ---------- 1. PAGE CONFIGURATION ---------- 
st.set_page_config(
    page_title="infosteam | Professional Dashboard",
    page_icon="🎮",
    layout="wide"
)

# Global styles for animated cards
st.markdown("""
<style>
.game-card { position: relative; border-radius:8px; overflow:hidden; transition: transform .25s ease, box-shadow .25s ease; }
.game-card img { width:100%; height:140px; object-fit:cover; transition: transform .35s ease; display:block; }
.game-card:hover { transform: translateY(-6px) scale(1.02); box-shadow:0 12px 30px rgba(0,0,0,0.45); }
.game-card:hover img { transform: scale(1.04); }
.game-card .meta { padding-top:6px; color: #cbd5e1; font-size:13px; }
.game-card__overlay { position:absolute; bottom:0; left:0; right:0; background:rgba(15,23,42,0.92); color:#f8fafc; padding:10px 12px; opacity:0; transform: translateY(12px); transition: opacity .25s ease, transform .25s ease; font-size:12px; line-height:1.4; z-index:2; }
.game-card:hover .game-card__overlay { opacity:1; transform: translateY(0); }
.badge { position:absolute; right:8px; top:8px; padding:4px 8px; border-radius:12px; font-weight:700; font-size:12px; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(155,92,255,0.7);} 70% { box-shadow: 0 0 0 10px rgba(155,92,255,0);} 100% { box-shadow: 0 0 0 0 rgba(155,92,255,0);} }
.badge.pulse { animation: pulse 2s infinite; }
.dashboard-card { position: relative; border-radius:8px; overflow:hidden; transition: transform .2s ease, box-shadow .2s ease; }
.dashboard-card img { width:100%; height:110px; object-fit:cover; transition: transform .3s ease; display:block; }
.dashboard-card:hover { transform: translateY(-4px); box-shadow:0 10px 26px rgba(0,0,0,0.35); }
.dashboard-card:hover img { transform: scale(1.03); filter:brightness(1); }
.dashboard-card__overlay { position:absolute; bottom:0; left:0; right:0; background:rgba(15,23,42,0.95); color:#f8fafc; padding:10px 12px; opacity:0; transform: translateY(14px); transition: opacity .2s ease, transform .2s ease; font-size:12px; line-height:1.4; z-index:2; }
.dashboard-card:hover .dashboard-card__overlay { opacity:1; transform: translateY(0); }
</style>
""", unsafe_allow_html=True)

IMG_ERROR = "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=460&h=215&fit=crop"

GAME_IMAGE_OVERRIDES = {
    "fivem": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=460&h=215&fit=crop",
    "windrose": "https://images.unsplash.com/photo-1556438064-2d7646166914?w=460&h=215&fit=crop",
}

NON_STEAM_IMAGE_TOKENS = [
    "fivem", "windrose", "mod", "server", "custom", "roleplay", "private", "rp"
]

USERS_FILE = "users.csv"
FAV_FILE = "favoritos.csv"

# ---------- 2. DATABASE INITIALIZATION ---------- 
def init_user_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["username", "password"]).to_csv(USERS_FILE, index=False)
    if not os.path.exists(FAV_FILE):
        pd.DataFrame(columns=["username", "appid"]).to_csv(FAV_FILE, index=False)

init_user_files()

LOGOS = {
    "windows": "https://img.icons8.com/color/48/000000/windows-10.png",
    "mac": "https://img.icons8.com/ios-filled/50/ffffff/mac-os.png",
    "linux": "https://img.icons8.com/color/48/000000/tux.png"
}

LANGUAGE_NAMES = ["Español", "English", "Français", "Português"]
LANGUAGE_CODES = {
    "Español": "es",
    "English": "en",
    "Français": "fr",
    "Português": "pt",
}
LANGUAGE_CODE_TO_NAME = {v: k for k, v in LANGUAGE_CODES.items()}
TRANSLATIONS = {
    "es": {
        "language_label": "🌐 Idioma",
        "account": "🔐 Cuenta",
        "mode": "Modo",
        "user": "Usuario",
        "password": "Contraseña",
        "create_account": "Crear Cuenta",
        "login": "Iniciar Sesión",
        "register": "Registrarse",
        "logout": "Cerrar sesión",
        "my_favorites": "⭐ Mis Favoritos",
        "navigation": "📑 Navegación",
        "select_date": "Seleccionar fecha:",
        "home_dashboard": "🏠 Inicio",
        "update_data": "🔄 Actualizar Datos",
        "dashboard": "Dashboard",
        "market_trends": "Tendencias",
        "top_genres": "Géneros",
        "top_developers": "Desarrolladores",
        "price_analysis": "Análisis de Precios",
        "popular_releases": "Populares",
        "favorites": "Favoritos",
        "user_exists": "¡El usuario ya existe!",
        "user_registered": "¡Usuario registrado!",
        "wrong_credentials": "Credenciales incorrectas",
        "please_login_favorites": "Por favor inicia sesión para ver tus favoritos.",
        "favorites_empty": "Tu lista de favoritos está vacía.",
        "saved": "Guardado:",
        "already_in_favorites": "Ya está en favoritos",
        "remove": "🗑️ Eliminar",
        "view_info": "Ver Información",
        "details": "Detalles",
        "favorite": "Favorito",
        "toggle_top": "Alternar Top 10 / 100",
        "players_online": "🟢 Jugadores en Línea",
        "games_tracked": "🎮 Juegos Seguimiento",
        "top_game": "🏆 Mejor Juego",
        "welcome": "Bienvenido",
        "price": "Precio",
        "free_to_play": "Gratis para jugar",
        "market_trends_title": "📈 Tendencias y ventas",
        "genre_popularity_title": "📂 Popularidad de géneros",
        "top_developers_title": "👨‍💻 Mejores desarrolladores",
        "popular_releases_title": "🎯 Populares",
        "price_analysis_title": "💰 Análisis de precios",
        "historical_trends_header": "📈 Tendencias históricas y cuota de mercado",
        "market_share": "🎭 Cuota de mercado",
        "volatility": "🔥 Volatilidad",
        "peak_24h_section": "📈 Pico 24h",
        "dashboard_title": "🎮 Dashboard",
        "live_rankings": "📊 Clasificación en vivo",
        "performance_trend": "📈 Tendencia de rendimiento",
        "data_explorer": "📋 Explorador de datos",
        "compare_games": "Comparar juegos:",
        "data_date": "Fecha de datos:",
        "no_24h_data": "No hay datos disponibles para las últimas 24 horas.",
        "popular_releases_description": "Un juego se considera popular si su pico de jugadores en la última semana supera al pico semanal de otros juegos lanzados en fechas similares (±7 días).",
        "copyright": "© 2026 infosteam — Monitorización de datos de alto nivel",
        "release_date": "Fecha de lanzamiento",
        "weekly_peak": "Pico última semana",
        "game_details": "Detalles del juego",
        "watch_trailer_on_steam": "Ver tráiler en Steam",
        "watch_live_streams_of": "Ver streams en vivo de {game_name}",
        "overview_tab": "📖 Resumen",
        "details_tab": "ℹ️ Detalles",
        "reviews_tab": "⭐ Reseñas",
        "information": "📋 Información",
        "release_information": "📅 Información de lanzamiento",
        "about_game": "📝 Acerca del juego",
        "trailer": "🎥 Trailer",
        "twitch_streams": "🎮 Streams en Vivo",
        "developer_label": "Desarrollador",
        "platforms_label": "Plataformas",
        "genres_label": "Géneros",
        "rating_label": "Rating",
        "reviews_label": "Reseñas",
        "current_rank": "Posición actual",
        "current_players": "Jugadores actuales",
        "peak_24h": "📈 Pico 24h",
        "open_steam": "Abrir en Steam",
        "open_twitch": "Ver en Twitch",
        "added_to_favorites": "Añadido a favoritos",
        "add_to_favorites": "Añadir a favoritos",
        "remove_from_favorites": "Quitar de favoritos",
        "summary_hint": "Este resumen usa las valoraciones y el número de reseñas del conjunto de datos para describir el juego seleccionado.",
    },
    "en": {
        "language_label": "🌐 Language",
        "account": "🔐 Account",
        "mode": "Mode",
        "user": "User",
        "password": "Password",
        "create_account": "Create Account",
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "my_favorites": "⭐ My Favorites",
        "navigation": "📑 Navigation",
        "select_date": "Select Date:",
        "home_dashboard": "🏠 Home",
        "update_data": "🔄 Update Data",
        "dashboard": "Dashboard",
        "market_trends": "Market Trends",
        "top_genres": "Top Genres",
        "top_developers": "Top Developers",
        "price_analysis": "Price Analysis",
        "popular_releases": "Popular Releases",
        "favorites": "Favorites",
        "user_exists": "User exists!",
        "user_registered": "User registered!",
        "wrong_credentials": "Wrong credentials",
        "please_login_favorites": "Please login to see your favorites.",
        "favorites_empty": "Your favorites list is empty.",
        "saved": "Saved:",
        "already_in_favorites": "Already in favorites",
        "remove": "🗑️ Remove",
        "view_info": "View Info",
        "details": "Details",
        "favorite": "Favorite",
        "toggle_top": "Toggle Top 10 / 100",
        "players_online": "🟢 Players Online",
        "games_tracked": "🎮 Games Tracked",
        "top_game": "🏆 Top Game",
        "welcome": "Welcome",
        "price": "Price",
        "free_to_play": "Free to Play",
        "market_trends_title": "📈 Market Trends & Sales",
        "genre_popularity_title": "📂 Genre Popularity",
        "top_developers_title": "👨‍💻 Top Developers",
        "popular_releases_title": "🎯 Popular Releases",
        "price_analysis_title": "💰 Price Analysis",
        "historical_trends_header": "📈 Historical Trends & Market Share",
        "market_share": "🎭 Market Share",
        "volatility": "🔥 Volatility",
        "peak_24h_section": "📈 24h Peak Players",
        "dashboard_title": "🎮 Dashboard",
        "live_rankings": "📊 Live Rankings",
        "performance_trend": "📈 Performance Trend",
        "data_explorer": "📋 Data Explorer",
        "compare_games": "Compare Games:",
        "data_date": "Data date:",
        "no_24h_data": "No data available for the latest 24 hours.",
        "popular_releases_description": "A game is considered popular if its weekly peak players exceed the weekly peak of other games released on similar dates (±7 days).",
        "copyright": "© 2026 infosteam — High-End Data Monitoring",
        "release_date": "Release Date",
        "weekly_peak": "Weekly peak",
        "game_details": "Game Details",
        "watch_trailer_on_steam": "Watch Trailer on Steam",
        "watch_live_streams_of": "Watch live streams of {game_name}",
        "overview_tab": "📖 Overview",
        "details_tab": "ℹ️ Details",
        "reviews_tab": "⭐ Reviews",
        "information": "📋 Information",
        "release_information": "📅 Release Information",
        "about_game": "📝 About This Game",
        "trailer": "🎥 Trailer",
        "twitch_streams": "🎮 Live Streams",
        "developer_label": "Developer",
        "platforms_label": "Platforms",
        "genres_label": "Genres",
        "rating_label": "Rating",
        "reviews_label": "Reviews",
        "current_rank": "Current Rank",
        "current_players": "Current Players",
        "peak_24h": "📈 24h Peak",
        "open_steam": "Open in Steam",
        "open_twitch": "Watch on Twitch",
        "added_to_favorites": "Added to favorites",
        "add_to_favorites": "Add to favorites",
        "remove_from_favorites": "Remove from favorites",
        "summary_hint": "This summary uses the rating and review counts from the dataset to describe the selected game.",
    },
    "fr": {
        "language_label": "🌐 Langue",
        "account": "🔐 Compte",
        "mode": "Mode",
        "user": "Utilisateur",
        "password": "Mot de passe",
        "create_account": "Créer un compte",
        "login": "Connexion",
        "register": "S'inscrire",
        "logout": "Déconnexion",
        "my_favorites": "⭐ Mes Favoris",
        "navigation": "📑 Navigation",
        "select_date": "Sélectionner la date:",
        "home_dashboard": "🏠 Accueil",
        "update_data": "🔄 Mettre à jour",
        "dashboard": "Tableau de bord",
        "market_trends": "Tendances",
        "top_genres": "Meilleurs Genres",
        "top_developers": "Meilleurs Développeurs",
        "price_analysis": "Analyse des Prix",
        "popular_releases": "Sorties Populaires",
        "favorites": "Favoris",
        "user_exists": "L'utilisateur existe déjà !",
        "user_registered": "Utilisateur enregistré !",
        "wrong_credentials": "Identifiants incorrects",
        "please_login_favorites": "Veuillez vous connecter pour voir vos favoris.",
        "favorites_empty": "Votre liste de favoris est vide.",
        "saved": "Enregistré :",
        "already_in_favorites": "Déjà dans les favoris",
        "remove": "🗑️ Supprimer",
        "view_info": "Voir Infos",
        "details": "Détails",
        "favorite": "Favori",
        "toggle_top": "Basculer Top 10 / 100",
        "players_online": "🟢 Joueurs en ligne",
        "games_tracked": "🎮 Jeux suivis",
        "top_game": "🏆 Meilleur jeu",
        "welcome": "Bienvenue",
        "price": "Prix",
        "free_to_play": "Gratuit",
        "market_trends_title": "📈 Tendances et ventes",
        "genre_popularity_title": "📂 Popularité des genres",
        "top_developers_title": "👨‍💻 Meilleurs développeurs",
        "popular_releases_title": "🎯 Sorties Populaires",
        "price_analysis_title": "💰 Analyse des prix",
        "historical_trends_header": "📈 Tendances historiques et part de marché",
        "market_share": "🎭 Part de marché",
        "volatility": "🔥 Volatilité",
        "peak_24h_section": "📈 Pic 24h",
        "dashboard_title": "🎮 Tableau de bord",
        "live_rankings": "📊 Classement en direct",
        "performance_trend": "📈 Tendance de performance",
        "data_explorer": "📋 Explorateur de données",
        "compare_games": "Comparer les jeux:",
        "data_date": "Date des données :",
        "no_24h_data": "Aucune donnée disponible pour les dernières 24 heures.",
        "popular_releases_description": "Un jeu est considéré comme populaire si son pic de joueurs hebdomadaire dépasse celui des autres jeux sortis à des dates similaires (±7 jours).",
        "copyright": "© 2026 infosteam — Surveillance de données haut de gamme",
        "release_date": "Date de sortie",
        "weekly_peak": "Pic hebdomadaire",
        "game_details": "Détails du jeu",
        "watch_trailer_on_steam": "Regarder la bande-annonce sur Steam",
        "watch_live_streams_of": "Voir les streams en direct de {game_name}",
        "overview_tab": "📖 Aperçu",
        "details_tab": "ℹ️ Détails",
        "reviews_tab": "⭐ Avis",
        "information": "📋 Informations",
        "release_information": "📅 Informations de sortie",
        "about_game": "📝 À propos du jeu",
        "trailer": "🎥 Bande-annonce",
        "twitch_streams": "🎮 Streams en Direct",
        "developer_label": "Développeur",
        "platforms_label": "Plateformes",
        "genres_label": "Genres",
        "rating_label": "Note",
        "reviews_label": "Avis",
        "current_rank": "Rang actuel",
        "current_players": "Joueurs actuels",
        "peak_24h": "📈 Pic 24h",
        "open_steam": "Ouvrir sur Steam",
        "open_twitch": "Voir sur Twitch",
        "added_to_favorites": "Ajouté aux favoris",
        "add_to_favorites": "Ajouter aux favoris",
        "remove_from_favorites": "Retirer des favoris",
        "summary_hint": "Ce résumé utilise les notes et le nombre d'avis du jeu dans l'ensemble de données pour décrire le jeu sélectionné.",
    },
    "pt": {
        "language_label": "🌐 Idioma",
        "account": "🔐 Conta",
        "mode": "Modo",
        "user": "Usuário",
        "password": "Senha",
        "create_account": "Criar conta",
        "login": "Entrar",
        "register": "Registrar",
        "logout": "Sair",
        "my_favorites": "⭐ Meus Favoritos",
        "navigation": "📑 Navegação",
        "select_date": "Selecionar data:",
        "home_dashboard": "🏠 Início",
        "update_data": "🔄 Atualizar Dados",
        "dashboard": "Painel",
        "market_trends": "Tendências",
        "top_genres": "Principais Gêneros",
        "top_developers": "Principais Desenvolvedores",
        "price_analysis": "Análise de Preços",
        "popular_releases": "Lançamentos Populares",
        "favorites": "Favoritos",
        "user_exists": "O usuário já existe!",
        "user_registered": "Usuário registrado!",
        "wrong_credentials": "Credenciais incorretas",
        "please_login_favorites": "Por favor faça login para ver seus favoritos.",
        "favorites_empty": "Sua lista de favoritos está vazia.",
        "saved": "Salvo:",
        "already_in_favorites": "Já está nos favoritos",
        "remove": "🗑️ Remover",
        "view_info": "Ver Informações",
        "details": "Detalhes",
        "favorite": "Favorito",
        "toggle_top": "Alternar Top 10 / 100",
        "players_online": "🟢 Jogadores Online",
        "games_tracked": "🎮 Jogos Monitorados",
        "top_game": "🏆 Melhor Jogo",
        "welcome": "Bem-vindo",
        "price": "Preço",
        "free_to_play": "Grátis para jogar",
        "market_trends_title": "📈 Tendências e vendas",
        "genre_popularity_title": "📂 Popularidade de gêneros",
        "top_developers_title": "👨‍💻 Principais desenvolvedores",
        "popular_releases_title": "🎯 Lançamentos populares",
        "price_analysis_title": "💰 Análise de preços",
        "historical_trends_header": "📈 Tendências históricas e participação de mercado",
        "market_share": "🎭 Participação de mercado",
        "volatility": "🔥 Volatilidade",
        "peak_24h_section": "📈 Pico 24h",
        "dashboard_title": "🎮 Painel",
        "live_rankings": "📊 Classificação ao vivo",
        "performance_trend": "📈 Tendência de desempenho",
        "data_explorer": "📋 Explorador de dados",
        "compare_games": "Comparar jogos:",
        "data_date": "Data dos dados:",
        "no_24h_data": "Nenhum dado disponível para as últimas 24 horas.",
        "popular_releases_description": "Um jogo é considerado popular se seu pico semanal de jogadores for maior que o pico semanal de outros jogos lançados em datas similares (±7 dias).",
        "copyright": "© 2026 infosteam — Monitoramento de dados de alto nível",
        "release_date": "Data de lançamento",
        "weekly_peak": "Pico semanal",
        "game_details": "Detalhes do jogo",
        "watch_trailer_on_steam": "Ver trailer no Steam",
        "watch_live_streams_of": "Assistir streams ao vivo de {game_name}",
        "overview_tab": "📖 Visão geral",
        "details_tab": "ℹ️ Detalhes",
        "reviews_tab": "⭐ Avaliações",
        "information": "📋 Informações",
        "release_information": "📅 Informações de lançamento",
        "about_game": "📝 Sobre este jogo",
        "trailer": "🎥 Trailer",
        "twitch_streams": "🎮 Streams ao Vivo",
        "developer_label": "Desenvolvedor",
        "platforms_label": "Plataformas",
        "genres_label": "Genres",
        "rating_label": "Avaliação",
        "reviews_label": "Avaliações",
        "current_rank": "Posição atual",
        "current_players": "Jogadores atuais",
        "peak_24h": "📈 Pico 24h",
        "open_steam": "Abrir no Steam",
        "open_twitch": "Ver no Twitch",
        "added_to_favorites": "Adicionado aos favoritos",
        "add_to_favorites": "Adicionar aos favoritos",
        "remove_from_favorites": "Remover dos favoritos",
        "summary_hint": "Este resumo usa as classificações e o número de avaliações do conjunto de dados para descrever o jogo selecionado.",
    },
}
CURRENCY_CONFIG = {
    "es": {"symbol": "€", "rate": 0.92},
    "fr": {"symbol": "€", "rate": 0.92},
    "pt": {"symbol": "€", "rate": 0.92},
    "en": {"symbol": "$", "rate": 1.00},
}
def get_currency_config(lang):
    return CURRENCY_CONFIG.get(lang, CURRENCY_CONFIG["en"])

def format_local_price(price_str, lang):
    val_usd = convert_to_usd_numeric(price_str)
    t = get_translations(lang)
    if val_usd == 0.0:
        return t["free_to_play"]
    cfg = get_currency_config(lang)
    amount = val_usd * cfg["rate"]
    return f"{cfg['symbol']}{amount:,.2f}"

def get_translations(lang):
    return TRANSLATIONS.get(lang, TRANSLATIONS["es"])

# ---------- PASSWORD ENCRYPTION FUNCTIONS ----------
def encrypt_password(password):
    """Encrypt password using base64 encoding"""
    if not password:
        return ""
    try:
        # Convert to bytes, encode with base64, then back to string
        password_bytes = password.encode('utf-8')
        encoded_bytes = base64.b64encode(password_bytes)
        return encoded_bytes.decode('utf-8')
    except:
        return password  # Fallback to plain text if encoding fails

def decrypt_password(encrypted_password):
    """Decrypt password from base64 encoding"""
    if not encrypted_password:
        return ""
    try:
        # Convert from string to bytes, decode from base64, then to string
        encrypted_bytes = encrypted_password.encode('utf-8')
        decoded_bytes = base64.b64decode(encrypted_bytes)
        return decoded_bytes.decode('utf-8')
    except:
        return encrypted_password  # Fallback to encrypted text if decoding fails

# ---------- 3. HELPER FUNCTIONS ---------- 
def fix_nan(val, default="-"):
    if pd.isna(val) or str(val).lower() == "nan" or str(val).strip() == "":
        return default
    return str(val)

def convert_to_usd_numeric(price_str):
    if pd.isna(price_str) or str(price_str).lower() == "nan": return 0.0
    p = str(price_str).upper()
    if any(word in p for word in ["GRATIS", "FREE", "0"]): return 0.0
    try:
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", p.replace(',', '.'))
        if not nums: return 0.0
        val = float(nums[0])
        rates = {"€": 1.08, "฿": 0.028, "РУБ": 0.011, "AED": 0.27, "CLP": 0.0011, "CDN$": 0.74, "¥": 0.0067}
        for s, r in rates.items():
            if s in p: return val * r
        return val
    except: return 0.0

def format_usd(price_str):
    val = convert_to_usd_numeric(price_str)
    return "Free to Play" if val == 0.0 else f"${round(val, 2)}"

def get_game_image(appid):
    """Get game image with multiple fallback options"""
    try:
        aid = int(float(appid))
        if aid <= 0:
            return get_fallback_game_image()
        return f"https://cdn.akamai.steamstatic.com/steam/apps/{aid}/header.jpg"
    except:
        return get_fallback_game_image()

def normalize_game_name(game_name):
    if not game_name:
        return ""
    name = str(game_name).strip().lower()
    return re.sub(r"[^a-z0-9\s]", "", name)


def normalize_game_name_compact(game_name):
    return normalize_game_name(game_name).replace(" ", "")


def get_special_game_image(game_name):
    normalized = normalize_game_name(game_name)
    compact = normalize_game_name_compact(game_name)
    for key, image_url in GAME_IMAGE_OVERRIDES.items():
        if key in normalized or key in compact:
            return image_url
    return None


def should_skip_steam_image(game_name):
    normalized = normalize_game_name(game_name)
    compact = normalize_game_name_compact(game_name)
    return any(token in normalized or token in compact for token in NON_STEAM_IMAGE_TOKENS)


@st.cache_data(ttl=86400)
def steam_image_exists(appid):
    try:
        aid = int(float(appid))
        if aid <= 0:
            return False
        import requests
        url = f"https://cdn.akamai.steamstatic.com/steam/apps/{aid}/header.jpg"
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except:
        return False


@st.cache_data(ttl=86400)
def steam_video_exists(appid):
    try:
        aid = int(float(appid))
        if aid <= 0:
            return False
        import requests
        # Use Steam API to get movie data
        url = f"https://store.steampowered.com/api/appdetails?appids={aid}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if str(aid) in data and data[str(aid)]['success']:
            app_data = data[str(aid)]['data']
            if 'movies' in app_data and len(app_data['movies']) > 0:
                # Return the HLS URL of the first movie
                first_movie = app_data['movies'][0]
                if 'hls_h264' in first_movie:
                    return first_movie['hls_h264']
        return False
    except:
        return False


def get_game_video(appid):
    """Get game trailer video URL"""
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


def get_fallback_game_image():
    """Get a fallback game image when Steam image is not available"""
    # Collection of gaming-themed placeholder images
    game_placeholders = [
        "https://images.unsplash.com/photo-1556438064-2d7646166914?w=460&h=215&fit=crop",  # Gaming setup
        "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=460&h=215&fit=crop",  # Controller
        "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=460&h=215&fit=crop",  # Gaming mouse
        "https://images.unsplash.com/photo-1593305841991-05c297ba4575?w=460&h=215&fit=crop",  # VR headset
        "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=460&h=215&fit=crop",  # Game characters
        "https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=460&h=215&fit=crop",  # Gaming room
        "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=460&h=215&fit=crop",  # RGB keyboard
        "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=460&h=215&fit=crop",  # Game controller
        "https://images.unsplash.com/photo-1552820728-8b83bb6b773f?w=460&h=215&fit=crop",  # Gaming PC
        "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=460&h=215&fit=crop",  # Controller closeup
        "https://images.unsplash.com/photo-1560419015-7c427e8ae5ba?w=460&h=215&fit=crop",  # Gaming chair
        "https://images.unsplash.com/photo-1592478411213-6153e4ebc696?w=460&h=215&fit=crop",  # Multiplayer gaming
        "https://images.unsplash.com/photo-1556438064-2d7646166914?w=460&h=215&fit=crop",  # Gaming setup 2
        "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=460&h=215&fit=crop",  # Esports
        "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=460&h=215&fit=crop",  # Mechanical keyboard
    ]

    # Return a random placeholder image
    import random
    return random.choice(game_placeholders)


def get_fallback_game_background():
    """Get a fallback game background when Steam background is not available"""
    background_placeholders = [
        "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=1600&h=900&fit=crop",
        "https://images.unsplash.com/photo-1556438064-2d7646166914?w=1600&h=900&fit=crop",
        "https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=1600&h=900&fit=crop",
        "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1600&h=900&fit=crop",
        "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=1600&h=900&fit=crop",
    ]
    import random
    return random.choice(background_placeholders)

def get_game_background(appid):
    try:
        aid = int(float(appid))
        if aid <= 0: return get_fallback_game_background()
        steam_bg = f"https://cdn.akamai.steamstatic.com/steam/apps/{aid}/page_bg_generated_v6b.jpg"
        return steam_bg
    except:
        return get_fallback_game_background()

def get_enhanced_game_image(appid, game_name=None):
    """Return the best available game image with fallback."""
    if game_name:
        special_image = get_special_game_image(game_name)
        if special_image:
            return special_image

    if steam_image_exists(appid):
        return get_game_image(appid)

    return get_fallback_game_image()

def get_ai_response(user_input, game_data):
    """Return a safe fallback AI-style response using known game data."""
    response_lines = [
        f"Here is what I found for {game_data.get('name', 'the game')}:",
        f"- Developer: {game_data.get('developer', 'Unknown')}",
        f"- Genres: {game_data.get('genres', 'Unknown')}",
        f"- Platforms: {game_data.get('platforms', 'Unknown')}",
        f"- Release Date: {game_data.get('release_date', 'Unknown')}",
        f"- Price: {game_data.get('price', 'Unknown')}",
        f"- Rating: {game_data.get('rating', 'Unknown')}",
        f"- Reviews: {game_data.get('reviews', 'Unknown')}"
    ]
    if "price" in user_input.lower():
        response_lines.append("This game appears to have the listed price and may be free to play depending on the store listing.")
    elif "rating" in user_input.lower() or "review" in user_input.lower():
        response_lines.append("The rating and reviews are based on the current dataset and may vary over time.")
    return "\n".join(response_lines)

def format_game_name_for_twitch(game_name):
    """Format game name for Twitch URL"""
    if not game_name:
        return ""
    # Remove special characters and replace spaces with %20 or use urllib
    import re
    import urllib.parse
    # Clean the name
    clean_name = re.sub(r'[^\w\s-]', '', game_name).strip()
    # URL encode
    return urllib.parse.quote(clean_name)


def get_platform_icons(platforms_str):
    """Convert platform string to visual icons"""
    if not platforms_str or pd.isna(platforms_str):
        return "❓ No disponible"

    platforms = [p.strip().lower() for p in str(platforms_str).split(',')]

    platform_icons = {
        'windows': '🪟 Windows',
        'mac': '🍎 macOS',
        'linux': '🐧 Linux',
        'android': '🤖 Android',
        'ios': '📱 iOS'
    }

    icons = []
    for platform in platforms:
        if platform in platform_icons:
            icons.append(platform_icons[platform])
        else:
            icons.append(f"❓ {platform.title()}")

    return " | ".join(icons)


def display_platforms_section(appid, lang):
    """Display platforms in an attractive card format"""
    t = get_translations(lang)

    # Get platforms for this game
    platforms_data = df_plataformas[df_plataformas["AppID"] == appid]
    if not platforms_data.empty:
        platforms_str = platforms_data["Plataformas"].iloc[0]
        platforms_display = get_platform_icons(platforms_str)
    else:
        platforms_display = "❓ No disponible"

    return platforms_display


def get_enhanced_game_background(appid, game_name=None):
    """Enhanced background getter that tries multiple sources"""
    try:
        # Convert appid to int and validate
        aid = int(float(appid)) if appid and str(appid).strip() else 0

        # Skip Steam check for known non-Steam games or invalid IDs
        skip_steam_games = [
            'fivem', 'fife', 'gta v fivem', 'grand theft auto v fivem',
            'multiplayer', 'server', 'custom', 'mod'
        ]

        should_check_steam = True
        if game_name and any(skip.lower() in game_name.lower() for skip in skip_steam_games):
            should_check_steam = False
        elif aid <= 0 or aid > 99999999:  # Invalid Steam AppID range
            should_check_steam = False

        # First try Steam background if valid
        if should_check_steam and steam_image_exists(appid):
            steam_bg = f"https://cdn.akamai.steamstatic.com/steam/apps/{aid}/page_bg_generated_v6b.jpg"
            return steam_bg

    except Exception as e:
        # If any error occurs, continue to fallback
        pass

    # Final fallback
    return get_fallback_game_background()

# ---------- 4. DATA LOADING ---------- 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "Clean")
SRC_DIR = os.path.join(BASE_DIR, "Src")
DOWNLOAD_SCRIPT = os.path.join(SRC_DIR, "download.py")


# ---------- LOAD DATA ----------
@st.cache_data(ttl=300)
def load_data():
    try:
        df_l = pd.read_csv(os.path.join(CLEAN_DIR, "listado_juegos.csv"))
        df_i = pd.read_csv(os.path.join(CLEAN_DIR, "info_juegos.csv"))
        df_d = pd.read_csv(os.path.join(CLEAN_DIR, "detalles_juegos.csv"), on_bad_lines="skip")
        df_p = pd.read_csv(os.path.join(CLEAN_DIR, "plataformas_juegos.csv"))
        for df in [df_l, df_i, df_d, df_p]:
            if not df.empty and 'AppID' in df.columns:
                df['AppID'] = pd.to_numeric(df['AppID'], errors='coerce').fillna(0).astype(int)
        return df_l, df_i, df_d, df_p
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_listado, df_info, df_detalles, df_plataformas = load_data()


def parse_date_safe(value):
    try:
        if pd.isna(value):
            return pd.NaT
        parsed = pd.to_datetime(value, dayfirst=True, errors='coerce')
        if pd.isna(parsed):
            parsed = pd.to_datetime(value, dayfirst=False, errors='coerce')
        return parsed
    except Exception:
        return pd.NaT


def get_recent_releases(ref_date, days=30):
    ref_dt = parse_date_safe(ref_date)
    if pd.isna(ref_dt) or df_info.empty:
        return pd.DataFrame()
    rel = df_info.copy()
    rel['__release_dt'] = rel['Fecha_Lanzamiento'].apply(parse_date_safe)
    window_start = ref_dt - pd.Timedelta(days=days)
    mask = (
        rel['__release_dt'].notna() &
        (rel['__release_dt'] <= ref_dt) &
        (rel['__release_dt'] >= window_start)
    )
    return rel.loc[mask].copy()


def peak_players_last_week(appid, ref_date):
    end_dt = parse_date_safe(ref_date)
    if pd.isna(end_dt) or df_listado.empty:
        return 0
    game_rows = df_listado[df_listado['AppID'] == int(appid)].copy()
    if game_rows.empty:
        return 0
    game_rows['__date'] = pd.to_datetime(game_rows['Fecha'], errors='coerce')
    window = game_rows[(game_rows['__date'] > (end_dt - pd.Timedelta(days=7))) & (game_rows['__date'] <= end_dt)]
    if window.empty:
        return 0
    values = pd.to_numeric(window['JugadoresConcurrentes'], errors='coerce').fillna(0)
    return int(values.max())


def get_latest_data_date():
    if df_listado.empty:
        return pd.Timestamp.today()
    dates = pd.to_datetime(df_listado['Fecha'], errors='coerce')
    return dates.max()


def get_peak_last_24h(ref_date):
    end_dt = parse_date_safe(ref_date)
    if pd.isna(end_dt) or df_listado.empty:
        return 0
    day_rows = df_listado.copy()
    day_rows['__date'] = pd.to_datetime(day_rows['Fecha'], errors='coerce')
    window = day_rows[day_rows['__date'] == end_dt]
    if window.empty:
        return 0
    values = pd.to_numeric(window['JugadoresConcurrentes'], errors='coerce').fillna(0)
    return int(values.max())


def get_latest_release_date():
    if df_info.empty:
        return pd.Timestamp.today()
    dates = df_info['Fecha_Lanzamiento'].apply(parse_date_safe)
    return dates.max()


def get_popular_reference_date():
    data_ref = get_latest_data_date()
    if not get_recent_releases(data_ref, days=30).empty:
        return data_ref
    return get_latest_release_date()


def compute_popular_releases(ref_date):
    recent = get_recent_releases(ref_date, days=30)
    if recent.empty:
        return pd.DataFrame(
            columns=['AppID', 'Nombre', 'Fecha_Lanzamiento', 'peak_last_week', 'is_popular']
        )

    rows = []
    for _, row in recent.iterrows():
        appid = int(row.get('AppID', 0))
        release_dt = parse_date_safe(row.get('Fecha_Lanzamiento'))
        peak_week = peak_players_last_week(appid, ref_date)
        rows.append({
            'AppID': appid,
            'Nombre': row.get('Nombre'),
            'Fecha_Lanzamiento': release_dt,
            'peak_last_week': peak_week,
        })

    df_recent = pd.DataFrame(rows)
    df_recent['is_popular'] = False

    for idx, row in df_recent.iterrows():
        if pd.isna(row['Fecha_Lanzamiento']):
            continue
        window_start = row['Fecha_Lanzamiento'] - pd.Timedelta(days=7)
        window_end = row['Fecha_Lanzamiento'] + pd.Timedelta(days=7)
        peers = df_recent[(df_recent['AppID'] != row['AppID']) &
                          (df_recent['Fecha_Lanzamiento'] >= window_start) &
                          (df_recent['Fecha_Lanzamiento'] <= window_end)]
        if peers.empty:
            df_recent.at[idx, 'is_popular'] = True
        else:
            df_recent.at[idx, 'is_popular'] = int(row['peak_last_week']) > int(peers['peak_last_week'].max())

    return df_recent.sort_values(['is_popular', 'peak_last_week'], ascending=[False, False]).reset_index(drop=True)


def prepare_popular_releases_display(popular_releases, t):
    if 'is_popular' in popular_releases.columns:
        popular_releases = popular_releases.loc[popular_releases['is_popular']]
    if 'Fecha_Lanzamiento' in popular_releases.columns:
        popular_releases = popular_releases.copy()
        popular_releases['Fecha_Lanzamiento'] = pd.to_datetime(
            popular_releases['Fecha_Lanzamiento'], errors='coerce'
        )
        popular_releases[t['release_date']] = popular_releases['Fecha_Lanzamiento'].dt.strftime('%Y-%m-%d')
    if popular_releases.empty:
        return pd.DataFrame(columns=['Nombre', 'AppID', t['release_date'], t['weekly_peak']])
    return popular_releases[['Nombre', 'AppID', t['release_date'], 'peak_last_week']].rename(
        columns={'peak_last_week': t['weekly_peak']}
    )


def safe_appid(value):
    try:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return int(float(value))
    except Exception:
        return None


def render_card_controls(aid, name, key_prefix, is_fav, t, compact=False):
    """Render details + favorite add/remove controls with consistent keys and behavior."""
    safe_id = safe_appid(aid)
    det_key = f"{key_prefix}_det_dash" if compact else f"{key_prefix}_det"
    remove_key = f"{key_prefix}_removefav_dash" if compact else f"{key_prefix}_removefav"
    add_key = f"{key_prefix}_addfav_dash" if compact else f"{key_prefix}_addfav"

    c1, c2 = st.columns([1, 1])
    with c1:
        if safe_id is None:
            st.button(t["details"], key=det_key, disabled=True)
        elif st.button(t["details"], key=det_key):
            st.session_state.selected_game = safe_id
            st.rerun()
    with c2:
        # Only allow favorites actions when a user is logged in
        if "user" not in st.session_state:
            st.info(t.get('please_login_favorites', 'Por favor inicia sesión para ver tus favoritos.'))
            return
        try:
            f_df = pd.read_csv(FAV_FILE)
        except:
            f_df = pd.DataFrame(columns=["username", "appid"])
        if is_fav:
            if safe_id is not None and st.button(t.get('remove_from_favorites', 'Quitar de favoritos'), key=remove_key):
                f_df = f_df[~((f_df['username'] == st.session_state['user']) & (f_df['appid'] == safe_id))]
                f_df.to_csv(FAV_FILE, index=False)
                st.success(t.get('remove_from_favorites', 'Quitar de favoritos'))
                st.rerun()
        else:
            # Use imperative label for add button
            if safe_id is not None and st.button(t.get('add_to_favorites', 'Añadir a favoritos'), key=add_key):
                new_fav = pd.DataFrame([[st.session_state['user'], safe_id]], columns=["username", "appid"])
                pd.concat([f_df, new_fav], ignore_index=True).to_csv(FAV_FILE, index=False)
                st.success(f"{t.get('saved', 'Guardado')} {name}")
                st.rerun()



def render_game_card(aid, name, t, key_prefix, price_raw=None, genres_raw=None, rating=None, reviews=None, rel_dt=None, extra_caption=None):
    """Render a standardized game card inside the current Streamlit column."""
    title_attr = f"{name}"
    img_url = get_enhanced_game_image(aid, name)
    # determine favorite state to show badge
    badge_html = ''
    is_fav = False
    safe_id = safe_appid(aid)
    if "user" in st.session_state and safe_id is not None:
        try:
            f_df = pd.read_csv(FAV_FILE)
            is_fav = ((f_df['username'] == st.session_state['user']) & (f_df['appid'] == safe_id)).any()
        except:
            is_fav = False
        # show filled heart when favorite, else show an outlined star to indicate addable
        if is_fav:
            badge_html = '<div class="badge pulse" style="position:absolute; right:8px; top:8px; background:transparent; color:#ff6b81; padding:4px 6px; border-radius:12px; font-weight:900; font-size:18px;" title="Favorito" aria-label="Favorito">❤️</div>'
        else:
            badge_html = '<div class="badge" style="position:absolute; right:8px; top:8px; background:transparent; color:#bdbdbd; padding:4px 6px; border-radius:12px; font-weight:700; font-size:16px;" title="'+t.get('add_to_favorites','Añadir a favoritos')+'" aria-label="'+t.get('add_to_favorites','Añadir a favoritos')+'">☆</div>'

    overlay_lines = []
    if rel_dt is not None:
        try:
            rel_str = parse_date_safe(rel_dt).strftime('%Y-%m-%d') if not pd.isna(parse_date_safe(rel_dt)) else fix_nan(rel_dt)
            overlay_lines.append(f"{t['release_date']}: {rel_str}")
        except:
            pass
    if price_raw is not None:
        overlay_lines.append(f"{t['price']}: {format_local_price(price_raw, st.session_state.language)}")
    if genres_raw:
        overlay_lines.append(f"{t['genres_label']}: {fix_nan(genres_raw)}")
    if rating is not None:
        overlay_lines.append(f"{t['rating_label']}: {fix_nan(rating)}")
    if reviews is not None and not pd.isna(reviews):
        overlay_lines.append(f"{t['reviews_label']}: {int(pd.to_numeric(reviews, errors='coerce')):,}")
    if safe_id is not None:
        try:
            info_row = df_info[df_info['AppID'] == safe_id]
            det_row = df_detalles[df_detalles['AppID'] == safe_id]
            if not info_row.empty:
                dev = fix_nan(info_row['Desarrollador'].iloc[0])
                if dev and dev.lower() != 'nan':
                    overlay_lines.insert(0, f"{t['developer_label']}: {dev}")
                platforms = display_platforms_section(aid, st.session_state.language)
                if platforms:
                    overlay_lines.append(platforms)
            if not det_row.empty and rating is None:
                det_rating = fix_nan(det_row['Rating'].iloc[0], None)
                if pd.notna(det_rating):
                    overlay_lines.append(f"{t['rating_label']}: {det_rating}")
            if not det_row.empty and (reviews is None or pd.isna(reviews)):
                det_reviews = pd.to_numeric(det_row['Reviews'].iloc[0], errors='coerce')
                if not pd.isna(det_reviews):
                    overlay_lines.append(f"{t['reviews_label']}: {int(det_reviews):,}")
        except:
            pass
    if extra_caption:
        overlay_lines.append(extra_caption)
    overlay_html = ''
    if overlay_lines:
        overlay_html = '<div class="game-card__overlay">' + '<br>'.join(overlay_lines) + '</div>'

    st.markdown(f'<div class="game-card" style="height: 140px; overflow: hidden; border-radius: 8px; background: #161921; position:relative;"><img src="{img_url}" onerror=\'this.src="{IMG_ERROR}";\' title="{title_attr}">{overlay_html}{badge_html}</div>', unsafe_allow_html=True)
    st.markdown(f"**{name}**")
    lines = []
    if rel_dt is not None:
        try:
            rel_str = parse_date_safe(rel_dt).strftime('%Y-%m-%d') if not pd.isna(parse_date_safe(rel_dt)) else fix_nan(rel_dt)
            lines.append(f"{t['release_date']}: {rel_str}")
        except:
            pass
    if extra_caption:
        lines.append(extra_caption)
    if lines:
        st.caption("  •  ".join(lines))

    price_display = format_local_price(price_raw if price_raw is not None else 'N/A', st.session_state.language)
    st.write(f"**{t['price']}:** {price_display}")
    if genres_raw:
        st.write(f"**{t['genres_label']}:** {fix_nan(genres_raw)}")
    if rating is not None:
        st.write(f"**{t['rating_label']}:** {fix_nan(rating)}")
    if reviews is not None and not pd.isna(reviews):
        st.write(f"**{t['reviews_label']}:** {int(pd.to_numeric(reviews, errors='coerce')):,}")

    # consistent controls (details + add/remove favorite)
    render_card_controls(aid, name, key_prefix, is_fav, t, compact=False)


def render_dashboard_card(aid, name, t, key_prefix, small_image_height=110, badge=None, players=None, peak=None):
    """Render a compact card used in dashboard tabs to differentiate from full navigation views."""
    img_url = get_enhanced_game_image(aid, name)
    # Determine badge color and background based on context
    badge_color = '#ffbf47'
    card_gradient = 'linear-gradient(135deg, #0f1720 0%, #111827 100%)'
    try:
        if badge == 'POP':
            badge_color = '#9b5cff'  # purple for popular
            card_gradient = 'linear-gradient(135deg, #6b21a8 0%, #111827 100%)'
        elif badge == '▲':
            badge_color = '#16a34a'  # green for growth
            card_gradient = 'linear-gradient(135deg, #052e18 0%, #08301a 100%)'
        elif peak is not None and float(peak) < 0:
            badge_color = '#ef4444'  # red for decline
            card_gradient = 'linear-gradient(135deg, #2b0f0f 0%, #111827 100%)'
        elif players is not None and int(players) > 100000:
            badge_color = '#f97316'  # orange for very large
            card_gradient = 'linear-gradient(135deg, #3a0f00 0%, #111827 100%)'
    except:
        pass
    pulse_class = ' pulse' if badge == 'POP' else ''
    badge_html = f'<div class="badge{pulse_class}" style="background:{badge_color};">{badge}</div>' if badge else ''
    # check favorites to show small fav badge (heart when favorited, star when not)
    fav_badge_html = ''
    is_fav_dash = False
    safe_id = safe_appid(aid)
    if "user" in st.session_state and safe_id is not None:
        try:
            f_df = pd.read_csv(FAV_FILE)
            is_fav_dash = ((f_df['username'] == st.session_state['user']) & (f_df['appid'] == safe_id)).any()
            if is_fav_dash:
                fav_badge_html = '<div class="badge" style="position:absolute; left:8px; top:8px; background:transparent; color:#ff6b81; padding:4px 6px; border-radius:12px; font-weight:900; font-size:16px;" title="Favorito" aria-label="Favorito">❤️</div>'
            else:
                fav_badge_html = '<div class="badge" style="position:absolute; left:8px; top:8px; background:transparent; color:#bdbdbd; padding:4px 6px; border-radius:12px; font-weight:700; font-size:14px;" title="'+t.get('add_to_favorites','Añadir a favoritos')+'" aria-label="'+t.get('add_to_favorites','Añadir a favoritos')+'">☆</div>'
        except:
            is_fav_dash = False

    overlay_lines = []
    try:
        info_row = df_info[df_info['AppID'] == aid]
        details_row = df_detalles[df_detalles['AppID'] == aid]
        if not info_row.empty:
            developer = fix_nan(info_row['Desarrollador'].iloc[0])
            if developer and developer.lower() != 'nan':
                overlay_lines.append(f"{t['developer_label']}: {developer}")
            release_date = parse_date_safe(info_row['Fecha_Lanzamiento'].iloc[0])
            if pd.notna(release_date):
                overlay_lines.append(f"{t['release_date']}: {release_date.strftime('%Y-%m-%d')}")
            genres = fix_nan(info_row['Géneros'].iloc[0])
            if genres and genres.lower() != 'nan':
                overlay_lines.append(f"{t['genres_label']}: {genres}")
            platforms = display_platforms_section(aid, st.session_state.language)
            if platforms:
                overlay_lines.append(platforms)
        if not details_row.empty:
            price_raw = details_row['Precio'].iloc[0]
            if pd.notna(price_raw):
                overlay_lines.append(f"{t['price']}: {format_local_price(price_raw, st.session_state.language)}")
    except:
        pass
    if players is not None:
        overlay_lines.append(f"👥 {int(players):,}")
    if peak is not None:
        overlay_lines.append(f"🔥 {int(peak):,}")
    overlay_html = ''
    if overlay_lines:
        overlay_html = '<div class="dashboard-card__overlay">' + '<br>'.join(overlay_lines[:4]) + '</div>'

    st.markdown(f'<div class="dashboard-card" style="position:relative; height:{small_image_height}px; overflow:hidden; border-radius:8px; background:{card_gradient}; box-shadow:0 6px 18px rgba(0,0,0,0.4);"><img src="{img_url}" onerror=\'this.src="{IMG_ERROR}";\'>{overlay_html}{badge_html}{fav_badge_html}</div>', unsafe_allow_html=True)
    st.markdown(f"**{name}**")
    meta = []
    if players is not None:
        meta.append(f"👥 {int(players):,}")
    if peak is not None:
        meta.append(f"🔥 {int(peak):,}")
    if meta:
        st.caption("  •  ".join(meta))

    # Use shared controls to keep details + favorites consistent across views
    render_card_controls(aid, name, key_prefix, is_fav_dash, t, compact=True)


# ---------- 6. SESSION STATE ---------- 
if "selected_game" not in st.session_state: st.session_state.selected_game = None
if "show_more" not in st.session_state: st.session_state.show_more = False
if "view" not in st.session_state: st.session_state.view = "Dashboard"
if "language_name" not in st.session_state:
    st.session_state.language_name = "Español"
elif st.session_state.language_name not in LANGUAGE_NAMES:
    st.session_state.language_name = LANGUAGE_CODE_TO_NAME.get(st.session_state.language_name, "Español")
if "language" not in st.session_state:
    st.session_state.language = LANGUAGE_CODES.get(st.session_state.language_name, "es")
if "sel_date" not in st.session_state:
    if not df_listado.empty:
        dates = sorted(df_listado["Fecha"].unique(), reverse=True)
        st.session_state.sel_date = dates[0]
    else:
        st.session_state.sel_date = None

# ---------- 6. SIDEBAR ---------- 
with st.sidebar:
    current_t = get_translations(st.session_state.language)
    language_index = LANGUAGE_NAMES.index(st.session_state.language_name) if st.session_state.language_name in LANGUAGE_NAMES else 0
    st.selectbox(current_t["language_label"], LANGUAGE_NAMES, index=language_index, key="language_name")
    if st.session_state.language_name not in LANGUAGE_CODES:
        st.session_state.language_name = LANGUAGE_CODE_TO_NAME.get(st.session_state.language_name, "Español")
    st.session_state.language = LANGUAGE_CODES.get(st.session_state.language_name, "es")
    t = get_translations(st.session_state.language)

    st.markdown(f"### {t['account']}")
    auth_mode = st.radio(t["mode"], [t["login"], t["register"]], label_visibility="collapsed")
    u_name = st.text_input(t["user"])
    u_pass = st.text_input(t["password"], type="password")

    if auth_mode == t["register"]:
        if st.button(t["create_account"], width='stretch'):
            users = pd.read_csv(USERS_FILE)
            if u_name in users["username"].values:
                st.error(t["user_exists"])
            else:
                # Encrypt password before saving
                encrypted_pass = encrypt_password(u_pass)
                new_u = pd.DataFrame([[u_name, encrypted_pass]], columns=["username", "password"])
                pd.concat([users, new_u]).to_csv(USERS_FILE, index=False)
                st.success(t["user_registered"])
    else:
        if st.button(t["login"], width='stretch'):
            users = pd.read_csv(USERS_FILE)
            # Check for valid login (support both encrypted and plain text passwords for migration)
            valid_user = None
            for _, user_row in users.iterrows():
                if user_row["username"] == u_name:
                    stored_pass = user_row["password"]
                    # Try encrypted comparison first
                    encrypted_input = encrypt_password(u_pass)
                    if stored_pass == encrypted_input:
                        valid_user = user_row
                        break
                    # Try plain text comparison for backward compatibility
                    elif stored_pass == u_pass:
                        valid_user = user_row
                        # Migrate to encrypted password
                        users.loc[users["username"] == u_name, "password"] = encrypted_input
                        users.to_csv(USERS_FILE, index=False)
                        break

            if valid_user is not None:
                st.session_state["user"] = u_name
                st.rerun()
            else:
                st.error(t["wrong_credentials"])
    if "user" in st.session_state:
        st.success(f"👤 {t['welcome'] if 'welcome' in t else 'Welcome'}, {st.session_state['user']}")
        if st.button(t["logout"], width='stretch'):
            del st.session_state["user"]
            st.rerun()
        if st.button(t["my_favorites"], width='stretch'):
            st.session_state.view = "Favorites"
            st.rerun()

    st.divider()
    st.markdown(f"### {t['navigation']}")

    view_menu_keys = ["Dashboard", "Market Trends", "Popular Releases", "Top Genres", "Top Developers", "Price Analysis", "Favorites"]
    view_menu_labels = [
        t["dashboard"], t["market_trends"], t["popular_releases"],
        t["top_genres"], t["top_developers"], t["price_analysis"], t["favorites"]
    ]
    current_index = view_menu_keys.index(st.session_state.view) if st.session_state.view in view_menu_keys else 0
    selected_label = st.selectbox("", view_menu_labels, index=current_index, label_visibility="collapsed")
    st.session_state.view = view_menu_keys[view_menu_labels.index(selected_label)]

    if not df_listado.empty:
        dates = sorted(df_listado["Fecha"].unique(), reverse=True)
        st.session_state.sel_date = st.selectbox(t["select_date"], dates, index=dates.index(st.session_state.sel_date) if st.session_state.sel_date in dates else 0)

    if st.button(t["home_dashboard"], width='stretch'):
        st.session_state.selected_game = None
        st.session_state.view = "Dashboard"
        st.rerun()

    if st.button(t["update_data"], width='stretch'):
        load_data.clear()
        st.rerun()

# ---------- 7. VIEW: GAME DETAIL ---------- 
selected_game_id = safe_appid(st.session_state.selected_game) if 'selected_game' in st.session_state else None
if selected_game_id:
    appid = selected_game_id
    st.session_state.selected_game = selected_game_id
    g_l = df_listado[df_listado["AppID"] == appid].iloc[0] if not df_listado[df_listado["AppID"] == appid].empty else None
    g_i = df_info[df_info["AppID"] == appid].iloc[0] if not df_info[df_info["AppID"] == appid].empty else pd.Series()
    g_d = df_detalles[df_detalles["AppID"] == appid].iloc[0] if not df_detalles[df_detalles["AppID"] == appid].empty else pd.Series()

    # Define metric values before use
    g_rank = df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)]["Posicion"].iloc[0] if not df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)].empty else "N/A"
    g_players = df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)]["JugadoresConcurrentes"].iloc[0] if not df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)].empty else "N/A"
    rating = fix_nan(g_d.get('Rating'), 'N/A')
    rating_num = pd.to_numeric(rating, errors='coerce')
    reviews = fix_nan(g_d.get('Reviews'), 'N/A')
    reviews_num = pd.to_numeric(reviews, errors='coerce')
    rank_num = pd.to_numeric(g_rank, errors='coerce')
    players_num = pd.to_numeric(g_players, errors='coerce')

    st.title(f"🎮 {fix_nan(g_l['Nombre'] if g_l is not None else t['game_details'])}")

    # Tabs for more detailed view
    tab1, tab2, tab3 = st.tabs([t["overview_tab"], t["details_tab"], t["reviews_tab"]])

    with tab1:
        game_name = fix_nan(g_l.get('Nombre') if g_l is not None else 'Game')

        # Hero section with background image and title
        st.markdown(f"""
        <div style="position: relative; height: 300px; border-radius: 15px; overflow: hidden; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
            <img src="{get_enhanced_game_background(appid, game_name)}" style="width: 100%; height: 100%; object-fit: cover; filter: brightness(0.4);" />
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">
                <h1 style="font-size: 3em; margin: 0; font-weight: bold;">{game_name}</h1>
                <p style="font-size: 1.2em; margin: 10px 0 0 0; opacity: 0.9;">{fix_nan(g_i.get('Desarrollador'))}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Key metrics in a nice grid
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t["rating_label"], f"⭐ {rating_num}/100" if not pd.isna(rating_num) else "⭐ N/A")
        with col2:
            st.metric(t["reviews_label"], f"💬 {int(reviews_num):,}" if not pd.isna(reviews_num) else "💬 N/A")
        with col3:
            st.metric(t["current_rank"], f"#{int(rank_num)}" if not pd.isna(rank_num) else "🏆 N/A")
        with col4:
            st.metric(t["current_players"], f"👥 {int(players_num):,}" if not pd.isna(players_num) else "👥 N/A")

        # Action buttons
        st.markdown("---")
        col_a, col_b, col_c = st.columns([1, 1, 2])
        with col_a:
            st.markdown(f"[![Steam](https://img.icons8.com/color/48/000000/steam.png)](https://store.steampowered.com/app/{appid})", unsafe_allow_html=True)
            st.caption(f"[{t['open_steam']}](https://store.steampowered.com/app/{appid})")
        with col_b:
            game_name_for_twitch = format_game_name_for_twitch(game_name)
            twitch_url = f"https://www.twitch.tv/directory/game/{game_name_for_twitch}" if game_name_for_twitch else "https://www.twitch.tv"
            st.markdown(f"[![Twitch](https://img.icons8.com/color/48/9146FF/twitch.png)]({twitch_url})", unsafe_allow_html=True)
            st.caption(f"[{t['open_twitch']}]({twitch_url})")
        with col_c:
            st.metric(t["price"], format_local_price(g_d.get('Precio', 'N/A'), st.session_state.language))

        st.markdown("---")

        # Media section - Trailer and Twitch side by side
        st.markdown(f"## 🎬 {t['trailer']} & {t['twitch_streams']}")

        media_col1, media_col2 = st.columns(2)

        with media_col1:
            st.markdown(f"### {t['trailer']}")
            video_url = get_game_video(appid)
            if video_url:
                video_html = f"""
                <video controls style="width:100%; border-radius:10px; box-shadow: 0 4px 16px rgba(0,0,0,0.2);" poster="{get_enhanced_game_image(appid, game_name)}">
                    <source src="{video_url}" type="application/x-mpegURL">
                    Your browser does not support HLS video playback.
                </video>
                """
                st.components.v1.html(video_html, height=250)
            else:
                st.markdown(f"🎥 [{t['watch_trailer_on_steam']}](https://store.steampowered.com/app/{appid})")

        with media_col2:
            st.markdown(f"### {t['twitch_streams']}")
            if game_name_for_twitch:
                # Create an attractive Twitch link instead of blocked iframe
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #9146FF 0%, #1e1e2e 100%); padding: 30px; border-radius: 15px; text-align: center; color: white; height: 200px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 8px 32px rgba(145, 70, 255, 0.3);">
                    <div style="font-size: 3em; margin-bottom: 10px;">🔴</div>
                    <h3 style="margin: 0 0 15px 0; color: #ffffff;">{t['twitch_streams']}</h3>
                    <p style="margin: 0 0 20px 0; opacity: 0.8;">{t['watch_live_streams_of'].format(game_name=game_name)}</p>
                    <a href="{twitch_url}" target="_blank" style="background: #ffffff; color: #9146FF; padding: 12px 24px; border-radius: 25px; text-decoration: none; font-weight: bold; display: inline-block; transition: all 0.3s ease;">
                        🎮 {t['open_twitch']}
                    </a>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #9146FF 0%, #1e1e2e 100%); padding: 30px; border-radius: 15px; text-align: center; color: white; height: 200px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <div style="font-size: 3em; margin-bottom: 10px;">🔴</div>
                    <h3 style="margin: 0 0 15px 0;">{t['twitch_streams']}</h3>
                    <a href="https://www.twitch.tv" target="_blank" style="background: #ffffff; color: #9146FF; padding: 12px 24px; border-radius: 25px; text-decoration: none; font-weight: bold;">
                        🎮 {t['open_twitch']}
                    </a>
                </div>
                """, unsafe_allow_html=True)
        # Game information in organized cards
        st.markdown(f"## 📋 {t['information']}")

        info_col1, info_col2 = st.columns(2)

        with info_col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white; margin-bottom: 15px;">
                <h4 style="margin: 0 0 10px 0;">{t['about_game']}</h4>
            </div>
            """, unsafe_allow_html=True)
            st.write(f"**{t['developer_label']}:** {fix_nan(g_i.get('Desarrollador'))}")
            st.write(f"**{t['genres_label']}:** {fix_nan(g_i.get('Géneros'))}")
            st.write(f"**{t['platforms_label']}:** {display_platforms_section(appid, st.session_state.language)}")
            st.write(f"**{t['release_information']}:** {fix_nan(g_i.get('Fecha_Lanzamiento'))}")

        with info_col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 15px; color: white; margin-bottom: 15px;">
                <h4 style="margin: 0 0 10px 0;">📊 Statistics</h4>
            </div>
            """, unsafe_allow_html=True)
            st.write(f"**{t['current_rank']}:** {fix_nan(g_rank)}")
            st.write(f"**{t['current_players']}:** {fix_nan(g_players)}")
            st.write(f"**{t['price']}:** {format_local_price(g_d.get('Precio', 'N/A'), st.session_state.language)}")

        st.markdown("---")
        st.subheader(t["about_game"])
        st.markdown(
            f"**{t['developer_label']}:** {fix_nan(g_i.get('Desarrollador'))}  \n"
            f"**{t['platforms_label']}:** {display_platforms_section(appid, st.session_state.language)}  \n"
            f"**{t['release_information']}:** {fix_nan(g_i.get('Fecha_Lanzamiento'))}  \n"
            f"**{t['price']}:** {format_local_price(g_d.get('Precio', 'N/A'), st.session_state.language)}  \n"
            f"**⭐ {t['rating_label']}:** {rating}  \n"
            f"**💬 {t['reviews_label']}:** {reviews}  \n\n"
            f"{t['summary_hint']}"
        )

    with tab2:
        st.markdown(f"### {t['details_tab']}")
        detail_rows = {
            t['developer_label']: fix_nan(g_i.get('Desarrollador')),
            t['genres_label']: fix_nan(g_i.get('Géneros')),
            t['platforms_label']: display_platforms_section(appid, st.session_state.language),
            t['release_information']: fix_nan(g_i.get('Fecha_Lanzamiento')),
            t['price']: format_local_price(g_d.get('Precio', 'N/A'), st.session_state.language),
            t['rating_label']: fix_nan(g_d.get('Rating'), 'N/A'),
            t['reviews_label']: fix_nan(g_d.get('Reviews'), 'N/A'),
            t['current_rank']: fix_nan(g_rank),
            t['current_players']: fix_nan(g_players),
        }
        st.table(pd.DataFrame.from_dict(detail_rows, orient="index", columns=["Value"]))

    with tab3:
        st.markdown(f"### {t['reviews_tab']}")
        if not pd.isna(rating_num):
            st.metric(t["rating_label"], f"{rating_num}/100")
        else:
            st.write(f"**{t['rating_label']}:** N/A")
        if not pd.isna(reviews_num):
            st.metric(t["reviews_label"], f"{int(reviews_num):,}")
        else:
            st.write(f"**{t['reviews_label']}:** N/A")

        # Use unified controls for details/favorites in game detail view
        if "user" in st.session_state:
            game_title = fix_nan(g_l.get('Nombre') if g_l is not None else t['game_details'])
            try:
                f_df = pd.read_csv(FAV_FILE)
                is_fav = ((f_df['username'] == st.session_state["user"]) & (f_df['appid'] == appid)).any()
            except:
                is_fav = False
            render_card_controls(appid, game_title, "detail", is_fav, t, compact=False)
    st.stop()

# ---------- 8. VIEW: FAVORITES ---------- 
if st.session_state.view == "Favorites":
    st.title(f"⭐ {t['my_favorites']}")
    if "user" not in st.session_state:
        st.warning(t["please_login_favorites"])
    else:
        favs_df = pd.read_csv(FAV_FILE)
        user_favs = favs_df[favs_df["username"] == st.session_state["user"]]
        if user_favs.empty:
            st.info(t["favorites_empty"])
        else:
            favs_list = user_favs.reset_index(drop=True)
            cols_per_row = 4
            for r in range(0, len(favs_list), cols_per_row):
                cols = st.columns(cols_per_row)
                for i, col in enumerate(cols):
                    idx = r + i
                    if idx < len(favs_list):
                        row = favs_list.iloc[idx]
                        aid = int(row["appid"])
                        # gather info
                        g_name = None
                        g_row = df_listado[df_listado['AppID'] == aid]
                        if not g_row.empty:
                            g_name = g_row['Nombre'].iloc[0]
                        else:
                            info_row = df_info[df_info['AppID'] == aid]
                            if not info_row.empty:
                                g_name = info_row['Nombre'].iloc[0]
                        if not g_name:
                            g_name = f"AppID: {aid}"

                        with col:
                            # use render helper
                            det_row = df_detalles[df_detalles['AppID'] == aid]
                            price_raw = det_row['Precio'].iloc[0] if not det_row.empty else None
                            info_row = df_info[df_info['AppID'] == aid]
                            genres_raw = info_row['Géneros'].iloc[0] if not info_row.empty else None
                            rel_dt = info_row['Fecha_Lanzamiento'].iloc[0] if not info_row.empty else None
                            render_game_card(aid, fix_nan(g_name), t, f"fav_{idx}", price_raw=price_raw, genres_raw=genres_raw, rel_dt=rel_dt)
    st.stop()

# ---------- 9. ANALYTICS VIEWS ---------- 
df_day = df_listado[df_listado["Fecha"] == st.session_state.sel_date].copy()

if st.session_state.view == "Market Trends":
    st.title(t["market_trends_title"])
    st.markdown(t.get('market_trends_title', ''))
    market_df = df_detalles.copy()
    market_df['Reviews_Num'] = pd.to_numeric(market_df['Reviews'], errors='coerce').fillna(0)
    top = market_df.sort_values('Reviews_Num', ascending=False).head(24)
    if top.empty:
        st.info("No data available")
    else:
        cols_per_row = 4
        for r in range(0, len(top), cols_per_row):
            cols = st.columns(cols_per_row)
            for i, col in enumerate(cols):
                idx = r + i
                if idx < len(top):
                    row = top.iloc[idx]
                    aid = int(row.get('AppID', 0)) if not pd.isna(row.get('AppID', 0)) else 0
                    with col:
                        render_game_card(aid, fix_nan(row.get('Nombre')), t, f"mt_{idx}", price_raw=row.get('Precio'), rating=row.get('Rating'), reviews=row.get('Reviews'))
    st.stop()

elif st.session_state.view == "Top Genres":
    st.title(t["genre_popularity_title"])
    counts = df_info['Géneros'].str.split(', ').explode().value_counts()
    st.bar_chart(counts)
    # Show representative games for genres as cards
    sample = df_info.head(24)
    cols_per_row = 4
    for r in range(0, len(sample), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            idx = r + i
            if idx < len(sample):
                row = sample.iloc[idx]
                aid = int(row.get('AppID', 0)) if not pd.isna(row.get('AppID', 0)) else 0
                with col:
                    render_game_card(aid, fix_nan(row.get('Nombre')), t, f"tg_{idx}", genres_raw=row.get('Géneros'), rel_dt=row.get('Fecha_Lanzamiento'))
    st.stop()

elif st.session_state.view == "Top Developers":
    st.title(t["top_developers_title"])
    devs = df_info['Desarrollador'].value_counts().head(15)
    st.bar_chart(devs)
    sample = df_info.sort_values('Desarrollador').head(24)
    cols_per_row = 4
    for r in range(0, len(sample), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            idx = r + i
            if idx < len(sample):
                row = sample.iloc[idx]
                aid = int(row.get('AppID', 0)) if not pd.isna(row.get('AppID', 0)) else 0
                with col:
                    render_game_card(aid, fix_nan(row.get('Nombre')), t, f"td_{idx}", genres_raw=row.get('Géneros'), rel_dt=row.get('Fecha_Lanzamiento'))
    st.stop()

elif st.session_state.view == "Popular Releases":
    st.title(t["popular_releases_title"])
    st.subheader(t["popular_releases_title"])
    st.markdown(t["popular_releases_description"])
    popular_ref_date = get_popular_reference_date()
    popular_releases = compute_popular_releases(popular_ref_date)
    popular_releases = popular_releases.loc[popular_releases['is_popular']] if 'is_popular' in popular_releases.columns else popular_releases
    display_df = prepare_popular_releases_display(popular_releases, t)
    # Show as cards similar to the main dashboard
    popular_list = popular_releases.reset_index(drop=True)
    if popular_list.empty:
        st.info("No popular releases found.")
    else:
        cols_per_row = 4
        for r in range(0, len(popular_list), cols_per_row):
            cols = st.columns(cols_per_row)
            for i, col in enumerate(cols):
                idx = r + i
                if idx < len(popular_list):
                    row = popular_list.iloc[idx]
                    aid = int(row.get('AppID', 0)) if not pd.isna(row.get('AppID', 0)) else 0
                    name = fix_nan(row.get('Nombre'))
                    rel_dt = row.get('Fecha_Lanzamiento')
                    rel_str = parse_date_safe(rel_dt).strftime('%Y-%m-%d') if not pd.isna(parse_date_safe(rel_dt)) else fix_nan(rel_dt)
                    peak = int(row.get('peak_last_week', 0)) if not pd.isna(row.get('peak_last_week', 0)) else 0

                    with col:
                        title_attr = f"{name} - {t['weekly_peak']}: {peak}"
                        st.markdown(f'<div style="height: 140px; overflow: hidden; border-radius: 8px; background: #161921;"><img src="{get_enhanced_game_image(aid, name)}" onerror=\'this.src="{IMG_ERROR}";\' style="width:100%; height:100%; object-fit:cover;" title="{title_attr}"></div>', unsafe_allow_html=True)
                        st.markdown(f"**{name}**")
                        st.caption(f"{t['release_date']}: {rel_str}  •  {t['weekly_peak']}: {peak}")

                        # Price and genres
                        try:
                            price_row = df_detalles[df_detalles['AppID'] == aid]
                            price_raw = price_row['Precio'].iloc[0] if not price_row.empty else None
                        except:
                            price_raw = None
                        try:
                            info_row = df_info[df_info['AppID'] == aid]
                            genres_raw = info_row['Géneros'].iloc[0] if not info_row.empty else None
                        except:
                            genres_raw = None

                        price_display = format_local_price(price_raw if price_raw is not None else 'N/A', st.session_state.language)
                        genres_display = fix_nan(genres_raw, 'N/A')
                        st.write(f"**{t['price']}:** {price_display}")
                        st.write(f"**{t['genres_label']}:** {genres_display}")

                        # Use unified card renderer (includes details + favorites controls)
                        render_game_card(aid, name, t, f"pop_{idx}", price_raw=price_raw, genres_raw=genres_raw, rel_dt=rel_dt, extra_caption=f"{t['weekly_peak']}: {peak}")
    st.stop()

elif st.session_state.view == "Price Analysis":
    st.title(t["price_analysis_title"])
    df_p = df_detalles.copy()
    df_p['Price_Val'] = df_p['Precio'].apply(convert_to_usd_numeric)
    st.bar_chart(df_p.sort_values('Price_Val', ascending=False).head(20).set_index('Nombre')['Price_Val'])
    sorted_df = df_p.sort_values('Price_Val', ascending=False).head(24)
    cols_per_row = 4
    for r in range(0, len(sorted_df), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            idx = r + i
            if idx < len(sorted_df):
                row = sorted_df.iloc[idx]
                aid = int(row.get('AppID', 0)) if not pd.isna(row.get('AppID', 0)) else 0
                with col:
                    render_game_card(aid, fix_nan(row.get('Nombre')), t, f"pa_{idx}", price_raw=row.get('Precio'), rating=row.get('Rating'))
    st.stop()

# ---------- 10. MAIN DASHBOARD ---------- 
st.title(t["dashboard_title"])

# Dashboard metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric(t["players_online"], f"{int(df_day['JugadoresConcurrentes'].sum()):,}")
m2.metric(t["games_tracked"], f"{len(df_day)}")
m3.metric(t["top_game"], fix_nan(df_day.iloc[0]["Nombre"]) if len(df_day) > 0 else "N/A")
m4.metric(t["peak_24h"], f"{get_peak_last_24h(get_latest_data_date()):,}")

st.divider()

t1, t2, t3, t4, t5 = st.tabs([t["live_rankings"], t["performance_trend"], t["data_explorer"], t["peak_24h_section"], t["popular_releases_title"]])

with t1:
    # AHORA MUESTRA 100 JUEGOS EN VEZ DE 50
    limit = 100 if st.session_state.show_more else 10
    top_df = df_day.head(limit).reset_index(drop=True)
    for r in range(0, len(top_df), 5):
        cols = st.columns(5)
        for i, col in enumerate(cols):
            idx = r + i
            if idx < len(top_df):
                game = top_df.iloc[idx]
                aid = int(game.get("AppID", 0))
                with col:
                    game_name = fix_nan(game.get("Nombre"))
                    game_title = f'{game_name} - Rank #{int(game.get("Posicion", 0))} - {int(game.get("JugadoresConcurrentes", 0))} players'
                    # Use unified game card (image, title, meta, details + favorites)
                    pos = int(game.get('Posicion', 0)) if not pd.isna(game.get('Posicion', 0)) else 0
                    players = int(game.get('JugadoresConcurrentes', 0)) if not pd.isna(game.get('JugadoresConcurrentes', 0)) else 0
                    render_game_card(aid, fix_nan(game_name), t, f"lr_{idx}", extra_caption=f"#{pos}  •  👥 {players:,}")
    if st.button(t["toggle_top"]):
        st.session_state.show_more = not st.session_state.show_more
        st.rerun()

with t2:
    st.header(t["historical_trends_header"])
    # Show compact performance trend summary and top movers
    dates_list = sorted(df_listado["Fecha"].unique(), reverse=True)
    if len(dates_list) < 2:
        st.info(t.get('no_24h_data', 'Not enough data for trends'))
    else:
        prev_date = dates_list[1]
        cur = df_listado[df_listado['Fecha'] == st.session_state.sel_date]
        prev = df_listado[df_listado['Fecha'] == prev_date]
        merged = cur.set_index('AppID')[['JugadoresConcurrentes']].rename(columns={'JugadoresConcurrentes':'cur_players'}).join(prev.set_index('AppID')[['JugadoresConcurrentes']].rename(columns={'JugadoresConcurrentes':'prev_players'}), how='left').fillna(0)
        merged['growth'] = merged['cur_players'].astype(float) - merged['prev_players'].astype(float)
        movers = merged.sort_values('growth', ascending=False).head(8).reset_index()

        cols_per_row = 4
        for r in range(0, len(movers), cols_per_row):
            cols = st.columns(cols_per_row)
            for i, col in enumerate(cols):
                idx = r + i
                if idx < len(movers):
                    row = movers.iloc[idx]
                    aid = int(row['AppID'])
                    g_row = df_listado[df_listado['AppID'] == aid]
                    name = g_row['Nombre'].iloc[0] if not g_row.empty else f"AppID: {aid}"
                    with col:
                        render_dashboard_card(aid, fix_nan(name), t, f"trend_{idx}", players=row['cur_players'], peak=row['growth'], badge='▲')
        st.divider()
        st.subheader(t["market_share"])
        sel_g = st.multiselect(t["compare_games"], sorted(df_listado["Nombre"].unique()), default=df_day.head(5)["Nombre"].tolist())
        if sel_g:
            pivot = df_listado[df_listado["Nombre"].isin(sel_g)].pivot_table(index="Fecha", columns="Nombre", values="JugadoresConcurrentes")
            st.line_chart(pivot)

with t3:
    st.header(t.get('data_explorer', t['data_explorer']))
    # Compact explorer: show top items for selected date (no freeform search)
    sample = df_day.head(12).reset_index(drop=True)
    cols_per_row = 4
    for r in range(0, len(sample), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            idx = r + i
            if idx < len(sample):
                row = sample.iloc[idx]
                aid = int(row.get('AppID', 0))
                with col:
                    render_dashboard_card(aid, fix_nan(row.get('Nombre')), t, f"de_{idx}", players=row.get('JugadoresConcurrentes'))

with t4:
    st.subheader(t["peak_24h_section"])
    peak_value = get_peak_last_24h(get_latest_data_date())
    st.metric(t["peak_24h"], f"{peak_value:,}")
    latest_date = get_latest_data_date()
    if not pd.isna(latest_date):
        st.write(f"{t['data_date']} {latest_date.strftime('%Y-%m-%d')}")

    if len(df_day) > 0:
        # Ensure numeric players and unique AppID to avoid duplicates
        tmp = df_day.copy()
        tmp['JugadoresConcurrentes'] = pd.to_numeric(tmp['JugadoresConcurrentes'], errors='coerce').fillna(0)
        top24_df = tmp.sort_values('JugadoresConcurrentes', ascending=False).drop_duplicates(subset='AppID').head(12).reset_index(drop=True)
        cols_per_row = 4
        for r in range(0, len(top24_df), cols_per_row):
            cols = st.columns(cols_per_row)
            for i, col in enumerate(cols):
                idx = r + i
                if idx < len(top24_df):
                    row = top24_df.iloc[idx]
                    aid = int(row.get('AppID', 0))
                    with col:
                        render_dashboard_card(aid, fix_nan(row.get('Nombre')), t, f"p24_{idx}", players=row.get('JugadoresConcurrentes'))
    else:
        st.info(t["no_24h_data"])

with t5:
    st.subheader(t["popular_releases_title"])
    st.markdown(t["popular_releases_description"])
    popular_ref_date = get_popular_reference_date()
    popular_releases = compute_popular_releases(popular_ref_date)
    popular_releases = popular_releases.loc[popular_releases['is_popular']] if 'is_popular' in popular_releases.columns else popular_releases
    popular_short = popular_releases.sort_values('peak_last_week', ascending=False).head(8).reset_index(drop=True)
    cols_per_row = 4
    for r in range(0, len(popular_short), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            idx = r + i
            if idx < len(popular_short):
                row = popular_short.iloc[idx]
                aid = int(row.get('AppID', 0))
                name = fix_nan(row.get('Nombre'))
                with col:
                    render_dashboard_card(aid, name, t, f"popdash_{idx}", peak=row.get('peak_last_week'), badge='POP')

st.divider()
st.caption(t["copyright"])
