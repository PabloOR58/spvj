import streamlit as st
import pandas as pd
import os
import re

# ---------- 1. PAGE CONFIGURATION ---------- 
st.set_page_config(
    page_title="infosteam | Professional Dashboard",
    page_icon="🎮",
    layout="wide"
)

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
        "overview_tab": "📖 Resumen",
        "details_tab": "ℹ️ Detalles",
        "reviews_tab": "⭐ Reseñas",
        "information": "📋 Información",
        "release_information": "📅 Información de lanzamiento",
        "about_game": "📝 Acerca del juego",
        "developer_label": "Desarrollador",
        "platforms_label": "Plataformas",
        "genres_label": "Géneros",
        "rating_label": "Rating",
        "reviews_label": "Reseñas",
        "current_rank": "Posición actual",
        "current_players": "Jugadores actuales",
        "open_steam": "Abrir en Steam",
        "added_to_favorites": "Añadido a favoritos",
        "remove_from_favorites": "Quitar de favoritos",
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
        "overview_tab": "📖 Overview",
        "details_tab": "ℹ️ Details",
        "reviews_tab": "⭐ Reviews",
        "information": "📋 Information",
        "release_information": "📅 Release Information",
        "about_game": "📝 About This Game",
        "developer_label": "Developer",
        "platforms_label": "Platforms",
        "genres_label": "Genres",
        "rating_label": "Rating",
        "reviews_label": "Reviews",
        "current_rank": "Current Rank",
        "current_players": "Current Players",
        "open_steam": "Open in Steam",
        "added_to_favorites": "Added to favorites",
        "remove_from_favorites": "Remove from favorites",
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
        "overview_tab": "📖 Aperçu",
        "details_tab": "ℹ️ Détails",
        "reviews_tab": "⭐ Avis",
        "information": "📋 Informations",
        "release_information": "📅 Informations de sortie",
        "about_game": "📝 À propos du jeu",
        "developer_label": "Développeur",
        "platforms_label": "Plateformes",
        "genres_label": "Genres",
        "rating_label": "Note",
        "reviews_label": "Avis",
        "current_rank": "Rang actuel",
        "current_players": "Joueurs actuels",
        "open_steam": "Ouvrir sur Steam",
        "added_to_favorites": "Ajouté aux favoris",
        "remove_from_favorites": "Retirer des favoris",
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
        "overview_tab": "📖 Visão geral",
        "details_tab": "ℹ️ Detalhes",
        "reviews_tab": "⭐ Avaliações",
        "information": "📋 Informações",
        "release_information": "📅 Informações de lançamento",
        "about_game": "📝 Sobre este jogo",
        "developer_label": "Desenvolvedor",
        "platforms_label": "Plataformas",
        "genres_label": "Genres",
        "rating_label": "Avaliação",
        "reviews_label": "Avaliações",
        "current_rank": "Posição atual",
        "current_players": "Jogadores atuais",
        "open_steam": "Abrir no Steam",
        "added_to_favorites": "Adicionado aos favoritos",
        "remove_from_favorites": "Remover dos favoritos",
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

def get_fallback_game_background():
    """Get a fallback background image"""
    backgrounds = [
        "https://images.unsplash.com/photo-1556438064-2d7646166914?w=800&h=400&fit=crop",  # Gaming setup
        "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800&h=400&fit=crop",  # Controller
        "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&h=400&fit=crop",  # Gaming mouse
        "https://images.unsplash.com/photo-1593305841991-05c297ba4575?w=800&h=400&fit=crop",  # VR headset
    ]
    import random
    return random.choice(backgrounds)


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
        for df in [df_l, df_i, df_d]:
            if not df.empty and 'AppID' in df.columns:
                df['AppID'] = pd.to_numeric(df['AppID'], errors='coerce').fillna(0).astype(int)
        return df_l, df_i, df_d
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_listado, df_info, df_detalles = load_data()

# ---------- 6. SESSION STATE ---------- 
if "selected_game" not in st.session_state: st.session_state.selected_game = None
if "show_more" not in st.session_state: st.session_state.show_more = False
if "view" not in st.session_state: st.session_state.view = "Dashboard"
if "language_name" not in st.session_state: st.session_state.language_name = "Español"
if "language" not in st.session_state: st.session_state.language = LANGUAGE_CODES[st.session_state.language_name]
if "sel_date" not in st.session_state:
    if not df_listado.empty:
        dates = sorted(df_listado["Fecha"].unique(), reverse=True)
        st.session_state.sel_date = dates[0]
    else:
        st.session_state.sel_date = None

if "show_chat" not in st.session_state:
    st.session_state.show_chat = False

# ---------- 6. SIDEBAR ---------- 
with st.sidebar:
    current_t = get_translations(st.session_state.language)
    st.selectbox(current_t["language_label"], LANGUAGE_NAMES, index=LANGUAGE_NAMES.index(st.session_state.language_name), key="language_name")
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
                new_u = pd.DataFrame([[u_name, u_pass]], columns=["username", "password"])
                pd.concat([users, new_u]).to_csv(USERS_FILE, index=False)
                st.success(t["user_registered"])
    else:
        if st.button(t["login"], width='stretch'):
            users = pd.read_csv(USERS_FILE)
            valid = users[(users["username"] == u_name) & (users["password"] == u_pass)]
            if not valid.empty:
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

    view_menu_keys = ["Dashboard", "Market Trends", "Top Genres", "Top Developers", "Price Analysis", "Favorites"]
    view_menu_labels = [
        t["dashboard"], t["market_trends"], t["top_genres"],
        t["top_developers"], t["price_analysis"], t["favorites"]
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

    st.session_state.show_chat = st.checkbox("💬 Show Chat", value=st.session_state.show_chat)

# ---------- 7. VIEW: GAME DETAIL ---------- 
if st.session_state.selected_game:
    appid = st.session_state.selected_game
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

    st.title(f"🎮 {fix_nan(g_l['Nombre'] if g_l is not None else 'Game Details')}")

    # Tabs for more detailed view
    tab1, tab2, tab3 = st.tabs([t["overview_tab"], t["details_tab"], t["reviews_tab"]])

    with tab1:
        st.markdown(f"## {fix_nan(g_l.get('Nombre') if g_l is not None else 'Game')}")
        c1, c2 = st.columns([1.7, 1])
        with c1:
            game_name = fix_nan(g_l.get('Nombre') if g_l is not None else 'Game')
            st.markdown(f'<img src="{get_enhanced_game_background(appid, game_name)}" onerror=\'this.src="{IMG_ERROR}";\' style="width:100%; border-radius:12px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);" title="{game_name}">', unsafe_allow_html=True)
            st.markdown(f"### {t['information']}")
            st.write(f"**{t['developer_label']}:** {fix_nan(g_i.get('Desarrollador'))}")
            st.write(f"**{t['genres_label']}:** {fix_nan(g_i.get('Géneros'))}")
            st.write(f"**{t['platforms_label']}:** {fix_nan(g_i.get('Plataformas'))}")
            st.write(f"**{t['release_information']}:** {fix_nan(g_i.get('Fecha_Lanzamiento'))}")
            st.write(f"**{t['current_rank']}:** {fix_nan(g_rank)}")
            st.write(f"**{t['current_players']}:** {fix_nan(g_players)}")
            st.write(f"**{t['price']}:** {format_local_price(g_d.get('Precio', 'N/A'), st.session_state.language)}")
        with c2:
            game_name = fix_nan(g_l.get('Nombre') if g_l is not None else 'Game')
            st.markdown(f'<img src="{get_enhanced_game_image(appid, game_name)}" onerror=\'this.src="{IMG_ERROR}";\' style="width:100%; border-radius:12px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);" title="{game_name}">', unsafe_allow_html=True)
            st.metric(t["rating_label"], f"⭐ {rating_num}/100" if not pd.isna(rating_num) else "⭐ N/A")
            st.metric(t["reviews_label"], f"💬 {int(reviews_num):,}" if not pd.isna(reviews_num) else "💬 N/A")
            st.metric(t["current_rank"], f"#{int(rank_num)}" if not pd.isna(rank_num) else "N/A")
            st.metric(t["current_players"], f"👥 {int(players_num):,}" if not pd.isna(players_num) else "👥 N/A")
            st.markdown(f"[{t['open_steam']}](https://store.steampowered.com/app/{appid})")
        st.divider()
        st.subheader(t["about_game"])
        st.write(
            f"⭐ {t['rating_label']}: {rating}\n"
            f"💬 {t['reviews_label']}: {reviews}\n\n"
            "This summary uses the rating and review counts from the dataset to describe the selected game."
        )

    with tab2:
        st.markdown(f"### {t['details_tab']}")
        detail_rows = {
            t['developer_label']: fix_nan(g_i.get('Desarrollador')),
            t['genres_label']: fix_nan(g_i.get('Géneros')),
            t['platforms_label']: fix_nan(g_i.get('Plataformas')),
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

        # Add favorite functionality in game detail view
        if "user" in st.session_state:
            f_df = pd.read_csv(FAV_FILE)
            is_fav = ((f_df['username'] == st.session_state["user"]) & (f_df['appid'] == appid)).any()
            if is_fav:
                if st.button(t["remove_from_favorites"], width='stretch'):
                    f_df = f_df[~((f_df['username'] == st.session_state["user"]) & (f_df['appid'] == appid))]
                    f_df.to_csv(FAV_FILE, index=False)
                    st.rerun()
            else:
                if st.button(t["added_to_favorites"], width='stretch'):
                    new_fav = pd.DataFrame([[st.session_state["user"], appid]], columns=["username","appid"])
                    pd.concat([f_df, new_fav]).to_csv(FAV_FILE, index=False)
                    st.success(t["added_to_favorites"])
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
            for idx, row in user_favs.iterrows():
                aid = int(row["appid"])
                g_data = df_listado[df_listado["AppID"] == aid]
                g_name = g_data["Nombre"].iloc[0] if not g_data.empty else f"AppID: {aid}"

                c1, c2, c3 = st.columns([1, 4, 1])
                with c1:
                    st.markdown(f'<img src="{get_enhanced_game_image(aid, g_name)}" onerror=\'this.src="{IMG_ERROR}";\' style="width:100%; height:auto; border-radius:10px;" title="{g_name}">', unsafe_allow_html=True)
                with c2: 
                    st.markdown(f"### {g_name}")
                    if st.button(t["view_info"], key=f"fav_view_{aid}"):
                        st.session_state.selected_game = aid
                        st.rerun()
                with c3:
                    if st.button(t["remove"], key=f"del_{aid}_{idx}", width='stretch'):
                        favs_df = favs_df.drop(idx)
                        favs_df.to_csv(FAV_FILE, index=False)
                        st.rerun()
    st.stop()

# ---------- 9. ANALYTICS VIEWS ---------- 
df_day = df_listado[df_listado["Fecha"] == st.session_state.sel_date].copy()

if st.session_state.view == "Market Trends":
    st.title("📈 Market Trends & Sales")
    if 'Precio_USD' in df_detalles.columns:
        st.dataframe(df_detalles[['Nombre', 'Precio_USD', 'Rating', 'Reviews']].rename(columns={'Precio_USD': 'Price (USD)'}), width='stretch', hide_index=True)
    else:
        st.dataframe(df_detalles[['Nombre', 'Precio', 'Rating', 'Reviews']], width='stretch', hide_index=True)
    st.stop()

elif st.session_state.view == "Top Genres":
    st.title("📂 Genre Popularity")
    counts = df_info['Géneros'].str.split(', ').explode().value_counts()
    st.bar_chart(counts)
    st.dataframe(df_info[['Nombre', 'Géneros', 'Desarrollador']], width='stretch', hide_index=True)
    st.stop()

elif st.session_state.view == "Top Developers":
    st.title("👨‍💻 Top Developers")
    devs = df_info['Desarrollador'].value_counts().head(15)
    st.bar_chart(devs)
    st.dataframe(df_info[['Desarrollador', 'Nombre', 'Géneros']], width='stretch', hide_index=True)
    st.stop()

elif st.session_state.view == "Price Analysis":
    st.title("💰 Price Analysis")
    df_p = df_detalles.copy()
    df_p['Price_Val'] = df_p['Precio'].apply(convert_to_usd_numeric)
    st.bar_chart(df_p.sort_values('Price_Val', ascending=False).head(20).set_index('Nombre')['Price_Val'])
    if 'Precio_USD' in df_p.columns:
        st.dataframe(df_p[['Nombre', 'Precio_USD', 'Rating']].rename(columns={'Precio_USD': 'Price (USD)'}).sort_values('Price_Val', ascending=False), width='stretch', hide_index=True)
    else:
        st.dataframe(df_p[['Nombre', 'Precio', 'Rating']].sort_values('Price_Val', ascending=False), width='stretch', hide_index=True)
    st.stop()

# ---------- 10. MAIN DASHBOARD ---------- 
st.title("🎮 Dashboard")

# Dashboard metrics
m1, m2, m3 = st.columns(3)
m1.metric(t["players_online"], f"{int(df_day['JugadoresConcurrentes'].sum()):,}")
m2.metric(t["games_tracked"], f"{len(df_day)}")
m3.metric(t["top_game"], fix_nan(df_day.iloc[0]["Nombre"]) if len(df_day) > 0 else "N/A")

st.divider()

t1, t2, t3 = st.tabs(["📊 Live Rankings", "📈 Performance Trend", "📋 Data Explorer"])

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
                    st.markdown(f'<div style="height: 140px; overflow: hidden; border-radius: 5px; background: #161921;"><img src="{get_enhanced_game_image(aid, game_name)}" onerror=\'this.src="{IMG_ERROR}";\' style="width: 100%; height: 100%; object-fit: cover;" title="{game_title}"></div>', unsafe_allow_html=True)
                    st.markdown(f"**#{int(game.get('Posicion', 0))} {game_name}**")
                    
                    if st.button(t["details"], key=f"btn_{idx}", width='stretch'):
                        st.session_state.selected_game = aid
                        st.rerun()

                    if "user" in st.session_state:
                        if st.button(f"❤️ {t['favorite']}", key=f"fav_{idx}", width='stretch'):
                            f_df = pd.read_csv(FAV_FILE)
                            if not ((f_df['username'] == st.session_state["user"]) & (f_df['appid'] == aid)).any():
                                new_fav = pd.DataFrame([[st.session_state["user"], aid]], columns=["username","appid"])
                                pd.concat([f_df, new_fav]).to_csv(FAV_FILE, index=False)
                                st.success(f"{t['saved']} {game.get('Nombre')}")
                            else:
                                st.info(t["already_in_favorites"])
    if st.button(t["toggle_top"]):
        st.session_state.show_more = not st.session_state.show_more
        st.rerun()

with t2:
    st.header("📈 Historical Trends & Market Share")
    dates_list = sorted(df_listado["Fecha"].unique(), reverse=True)
    d_idx = dates_list.index(st.session_state.sel_date)
    tr_dates = dates_list[max(0, d_idx):min(len(dates_list), d_idx + 7)]
    df_trend_all = df_listado[df_listado["Fecha"].isin(tr_dates)].copy()
    sel_g = st.multiselect("Compare Games:", sorted(df_trend_all["Nombre"].unique()), default=df_day.head(5)["Nombre"].tolist())
    if sel_g:
        pivot = df_trend_all[df_trend_all["Nombre"].isin(sel_g)].pivot_table(index="Fecha", columns="Nombre", values="JugadoresConcurrentes")
        st.line_chart(pivot)
        st.divider()
        cl, cr = st.columns(2)
        with cl:
            st.subheader("🎭 Market Share")
            st.area_chart(pivot)
        with cr:
            st.subheader("🔥 Volatility")
            st.bar_chart(df_trend_all[df_trend_all["Nombre"].isin(sel_g)].groupby("Nombre")["JugadoresConcurrentes"].agg(["max", "min"]))

with t3:
    st.dataframe(df_day[["Posicion", "Nombre", "JugadoresConcurrentes", "AppID"]], width='stretch', hide_index=True)

st.divider()
st.caption("© 2026 infosteam — High-End Data Monitoring")

# Floating chat
if st.session_state.get('show_chat', False):
    with st.sidebar:
        st.subheader("💬 Game Chat")

        # Initialize chat history
        if "global_chat_history" not in st.session_state:
            st.session_state.global_chat_history = []

        # Display chat history
        chat_container = st.container(height=400)
        with chat_container:
            for message in st.session_state.global_chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Chat input
        user_input = st.chat_input("Ask about any game...")
        if user_input:
            st.session_state.global_chat_history.append({"role": "user", "content": user_input})

            # Find game mentioned in question - improved search
            game_data = None
            user_lower = user_input.lower()

            # More flexible game name matching
            for _, row in df_listado.iterrows():
                game_name = str(row.get('Nombre', '')).lower()
                if game_name:
                    # Check if game name is mentioned (partial match)
                    game_words = game_name.split()
                    if any(word in user_lower for word in game_words if len(word) > 3):  # Only words longer than 3 chars
                        appid = row.get('AppID')
                        g_i = df_info[df_info["AppID"] == appid].iloc[0] if not df_info[df_info["AppID"] == appid].empty else pd.Series()
                        g_d = df_detalles[df_detalles["AppID"] == appid].iloc[0] if not df_detalles[df_detalles["AppID"] == appid].empty else pd.Series()

                        game_data = {
                            "name": fix_nan(row.get('Nombre')),
                            "price": g_d.get('Precio', 'N/A'),
                            "developer": fix_nan(g_i.get('Desarrollador')),
                            "genres": fix_nan(g_i.get('Géneros')),
                            "rating": fix_nan(g_d.get('Rating')),
                            "reviews": fix_nan(g_d.get('Reviews')),
                            "release_date": fix_nan(g_i.get('Fecha_Lanzamiento')),
                            "platforms": fix_nan(g_i.get('Plataformas'))
                        }
                        break

            if game_data:
                bot_response = get_ai_response(user_input, game_data)
            else:
                bot_response = (
                    "I couldn't find a specific game in your question. "
                    "Please mention an exact game name from the database, such as 'Counter-Strike 2' or 'Dota 2'. "
                    "If you need more details, select the game from the dashboard. " 
                )

            st.session_state.global_chat_history.append({"role": "assistant", "content": bot_response})
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)