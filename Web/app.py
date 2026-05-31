import streamlit as st #biblioteca para la interfaz web
import pandas as pd #librería para la manipulación y el análisis de datos
import os #librería para interactuar con el sistema operativo y manejar archivos y directorios 
import re #Sirve para gestionar rutas de archivos de forma segura e independiente de si ejecutas la app en Windows, Linux o Docker. También la usas para comprobar si un archivo físico existe en el disco duro, como los CSV de usuarios o favoritos
import base64 #Se usa para buscar y extraer patrones de texto complejos. En tu código es fundamental para la conversión de divisas, ya que analiza los textos de los precios de Steam (que vienen con símbolos raros como €, $, ฿, o letras) y extrae únicamente la parte numérica para poder hacer cálculos matemáticos con ella.
import subprocess #librería para ejecutar comandos del sistema operativo, aunque no se utiliza en el código proporcionado, podría ser útil para tareas como actualizar datos o ejecutar scripts externos. Por ejemplo, sirven para comprobar qué versión de Python se está usando (sys.version) o para lanzar tareas secundarias del sistema operativo directamente desde un botón de la web.
import sys #librería para interactuar con el intérprete de Python, aunque no se utiliza en el código proporcionado, podría ser útil para tareas como manejar argumentos de línea de comandos o controlar la salida del programa. Por ejemplo, sirven para comprobar qué versión de Python se está usando (sys.version) o para lanzar tareas secundarias del sistema operativo directamente desde un botón de la web.
import plotly.graph_objects as go #librería para crear gráficos interactivo visualizar datos de tendencias, análisis de precios, etc.

 
st.set_page_config(
    page_title="infosteam | Professional Dashboard",
    page_icon="https://img.icons8.com/ios-filled/50/ffffff/steam.png",
    layout="wide"
)


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

 
def init_user_files(): #Inicializa los archivos CSV para usuarios y favoritos si no existen, creando estructuras vacías con las columnas necesarias para almacenar la información de cuentas y preferencias de los usuarios.
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
LANGUAGE_CODE_TO_NAME = {v: k for k, v in LANGUAGE_CODES.items()} #Diccionario inverso para mapear códigos de idioma a nombres legibles, útil para mostrar el idioma seleccionado en la interfaz de usuario de manera amigable.
TRANSLATIONS = {
    "es": {
        "language_label": "Idioma",
        "account": "Cuenta",
        "mode": "Modo",
        "user": "Usuario",
        "password": "Contraseña",
        "create_account": "Crear Cuenta",
        "login": "Iniciar Sesión",
        "register": "Registrarse",
        "logout": "Cerrar sesión",
        "my_favorites": "Mis Favoritos",
        "navigation": "Navegación",
        "select_date": "Seleccionar fecha:",
        "home_dashboard": "Inicio",
        "update_data": "Actualizar Datos",
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
        "please_login_favorites": "Por favor, inicia sesión para revisar tus favoritos.",
        "favorites_empty": "Tu lista de favoritos está vacía.",
        "saved": "Guardado:",
        "already_in_favorites": "Ya está en favoritos",
        "remove": "Eliminar",
        "view_info": "Ver Información",
        "details": "Detalles",
        "favorite": "Favorito",
        "toggle_top": "Alternar Top 10 / 100",
        "players_online": "Jugadores en Línea",
        "games_tracked": "Juegos Seguimiento",
        "top_game": "Mejor Juego",
        "welcome": "Bienvenido",
        "price": "Precio",
        "free_to_play": "Gratis para jugar",
        "market_trends_title": "Tendencias y ventas",
        "genre_popularity_title": "Popularidad de géneros",
        "top_developers_title": "Mejores desarrolladores",
        "popular_releases_title": "Populares",
        "price_analysis_title": "Análisis de precios",
        "historical_trends_header": "Tendencias históricas y cuota de mercado",
        "market_share": "Cuota de mercado",
        "volatility": "Volatilidad",
        "peak_24h_section": "Pico 24h",
        "dashboard_title": "Dashboard",
        "live_rankings": "Clasificación en vivo",
        "performance_trend": "Tendencia de rendimiento",
        "data_explorer": "Explorador de datos",
        "compare_games": "Comparar juegos:",
        "filters_title": "Filtros de juegos",
        "name_filter": "Juego",
        "genre_filter": "Género",
        "developer_filter": "Desarrollador",
        "platform_filter": "Plataforma",
        "price_range": "Rango de precio",
        "players_range": "Rango de jugadores",
        "filtered_results": "**Resultados:**",
        "fallback_to_top": "Mostrando todos los juegos porque no hubo coincidencias exactas.",
        "no_filtered_results": "No hay juegos que cumplan esos filtros.",
        "select_at_least_one_game": "Selecciona al menos un juego para comparar",
        "no_weekly_data": "No hay datos suficientes para la última semana con los juegos seleccionados.",
        "data_date": "Fecha de datos:",
        "no_24h_data": "No hay datos disponibles para las últimas 24 horas.",
        "popular_releases_description": "Un juego se considera popular si su pico de jugadores en la última semana supera al pico semanal de otros juegos lanzados en fechas similares (más o menos 7 días).",
        "future_trending": "Tendencias a futuro",
        "future_trending_title": "Tendencias a futuro",
        "future_trending_description": "Proyección de los juegos con mayor potencial ascendente usando el Trend Score.",
        "copyright": "© 2026 infosteam — Monitorización de datos de alto nivel",
        "release_date": "Fecha de lanzamiento",
        "weekly_peak": "Pico última semana",
        "game_details": "Detalles del juego",
        "watch_trailer_on_steam": "Ver tráiler en Steam",
        "watch_live_streams_of": "Ver streams en vivo de {game_name}",
        "overview_tab": "Resumen",
        "details_tab": "Detalles",
        "reviews_tab": "Reseñas",
        "information": "Información",
        "release_information": "Información de lanzamiento",
        "about_game": "Acerca del juego",
        "trailer": "Trailer",
        "twitch_streams": "Streams en Vivo",
        "developer_label": "Desarrollador",
        "platforms_label": "Plataformas",
        "genres_label": "Géneros",
        "rating_label": "Rating",
        "reviews_label": "Reseñas",
        "trend_formula_title": "Fórmula de tendencia",
        "trend_formula_description": "Puntuación estimada para proyectar la evolución de cada juego.",
        "trend_formula_equation": "Trend Score = (Pico última semana * 0.6) + (Crecimiento 7d * 0.3) + (Recencia * 0.1)",
        "trend_formula_note": "Valores más altos indican una mayor probabilidad de alza en la próxima semana.",
        "trend_forecast_title": "Tendencias",
        "trend_forecast_description": "Clasificación de juegos según el score de tendencia calculado.",
        "trend_forecast_chart": "Top juegos por Trend Score",
        "current_rank": "Posición actual",
        "current_players": "Jugadores actuales",
        "peak_24h": "Pico 24h",
        "open_steam": "Abrir en Steam",
        "open_twitch": "Ver en Twitch",
        "added_to_favorites": "Añadido a favoritos",
        "add_to_favorites": "Añadir a favoritos",
        "remove_from_favorites": "Quitar de favoritos",
        "summary_hint": "Este resumen usa las valoraciones y el número de reseñas del conjunto de datos para describir el juego seleccionado.",
    },
    "en": {
        "language_label": "Language",
        "account": "Account",
        "mode": "Mode",
        "user": "User",
        "password": "Password",
        "create_account": "Create Account",
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "my_favorites": "My Favorites",
        "navigation": "Navigation",
        "select_date": "Select Date:",
        "home_dashboard": "Home",
        "update_data": "Update Data",
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
        "remove": "Remove",
        "view_info": "View Info",
        "details": "Details",
        "favorite": "Favorite",
        "toggle_top": "Toggle Top 10 / 100",
        "players_online": "Players Online",
        "games_tracked": "Games Tracked",
        "top_game": "Top Game",
        "welcome": "Welcome",
        "price": "Price",
        "free_to_play": "Free to Play",
        "market_trends_title": "Market Trends & Sales",
        "genre_popularity_title": "Genre Popularity",
        "top_developers_title": "Top Developers",
        "popular_releases_title": "Popular Releases",
        "price_analysis_title": "Price Analysis",
        "historical_trends_header": "Historical Trends & Market Share",
        "market_share": "Market Share",
        "volatility": "Volatility",
        "peak_24h_section": "24h Peak Players",
        "dashboard_title": "Dashboard",
        "live_rankings": "Live Rankings",
        "performance_trend": "Performance Trend",
        "data_explorer": "Data Explorer",
        "compare_games": "Compare Games:",
        "filters_title": "Game Filters",
        "name_filter": "Game",
        "genre_filter": "Genre",
        "developer_filter": "Developer",
        "platform_filter": "Platform",
        "price_range": "Price range",
        "players_range": "Players range",
        "filtered_results": "**Results:**",
        "fallback_to_top": "Showing all games because no exact matches were found.",
        "no_filtered_results": "No games match these filters.",
        "select_at_least_one_game": "Select at least one game to compare",
        "no_weekly_data": "Not enough weekly data for the selected games.",
        "data_date": "Data date:",
        "no_24h_data": "No data available for the latest 24 hours.",
        "popular_releases_description": "A game is considered popular if its weekly peak players exceed the weekly peak of other games released on similar dates (plus or minus 7 days).",
        "future_trending": "Future Trending",
        "future_trending_title": "Future Trending",
        "future_trending_description": "Projected games with the highest upward potential using the Trend Score.",
        "copyright": "© 2026 infosteam — High-End Data Monitoring",
        "release_date": "Release Date",
        "weekly_peak": "Weekly peak",
        "game_details": "Game Details",
        "watch_trailer_on_steam": "Watch Trailer on Steam",
        "watch_live_streams_of": "Watch live streams of {game_name}",
        "overview_tab": "Overview",
        "details_tab": "Details",
        "reviews_tab": "Reviews",
        "information": "Information",
        "release_information": "Release Information",
        "about_game": "About This Game",
        "trailer": "Trailer",
        "twitch_streams": "Live Streams",
        "developer_label": "Developer",
        "platforms_label": "Platforms",
        "genres_label": "Genres",
        "rating_label": "Rating",
        "reviews_label": "Reviews",
        "trend_formula_title": "Trend Formula",
        "trend_formula_description": "Estimated score to project how each game may evolve.",
        "trend_formula_equation": "Trend Score = (Weekly Peak * 0.6) + (7d Growth * 0.3) + (Recency * 0.1)",
        "trend_formula_note": "Higher values indicate a stronger upward trajectory next week.",
        "trend_forecast_title": "Trends",
        "trend_forecast_description": "Rank games by their computed trend score.",
        "trend_forecast_chart": "Top games by Trend Score",
        "current_rank": "Current Rank",
        "current_players": "Current Players",
        "peak_24h": "24h Peak",
        "open_steam": "Open in Steam",
        "open_twitch": "Watch on Twitch",
        "added_to_favorites": "Added to favorites",
        "add_to_favorites": "Add to favorites",
        "remove_from_favorites": "Remove from favorites",
        "summary_hint": "This summary uses the rating and review counts from the dataset to describe the selected game.",
    },
    "fr": {
        "language_label": "Langue",
        "account": "Compte",
        "mode": "Mode",
        "user": "Utilisateur",
        "password": "Mot de passe",
        "create_account": "Créer un compte",
        "login": "Connexion",
        "register": "S'inscrire",
        "logout": "Déconnexion",
        "my_favorites": "Mes Favoris",
        "navigation": "Navigation",
        "select_date": "Sélectionner la date:",
        "home_dashboard": "Accueil",
        "update_data": "Mettre à jour",
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
        "remove": "Supprimer",
        "view_info": "Voir Infos",
        "details": "Détails",
        "favorite": "Favori",
        "toggle_top": "Basculer Top 10 / 100",
        "players_online": "Joueurs en ligne",
        "games_tracked": "Jeux suivis",
        "top_game": "Meilleur jeu",
        "welcome": "Bienvenue",
        "price": "Prix",
        "free_to_play": "Gratuit",
        "market_trends_title": "Tendances et ventes",
        "genre_popularity_title": "Popularité des genres",
        "top_developers_title": "Meilleurs développeurs",
        "popular_releases_title": "Sorties Populaires",
        "price_analysis_title": "Analyse des prix",
        "historical_trends_header": "Tendances historiques et part de marché",
        "market_share": "Part de marché",
        "volatility": "Volatilité",
        "peak_24h_section": "Pic 24h",
        "dashboard_title": "Tableau de bord",
        "live_rankings": "Classement en direct",
        "performance_trend": "Tendance de performance",
        "data_explorer": "Explorateur de données",
        "compare_games": "Comparer les jeux:",
        "filters_title": "Filtres de jeu",
        "name_filter": "Jeu",
        "genre_filter": "Genre",
        "developer_filter": "Développeur",
        "platform_filter": "Plateforme",
        "price_range": "Plage de prix",
        "players_range": "Plage de joueurs",
        "filtered_results": "**Résultats:**",
        "fallback_to_top": "Affichage de tous les jeux car aucune correspondance exacte n'a été trouvée.",
        "no_filtered_results": "Aucun jeu ne correspond à ces filtres.",
        "select_at_least_one_game": "Sélectionnez au moins un jeu à comparer",
        "no_weekly_data": "Pas assez de données hebdomadaires pour les jeux sélectionnés.",
        "data_date": "Date des données :",
        "no_24h_data": "Aucune donnée disponible pour les dernières 24 heures.",
        "popular_releases_description": "Un jeu est considéré comme populaire si son pic de joueurs hebdomadaire dépasse celui des autres jeux sortis à des dates similaires (plus ou moins 7 jours).",
        "copyright": "© 2026 infosteam — Surveillance de données haut de gamme",
        "release_date": "Date de suite",
        "weekly_peak": "Pic hebdomadaire",
        "game_details": "Détails du jeu",
        "watch_trailer_on_steam": "Regarder la bande-annonce sur Steam",
        "watch_live_streams_of": "Voir les streams en direct de {game_name}",
        "overview_tab": "Aperçu",
        "details_tab": "Détails",
        "reviews_tab": "Avis",
        "information": "Informations",
        "release_information": "Informations de sortie",
        "about_game": "À propos du jeu",
        "trailer": "Bande-annonce",
        "twitch_streams": "Streams en Direct",
        "developer_label": "Développeur",
        "platforms_label": "Plataformes",
        "genres_label": "Genres",
        "rating_label": "Note",
        "reviews_label": "Avis",
        "trend_formula_title": "Formule de tendance",
        "trend_formula_description": "Score estimé pour projeter l'évolution de cada jeu.",
        "trend_formula_equation": "Score de tendance = (Pic hebdo * 0.6) + (Croissance 7j * 0.3) + (Récence * 0.1)",
        "trend_formula_note": "Les valeurs plus élevées indiquent une trajectoire ascendante plus probable.",
        "future_trending": "Tendance future",
        "future_trending_title": "Tendance future",
        "future_trending_description": "Jeux projetés avec le plus fort potentiel de hausse selon le Trend Score.",
        "trend_forecast_title": "Tendances",
        "trend_forecast_description": "Classement des jeux par leur score de tendance calculé.",
        "trend_forecast_chart": "Top jeux par Trend Score",
        "current_rank": "Rang actuel",
        "current_players": "Joueurs actuels",
        "peak_24h": "Pic 24h",
        "open_steam": "Ouvrir sur Steam",
        "open_twitch": "Voir sur Twitch",
        "added_to_favorites": "Ajouté aux favoris",
        "add_to_favorites": "Ajouter aux favoris",
        "remove_from_favorites": "Retirer des favoris",
        "summary_hint": "Ce résumé utilise les notes et le nombre d'avis du jeu dans l'ensemble de données para décrire le jeu sélectionné.",
    },
    "pt": {
        "language_label": "Idioma",
        "account": "Conta",
        "mode": "Modo",
        "user": "Usuário",
        "password": "Senha",
        "create_account": "Criar conta",
        "login": "Entrar",
        "register": "Registrar",
        "logout": "Sair",
        "my_favorites": "Meus Favoritos",
        "navigation": "Navegação",
        "select_date": "Selecionar data:",
        "home_dashboard": "Início",
        "update_data": "Atualizar Dados",
        "dashboard": "Painel",
        "market_trends": "Tendências",
        "top_genres": "Principais Gêneros",
        "top_developers": "Principais Desenvolvedores",
        "price_analysis": "Análise de Preços",
        "popular_releases": "Lançamentos Populares",
        "favorites": "Favoritos",
        "user_exists": "O usuário ya existe!",
        "user_registered": "Usuário registrado!",
        "wrong_credentials": "Credenciales incorretas",
        "please_login_favorites": "Por favor faça login para ver seus favoritos.",
        "favorites_empty": "Sua lista de favoritos está vazia.",
        "saved": "Salvo:",
        "already_in_favorites": "Já está nos favoritos",
        "remove": "Remover",
        "view_info": "Ver Informações",
        "details": "Detalhes",
        "favorite": "Favorito",
        "toggle_top": "Alternar Top 10 / 100",
        "players_online": "Jogadores Online",
        "games_tracked": "Jogos Monitorados",
        "top_game": "Melhor Jogo",
        "welcome": "Bem-vindo",
        "price": "Preço",
        "free_to_play": "Grátis para jogar",
        "market_trends_title": "Tendências e vendas",
        "genre_popularity_title": "Popularidade de gêneros",
        "top_developers_title": "Principais desenvolvedores",
        "popular_releases_title": "Lançamentos populares",
        "price_analysis_title": "Análise de preços",
        "historical_trends_header": "Tendências históricas e participação de mercado",
        "market_share": "Participação de mercado",
        "volatility": "Volatilidade",
        "peak_24h_section": "Pico 24h",
        "dashboard_title": "Painel",
        "live_rankings": "Classificação ao vivo",
        "performance_trend": "Tendência de desempenho",
        "data_explorer": "Explorador de dados",
        "compare_games": "Comparar jogos:",
        "filters_title": "Filtros de jogos",
        "name_filter": "Jogo",
        "genre_filter": "Gênero",
        "developer_filter": "Desenvolvedor",
        "platform_filter": "Plataforma",
        "price_range": "Intervalo de preço",
        "players_range": "Intervalo de jogadores",
        "filtered_results": "**Resultados:**",
        "fallback_to_top": "Mostrando todos os jogos porque não houve correspondências exatas.",
        "no_filtered_results": "Nenhum jogo corresponde a esses filtros.",
        "select_at_least_one_game": "Selecione pelo menos um jogo para comparar",
        "no_weekly_data": "Não há dados semanais suficientes para os jogos selecionados.",
        "data_date": "Data dos dados:",
        "no_24h_data": "Nenhum dado disponível para as últimas 24 horas.",
        "popular_releases_description": "Um jogo é considerado popular se seu pico semanal de jogadores for maior que o pico semanal de outros jogos lançados em datas similares (mais o menos 7 dias).",
        "copyright": "© 2026 infosteam — Monitoramento de dados de alto nível",
        "release_date": "Data de lançamento",
        "weekly_peak": "Pico semanal",
        "game_details": "Detalhes do jogo",
        "watch_trailer_on_steam": "Ver trailer no Steam",
        "watch_live_streams_of": "Assistir streams ao vivo de {game_name}",
        "overview_tab": "Visão geral",
        "details_tab": "Detalhes",
        "reviews_tab": "Avaliações",
        "information": "Informações",
        "release_information": "Informações de lançamento",
        "about_game": "Sobre este jogo",
        "trailer": "Trailer",
        "twitch_streams": "Streams ao Vivo",
        "developer_label": "Desenvolvedor",
        "platforms_label": "Plataformas",
        "genres_label": "Gêneros",
        "rating_label": "Avaliação",
        "reviews_label": "Avaliações",
        "trend_formula_title": "Fórmula de tendência",
        "trend_formula_description": "Pontuação estimada para projetar a evolução de cada jogo.",
        "trend_formula_equation": "Trend Score = (Pico Semanal * 0.6) + (Crecimento 7d * 0.3) + (Recência * 0.1)",
        "trend_formula_note": "Valores maiores indicam uma tendência de alta mais forte.",
        "future_trending": "Tendência futura",
        "future_trending_title": "Tendência futura",
        "future_trending_description": "Jogos projetados com maior potencial de alta usando o Trend Score.",
        "trend_forecast_title": "Tendências",
        "trend_forecast_description": "Rankeie os jogos pelo score de tendência calculado.",
        "trend_forecast_chart": "Top jogos por Trend Score",
        "current_rank": "Posição atual",
        "current_players": "Jogadores atuais",
        "peak_24h": "Pico 24h",
        "open_steam": "Abrir no Steam",
        "open_twitch": "Ver no Twitch",
        "added_to_favorites": "Adicionado aos favoritos",
        "add_to_favorites": "Adicionar aos favoritos",
        "remove_from_favorites": "Remover dos favoritos",
        "summary_hint": "Este resumo usa as classificações e o número de avaliações do conjunto de datos para descrever o jogo selecionado.",
    },
}
CURRENCY_CONFIG = {
    "es": {"symbol": "€", "rate": 0.92},
    "fr": {"symbol": "€", "rate": 0.92},
    "pt": {"symbol": "€", "rate": 0.92},
    "en": {"symbol": "$", "rate": 1.00},
}
def get_currency_config(lang): #Devuelve la configuración de moneda (símbolo y tasa de conversión) para el idioma especificado, con un valor predeterminado para inglés si el idioma no está definido en la configuración.
    return CURRENCY_CONFIG.get(lang, CURRENCY_CONFIG["en"]) #Devuelve la configuración de moneda (símbolo y tasa de conversión) para el idioma especificado, con un valor predeterminado para inglés si el idioma no está definido en la configuración.

def format_local_price(price_str, lang):
    val_usd = convert_to_usd_numeric(price_str)
    t = get_translations(lang)
    if val_usd == 0.0:
        return t["free_to_play"]
    cfg = get_currency_config(lang)
    amount = val_usd * cfg["rate"]
    return f"{cfg['symbol']}{amount:,.2f}" #Formatea el precio local con el símbolo de moneda y dos decimales, usando comas como separadores de miles.

def get_translations(lang):
    return TRANSLATIONS.get(lang, TRANSLATIONS["es"])


def encrypt_password(password):
    """Encrypt password using base64 encoding"""
    if not password:
        return ""
    try:
        
        password_bytes = password.encode('utf-8')
        encoded_bytes = base64.b64encode(password_bytes)
        return encoded_bytes.decode('utf-8')
    except:
        return password  

def decrypt_password(encrypted_password): 
    """Decrypt password from base64 encoding"""
    if not encrypted_password: #Si la contraseña cifrada está vacía o es None, devuelve una cadena vacía para evitar errores al intentar decodificar un valor no válido.
        return ""
    try:
        
        encrypted_bytes = encrypted_password.encode('utf-8') #Convierte la contraseña cifrada de una cadena a bytes utilizando UTF-8, preparando el valor para la decodificación base64.
        decoded_bytes = base64.b64decode(encrypted_bytes)
        return decoded_bytes.decode('utf-8')
    except:
        return encrypted_password 

 
def fix_nan(val, default="-"): #Si el valor es NaN, una cadena vacía o la cadena "nan" (ignorando mayúsculas), devuelve un valor predeterminado (por defecto "-"). De lo contrario, devuelve el valor convertido a cadena. Esto es útil para limpiar datos antes de mostrarlos en la interfaz de usuario.
    if pd.isna(val) or str(val).lower() == "nan" or str(val).strip() == "":
        return default
    return str(val)

def convert_to_usd_numeric(price_str):
    if pd.isna(price_str) or str(price_str).lower() == "nan":
        return 0.0
    p = str(price_str).upper()
    if re.search(r"\b(GRATIS|FREE)\b", p):
        return 0.0
    try:
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", p.replace(',', '.')) #Busca números en la cadena de precio, permitiendo tanto puntos como comas como separadores decimales, y devuelve el primer número encontrado como valor numérico. Si no se encuentran números, devuelve 0.0.
        if not nums:
            return 0.0
        val = float(nums[0])
        if val == 0.0:
            return 0.0
        rates = {"€": 1.08, "฿": 0.028, "РУБ": 0.011, "AED": 0.27, "CLP": 0.0011, "CDN$": 0.74, "¥": 0.0067} #Diccionario de símbolos de moneda y sus tasas de conversión aproximadas a USD para convertir precios que pueden estar en diferentes monedas a un valor numérico en dólares.
        for s, r in rates.items():
            if s in p:
                return val * r
        return val
    except:
        return 0.0

def normalize_genre_token(token): #Normaliza un token de género eliminando espacios, caracteres especiales y aplicando reemplazos específicos para estandarizar los nombres de géneros, devolviendo None para tokens vacíos o no significativos.
    if pd.isna(token):
        return None
    token_text = str(token).strip()
    if not token_text:
        return None
    token_text = re.sub(r"[\|/;]+", ",", token_text) #Reemplaza cualquier secuencia de caracteres delimitadores (barra vertical, barra o punto y coma) por una coma para estandarizar la separación de géneros, lo que facilita la posterior división en tokens individuales.
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
    return token_text #Devuelve el token de género normalizado, o None si el token es considerado vacío, no significativo o está en la lista de reemplazos que indican que no es un género válido.

def get_genre_tokens(genre_text):
    if pd.isna(genre_text):
        return []
    tokens = []
    for raw in re.split(r"[;,|/]+", str(genre_text)): #Divide la cadena de texto de géneros en tokens individuales utilizando una expresión regular que permite múltiples delimitadores (punto y coma, barra vertical, barra o coma), luego normaliza cada token y lo agrega a la lista de tokens si no es None.
        normalized = normalize_genre_token(raw)
        if normalized:
            tokens.append(normalized)
    return tokens

def format_usd(price_str):
    val = convert_to_usd_numeric(price_str)
    return "Free to Play" if val == 0.0 else f"${round(val, 2)}"

def get_game_image(appid):
    """Get game image with multiple fallback options"""
    try:
        aid = int(float(appid)) #Intenta convertir el appid a un número entero para asegurarse de que es un valor válido antes de intentar acceder a la imagen de Steam. Si el appid no es un número válido o es menor o igual a cero, devuelve una imagen de respaldo genérica para juegos.
        if aid <= 0:
            return get_fallback_game_image()
        return f"https://cdn.akamai.steamstatic.com/steam/apps/{aid}/header.jpg" #Intenta obtener la imagen del juego desde Steam usando el appid, pero si el appid no es válido o si la imagen no existe, devuelve una imagen de respaldo genérica para juegos.
    except:
        return get_fallback_game_image()

def normalize_game_name(game_name):
    if not game_name:
        return ""
    name = str(game_name).strip().lower()
    return re.sub(r"[^a-z0-9\s]", "", name) #Normaliza el nombre del juego convirtiéndolo a minúsculas, eliminando espacios al principio y al final, y eliminando caracteres especiales, dejando solo letras, números y espacios. Esto ayuda a estandarizar los nombres de juegos para comparaciones y búsquedas más consistentes.


def normalize_game_name_compact(game_name):
    return normalize_game_name(game_name).replace(" ", "") #Crea una versión compacta del nombre del juego eliminando todos los espacios después de normalizarlo, lo que permite comparaciones aún más flexibles al ignorar completamente los espacios entre palabras.


def get_special_game_image(game_name):
    normalized = normalize_game_name(game_name)
    compact = normalize_game_name_compact(game_name)
    for key, image_url in GAME_IMAGE_OVERRIDES.items(): #Busca en las claves de GAME_IMAGE_OVERRIDES si alguna de ellas está presente en el nombre normalizado o compactado del juego. Si encuentra una coincidencia, devuelve la URL de la imagen correspondiente. Esto permite asignar imágenes específicas a ciertos juegos basándose en palabras clave en sus nombres.
        if key in normalized or key in compact:
            return image_url
    return None


def should_skip_steam_image(game_name):
    normalized = normalize_game_name(game_name) #Normaliza el nombre del juego eliminando caracteres especiales y convirtiéndolo a minúsculas para facilitar la detección de palabras clave que indican que no se debe usar la imagen de Steam, lo que es útil para juegos que pueden no tener imágenes disponibles o para evitar imágenes genéricas.
    compact = normalize_game_name_compact(game_name) #Normaliza el nombre del juego tanto en una versión con espacios como en una versión compacta sin espacios para facilitar la detección de palabras clave que indican que no se debe usar la imagen de Steam, lo que es útil para juegos que pueden no tener imágenes disponibles o para evitar imágenes genéricas.
    return any(token in normalized or token in compact for token in NON_STEAM_IMAGE_TOKENS) #Determina si se debe omitir la imagen de Steam para un juego verificando si el nombre del juego contiene alguna de las palabras clave definidas en NON_STEAM_IMAGE_TOKENS. Si alguna de estas palabras clave está presente en el nombre normalizado o compactado del juego, devuelve True, indicando que se debe usar una imagen de respaldo en lugar de la imagen de Steam, lo que es útil para juegos que no tienen imágenes disponibles en Steam o para evitar imágenes genéricas que no representan bien el juego.


@st.cache_data(ttl=86400) #Caché de la función para verificar si la imagen de Steam existe, con un tiempo de vida de 24 horas para evitar hacer demasiadas solicitudes a Steam y mejorar el rendimiento al reutilizar resultados anteriores.
def steam_image_exists(appid):
    try:
        aid = int(float(appid)) #Intenta convertir el appid a un número entero para asegurarse de que es un valor válido antes de intentar acceder a la imagen de Steam. Si el appid no es un número válido o es menor o igual a cero, devuelve False, indicando que la imagen de Steam no existe para ese appid.
        if aid <= 0:
            return False
        import requests
        url = f"https://cdn.akamai.steamstatic.com/steam/apps/{aid}/header.jpg"
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except:
        return False


@st.cache_data(ttl=86400) #Caché de la función para verificar si el video de Steam existe, con un tiempo de vida de 24 horas para evitar hacer demasiadas solicitudes a Steam y mejorar el rendimiento al reutilizar resultados anteriores.
def steam_video_exists(appid):
    try:
        aid = int(float(appid))
        if aid <= 0:
            return False
        import requests
        
        url = f"https://store.steampowered.com/api/appdetails?appids={aid}" #Hace una solicitud a la API de Steam para obtener los detalles del juego utilizando el appid, y luego verifica si la respuesta contiene información sobre videos (trailers) para ese juego. Si se encuentra un video válido, devuelve la URL del video; de lo contrario, devuelve False, indicando que no hay un video disponible para ese appid.
        response = requests.get(url, timeout=10)
        data = response.json()
        if str(aid) in data and data[str(aid)]['success']:
            app_data = data[str(aid)]['data']
            if 'movies' in app_data and len(app_data['movies']) > 0:
                
                first_movie = app_data['movies'][0]
                if 'hls_h264' in first_movie: #Verifica si el primer video tiene una URL de video en formato HLS (hls_h264) y, si es así, devuelve esa URL para que pueda ser utilizada como el trailer del juego. Si no se encuentra un video válido, devuelve False.
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
    
    game_placeholders = [
        "https://images.unsplash.com/photo-1556438064-2d7646166914?w=460&h=215&fit=crop",  # Gaming setup
        "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=460&h=215&fit=crop",  # Controller
        "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=460&h=215&fit=crop",  # Gaming mouse
        "https://images.unsplash.com/photo-1593305841991-05c297ba4575?w=460&h=215&fit=crop",  # VR headset
        "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=460&h=215&fit=crop",  # Game characters
        "https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=460&h=215&fit=crop",  # Gaming room
        "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=460&h=215&fit=crop",  # RGB keyboard
        "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=460&h=215&fit=crop",  # Game controller
        "https://images.unsplash.com/photo-1556438064-2d7646166914?w=460&h=215&fit=crop",  # Gaming PC
        "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=460&h=215&fit=crop",  # Controller closeup
        "https://images.unsplash.com/photo-1560419015-7c427e8ae5ba?w=460&h=215&fit=crop",  # Gaming chair
        "https://images.unsplash.com/photo-1592478411213-6153e4ebc696?w=460&h=215&fit=crop",  # Multiplayer gaming
        "https://images.unsplash.com/photo-1556438064-2d7646166914?w=460&h=215&fit=crop",  # Gaming setup 2
        "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=460&h=215&fit=crop",  # Esports
        "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=460&h=215&fit=crop",  # Mechanical keyboard
    ]

    
    import random
    return random.choice(game_placeholders) #Devuelve una imagen de respaldo aleatoria de la lista de game_placeholders para usar cuando la imagen de Steam no esté disponible, proporcionando una variedad de imágenes relacionadas con juegos para mejorar la apariencia visual de la aplicación incluso cuando no se pueden obtener imágenes específicas de los juegos desde Steam.


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

def get_game_background(appid): #Intenta obtener la imagen de fondo del juego desde Steam utilizando el appid, pero si el appid no es válido o si la imagen no existe, devuelve una imagen de respaldo genérica para juegos.
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

def get_ai_response(user_input, game_data): #Devuelve una respuesta de estilo IA segura utilizando los datos conocidos del juego.
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
        response_lines.append("This game appears to have the listed price and may be free to play depending on the store listing.") #Agrega una línea adicional a la respuesta si el usuario pregunta sobre el precio, indicando que el juego tiene el precio listado y que puede ser gratuito dependiendo de la tienda, lo que proporciona información útil sin hacer afirmaciones específicas sobre promociones o descuentos actuales.
    elif "rating" in user_input.lower() or "review" in user_input.lower():
        response_lines.append("The rating and reviews are based on the current dataset and may vary over time.")
    return "\n".join(response_lines)

def generate_review_snippets(game_name, rating, reviews):
    """Generate example review bullets from available rating and review count."""
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

def format_game_name_for_twitch(game_name):
    """Format game name for Twitch URL"""
    if not game_name:
        return ""
   
    import re
    import urllib.parse #Importa el módulo re para usar expresiones regulares y urllib.parse para codificar el nombre del juego de manera segura en una URL, asegurándose de que los caracteres especiales se manejen correctamente al generar enlaces a Twitch.
    
    clean_name = re.sub(r'[^\w\s-]', '', game_name).strip()
    
    return urllib.parse.quote(clean_name)


def get_platform_icons(platforms_str):
    """Convert platform string to visual text without icons"""
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


def display_platforms_section(appid, lang): 
    """Display platforms in an attractive card format"""
    t = get_translations(lang) 

    
    platforms_data = df_plataformas[df_plataformas["AppID"] == appid]
    if not platforms_data.empty:
        platforms_str = platforms_data["Plataformas"].iloc[0] #Obtiene la cadena de plataformas para el juego con el appid dado desde el DataFrame df_plataformas. Si se encuentra una fila correspondiente, extrae la información de plataformas; de lo contrario, se considera que no hay datos disponibles para las plataformas del juego.
        platforms_display = get_platform_icons(platforms_str)
    else:
        platforms_display = "No disponible"

    return platforms_display


def get_enhanced_game_background(appid, game_name=None):
    """Enhanced background getter that tries multiple sources"""
    try:
       
        aid = int(float(appid)) if appid and str(appid).strip() else 0 #Intenta convertir el appid a un número entero para asegurarse de que es un valor válido antes de intentar acceder a la imagen de fondo de Steam. Si el appid no es un número válido o es menor o igual a cero, devuelve una imagen de fondo de respaldo genérica para juegos.

        
        skip_steam_games = [
            'fivem', 'fife', 'gta v fivem', 'grand theft auto v fivem',
            'multiplayer', 'server', 'custom', 'mod'
        ]

        should_check_steam = True
        if game_name and any(skip.lower() in game_name.lower() for skip in skip_steam_games): #Si el nombre del juego contiene alguna de las palabras clave definidas en skip_steam_games (como "fivem", "multiplayer", "server", etc.), se establece should_check_steam en False para indicar que no se debe intentar obtener la imagen de fondo de Steam, lo que es útil para juegos que son modificaciones, servidores personalizados o juegos multijugador que pueden no tener imágenes de fondo representativas en Steam.
            should_check_steam = False
        elif aid <= 0 or aid > 99999999:  
            should_check_steam = False

        
        if should_check_steam and steam_image_exists(appid):
            steam_bg = f"https://cdn.akamai.steamstatic.com/steam/apps/{aid}/page_bg_generated_v6b.jpg"
            return steam_bg

    except Exception as e:
       
        pass

    
    return get_fallback_game_background()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #Determina el directorio base del proyecto al obtener la ruta absoluta del archivo actual, luego subir un nivel para llegar al directorio raíz del proyecto. Esto es útil para construir rutas relativas a los archivos de datos y scripts dentro del proyecto de manera consistente, independientemente de dónde se ejecute el código.
CLEAN_DIR = os.path.join(BASE_DIR, "Clean") #Construye la ruta al directorio "Clean" dentro del directorio base del proyecto, donde se espera que se encuentren los archivos CSV limpios con los datos de juegos. Esta ruta se utiliza para cargar los datos en los DataFrames de pandas y para acceder a los archivos necesarios para la aplicación.
SRC_DIR = os.path.join(BASE_DIR, "Src")
DOWNLOAD_SCRIPT = os.path.join(SRC_DIR, "download.py")



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


def update_data_source():
    """Run the external download script and clear cached data on success."""
    try: #Ejecuta el script de descarga externo para actualizar los datos, capturando la salida y los errores. Si el script se ejecuta correctamente (código de retorno 0), borra la caché de datos para forzar la recarga de los nuevos datos actualizados. Si el script falla o si ocurre un error, devuelve un mensaje de error apropiado.
        result = subprocess.run(
            [sys.executable, DOWNLOAD_SCRIPT],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=180
        )
        if result.returncode != 0:
            return False, result.stderr.strip() or result.stdout.strip() or "Error al ejecutar la actualización."
        load_data.clear()
        return True, result.stdout.strip()
    except subprocess.TimeoutExpired as e:
        return False, f"Tiempo de actualización agotado después de {e.timeout} segundos."
    except Exception as e:
        return False, str(e) #Devuelve el mensaje de error como una cadena, lo que permite mostrar información útil sobre lo que salió mal durante la actualización de los datos, ya sea un error específico del proceso o cualquier otra excepción que pueda ocurrir.


def parse_date_safe(value): #Intenta analizar una fecha a partir de una cadena de texto utilizando pandas, primero asumiendo el formato día/mes/año (dayfirst=True) y luego intentando el formato mes/día/año (dayfirst=False) si el primer intento falla. Si ambos intentos fallan o si el valor es NaN, devuelve pd.NaT para indicar que no se pudo analizar la fecha de manera segura.
    try:
        if pd.isna(value):
            return pd.NaT
        parsed = pd.to_datetime(value, dayfirst=True, errors='coerce') #Intenta analizar la fecha asumiendo el formato día/mes/año (dayfirst=True) y, si el análisis falla (errors='coerce' convierte valores no válidos en NaT), intenta nuevamente asumiendo el formato mes/día/año (dayfirst=False). Esto es útil para manejar fechas que pueden estar en diferentes formatos dependiendo de la fuente de datos, aumentando la probabilidad de analizar correctamente las fechas sin errores.
        if pd.isna(parsed):
            parsed = pd.to_datetime(value, dayfirst=False, errors='coerce')
        return parsed
    except Exception:
        return pd.NaT


def get_recent_releases(ref_date, days=30): #Devuelve un DataFrame de juegos que se lanzaron dentro de una ventana de tiempo específica (por defecto, los últimos 30 días) antes de una fecha de referencia dada. Analiza las fechas de lanzamiento de los juegos y filtra aquellos que caen dentro del rango definido por la fecha de referencia y el número de días especificado.
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
    if pd.isna(end_dt) or df_listado.empty: #Si la fecha de referencia no se puede analizar correctamente o si el DataFrame df_listado está vacío, devuelve 0 como el número máximo de jugadores concurrentes en la última semana, lo que indica que no hay datos disponibles para calcular esta métrica.
        return 0
    game_rows = df_listado[df_listado['AppID'] == int(appid)].copy() #Filtra el DataFrame df_listado para obtener solo las filas correspondientes al juego con el appid dado. Si no se encuentran filas para ese appid, devuelve 0, indicando que no hay datos de jugadores concurrentes disponibles para ese juego.
    if game_rows.empty: 
        return 0
    game_rows['__date'] = pd.to_datetime(game_rows['Fecha'], errors='coerce') #Convierte la columna 'Fecha' a un formato de fecha utilizando pandas, lo que permite realizar operaciones de filtrado basadas en fechas. Si alguna fecha no se puede analizar correctamente, se convierte en NaT (Not a Time), lo que facilita la exclusión de filas con fechas no válidas al calcular el número máximo de jugadores concurrentes en la última semana.
    window = game_rows[(game_rows['__date'] > (end_dt - pd.Timedelta(days=7))) & (game_rows['__date'] <= end_dt)]
    if window.empty:
        return 0
    values = pd.to_numeric(window['JugadoresConcurrentes'], errors='coerce').fillna(0) #Convierte la columna 'JugadoresConcurrentes' a valores numéricos, manejando cualquier valor no numérico como NaN y luego llenando esos NaN con 0 para asegurarse de que se puedan calcular correctamente los valores máximos sin errores. Esto es útil para obtener el número máximo de jugadores concurrentes en la última semana, incluso si algunos datos de jugadores concurrentes no son válidos o están ausentes.
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
    return int(values.sum())


def get_previous_week_peak(appid, ref_date):
    end_dt = parse_date_safe(ref_date)
    if pd.isna(end_dt) or df_listado.empty:
        return 0
    game_rows = df_listado[df_listado['AppID'] == int(appid)].copy()
    if game_rows.empty:
        return 0
    game_rows['__date'] = pd.to_datetime(game_rows['Fecha'], errors='coerce')
    prev_window = game_rows[(game_rows['__date'] > (end_dt - pd.Timedelta(days=14))) & (game_rows['__date'] <= (end_dt - pd.Timedelta(days=7)))]
    if prev_window.empty:
        return 0
    values = pd.to_numeric(prev_window['JugadoresConcurrentes'], errors='coerce').fillna(0)
    return int(values.max())


def compute_trend_scores(ref_date, limit=12): #Calcula una puntuación de tendencia para los juegos basándose en su pico de jugadores concurrentes en la última semana, el crecimiento en jugadores concurrentes en los últimos 7 días y la recencia del lanzamiento. Devuelve un DataFrame con los juegos ordenados por su puntuación de tendencia, mostrando solo los mejores resultados según el límite especificado.
    ref_dt = parse_date_safe(ref_date)
    if pd.isna(ref_dt) or df_info.empty:
        return pd.DataFrame()

    rows = []
    for _, row in df_info.iterrows():
        appid = int(row.get('AppID', 0)) if not pd.isna(row.get('AppID', 0)) else 0 #Intenta obtener el appid de la fila actual del DataFrame df_info, asegurándose de que sea un número entero válido. Si el appid no es un número válido o es menor o igual a cero, se establece en 0, lo que indica que no hay un appid válido para ese juego. Esto es útil para evitar errores al calcular las métricas de tendencia para juegos sin un appid válido.
        if appid <= 0:
            continue
        weekly_peak = peak_players_last_week(appid, ref_dt)  
        prev_peak = get_previous_week_peak(appid, ref_dt)
        growth_7d = weekly_peak - prev_peak
        release_dt = parse_date_safe(row.get('Fecha_Lanzamiento'))
        age_days = (ref_dt - release_dt).days if pd.notna(release_dt) else 90
        recency_score = max(0, 30 - age_days)
        score = (weekly_peak * 0.6) + (growth_7d * 0.3) + (recency_score * 0.1)
        rows.append({
            'AppID': appid,
            'Nombre': row.get('Nombre'),
            'Weekly peak': weekly_peak,
            'Growth 7d': growth_7d,
            'Recency': recency_score,
            'Trend Score': round(score, 2),
        })

    df = pd.DataFrame(rows) #Crea un DataFrame a partir de la lista de diccionarios que contienen las métricas calculadas para cada juego, lo que permite ordenar y filtrar los juegos según su puntuación de tendencia.
    if df.empty:
        return df
    return df.sort_values('Trend Score', ascending=False).head(limit).reset_index(drop=True)


def get_latest_release_date():
    if df_info.empty:
        return pd.Timestamp.today()
    dates = df_info['Fecha_Lanzamiento'].apply(parse_date_safe)
    return dates.max()


def get_popular_reference_date(): #Determina la fecha de referencia para calcular los lanzamientos populares, utilizando la fecha de los datos más recientes si hay lanzamientos recientes, o la fecha del último lanzamiento si no hay lanzamientos recientes. Esto asegura que la sección de lanzamientos populares se base en una fecha relevante para los datos disponibles.
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
    for _, row in recent.iterrows(): #Itera sobre las filas del DataFrame de lanzamientos recientes y calcula el pico de jugadores concurrentes en la última semana para cada juego utilizando su appid. Luego, almacena esta información junto con el nombre y la fecha de lanzamiento en una lista de diccionarios, que se convertirá en un nuevo DataFrame para analizar qué lanzamientos son populares en comparación con sus pares lanzados en un período similar.
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

    return df_recent.sort_values(['is_popular', 'peak_last_week'], ascending=[False, False]).reset_index(drop=True) #Ordena el DataFrame de lanzamientos recientes primero por la columna 'is_popular' en orden descendente (colocando los lanzamientos populares al principio) y luego por 'peak_last_week' también en orden descendente (colocando los lanzamientos con mayor pico de jugadores concurrentes en la última semana al principio dentro de cada grupo de popularidad), lo que permite mostrar los lanzamientos más destacados y populares en la parte superior de la lista.


def prepare_popular_releases_display(popular_releases, t): #Prepara el DataFrame de lanzamientos populares para su visualización, filtrando solo los lanzamientos populares y formateando la fecha de lanzamiento para mostrarla de manera legible. Si no hay lanzamientos populares, devuelve un DataFrame vacío con las columnas esperadas para mantener la consistencia en la visualización.
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

        if "user" not in st.session_state:
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
            
            if safe_id is not None and st.button(t.get('add_to_favorites', 'Añadir a favoritos'), key=add_key):
                new_fav = pd.DataFrame([[st.session_state['user'], safe_id]], columns=["username", "appid"])
                pd.concat([f_df, new_fav], ignore_index=True).to_csv(FAV_FILE, index=False)
                st.success(f"{t.get('saved', 'Guardado')} {name}")
                st.rerun()



def render_game_card(aid, name, t, key_prefix, price_raw=None, genres_raw=None, rating=None, reviews=None, rel_dt=None, extra_caption=None): 
    """Render a standardized game card inside the current Streamlit column."""
    title_attr = f"{name}" 
    img_url = get_enhanced_game_image(aid, name)
    
    badge_html = ''
    is_fav = False
    safe_id = safe_appid(aid)
    if "user" in st.session_state and safe_id is not None:
        try:
            f_df = pd.read_csv(FAV_FILE)
            is_fav = ((f_df['username'] == st.session_state['user']) & (f_df['appid'] == safe_id)).any()
        except:
            is_fav = False
        # No emoji badges
        if is_fav:
            badge_html = '<div class="badge pulse" style="position:absolute; right:8px; top:8px; background:#ff6b81; color:#ffffff; padding:4px 8px; border-radius:12px; font-weight:700; font-size:11px;" title="Favorito">FAVORITO</div>'
        else:
            badge_html = '<div class="badge" style="position:absolute; right:8px; top:8px; background:#4b5563; color:#ffffff; padding:4px 8px; border-radius:12px; font-weight:700; font-size:11px;" title="'+t.get('add_to_favorites','Añadir a favoritos')+'">DISPONIBLE</div>'

    overlay_lines = []
    if rel_dt is not None:
        try:
            rel_str = parse_date_safe(rel_dt).strftime('%Y-%m-%d') if not pd.isna(parse_date_safe(rel_dt)) else fix_nan(rel_dt) #Intenta analizar la fecha de lanzamiento y formatearla como una cadena legible. Si el análisis falla o si la fecha es NaN, utiliza la función fix_nan para mostrar un valor adecuado en su lugar. Luego, agrega esta información a las líneas de superposición que se mostrarán sobre la imagen del juego en la tarjeta.
            overlay_lines.append(f"{t['release_date']}: {rel_str}")
        except:
            pass
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
                platforms = display_platforms_section(aid, st.session_state.language) #Obtiene la información de plataformas para el juego utilizando la función display_platforms_section, que a su vez consulta el DataFrame df_plataformas para obtener las plataformas disponibles para el juego con el appid dado. Si se encuentran plataformas disponibles, se agrega esta información a las líneas de superposición que se mostrarán sobre la imagen del juego en la tarjeta, proporcionando a los usuarios información adicional sobre en qué plataformas pueden jugar el juego.
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

    if genres_raw:
        st.write(f"**{t['genres_label']}:** {fix_nan(genres_raw)}")
    if rating is not None:
        st.write(f"**{t['rating_label']}:** {fix_nan(rating)}")
    if reviews is not None and not pd.isna(reviews):
        st.write(f"**{t['reviews_label']}:** {int(pd.to_numeric(reviews, errors='coerce')):,}")

  
    render_card_controls(aid, name, key_prefix, is_fav, t, compact=False)


def render_dashboard_card(aid, name, t, key_prefix, small_image_height=110, badge=None, players=None, peak=None):
    """Render a compact card used in dashboard tabs to differentiate from full navigation views."""
    img_url = get_enhanced_game_image(aid, name)
    
    badge_color = '#ffbf47'
    card_gradient = 'linear-gradient(135deg, #0f1720 0%, #111827 100%)'
    try:
        if badge == 'POP':
            badge_color = '#9b5cff'  
            card_gradient = 'linear-gradient(135deg, #6b21a8 0%, #111827 100%)'
        elif badge == '▲':
            badge_color = '#16a34a'  
            card_gradient = 'linear-gradient(135deg, #052e18 0%, #08301a 100%)'
        elif peak is not None and float(peak) < 0:
            badge_color = '#ef4444'  
            card_gradient = 'linear-gradient(135deg, #2b0f0f 0%, #111827 100%)'
        elif players is not None and int(players) > 100000:
            badge_color = '#f97316'  
            card_gradient = 'linear-gradient(135deg, #3a0f00 0%, #111827 100%)'
    except:
        pass
    pulse_class = ' pulse' if badge == 'POP' else ''
    badge_html = f'<div class="badge{pulse_class}" style="background:{badge_color};">{badge}</div>' if badge else ''
    
    fav_badge_html = ''
    is_fav_dash = False
    safe_id = safe_appid(aid)
    if "user" in st.session_state and safe_id is not None:
        try:
            f_df = pd.read_csv(FAV_FILE)
            is_fav_dash = ((f_df['username'] == st.session_state['user']) & (f_df['appid'] == safe_id)).any()
            if is_fav_dash:
                fav_badge_html = '<div class="badge" style="position:absolute; left:8px; top:8px; background:#ff6b81; color:#ffffff; padding:4px 6px; border-radius:12px; font-weight:700; font-size:9px;" title="Favorito">FAV</div>'
            else:
                fav_badge_html = '<div class="badge" style="position:absolute; left:8px; top:8px; background:#4b5563; color:#ffffff; padding:4px 6px; border-radius:12px; font-weight:700; font-size:9px;" title="'+t.get('add_to_favorites','Añadir a favoritos')+'">ADD</div>'
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
    except:
        pass
    if players is not None:
        overlay_lines.append(f"Jugadores: {int(players):,}")
    if peak is not None:
        overlay_lines.append(f"Pico: {int(peak):,}")
    overlay_html = ''
    if overlay_lines:
        overlay_html = '<div class="dashboard-card__overlay">' + '<br>'.join(overlay_lines[:4]) + '</div>'

    st.markdown(f'<div class="dashboard-card" style="position:relative; height:{small_image_height}px; overflow:hidden; border-radius:8px; background:{card_gradient}; box-shadow:0 6px 18px rgba(0,0,0,0.4);"><img src="{img_url}" onerror=\'this.src="{IMG_ERROR}";\'>{overlay_html}{badge_html}{fav_badge_html}</div>', unsafe_allow_html=True)
    st.markdown(f"**{name}**")
    meta = []
    if players is not None:
        meta.append(f"Jugadores: {int(players):,}")
    if peak is not None:
        meta.append(f"Pico: {int(peak):,}")
    if meta:
        st.caption("  •  ".join(meta))

    render_card_controls(aid, name, key_prefix, is_fav_dash, t, compact=True)


def render_trend_formula_card(t):
    formula_html = f'''
    <div style="background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border-radius:18px; padding:20px; color:#e2e8f0; box-shadow:0 24px 60px rgba(15,23,42,0.35);">
      <div style="font-size:1.1rem; font-weight:700; margin-bottom:10px;">{t['trend_formula_title']}</div>
      <div style="color:#94a3b8; margin-bottom:16px; line-height:1.5;">{t['trend_formula_description']}</div>
      <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(148,163,184,0.18); padding:14px; border-radius:14px; font-family:monospace; font-size:0.95rem; color:#f8fafc; white-space:pre-wrap;">{t['trend_formula_equation']}</div>
      <div style="margin-top:14px; color:#cbd5e1; font-size:0.92rem;">{t['trend_formula_note']}</div>
    </div>
    '''
    st.markdown(formula_html, unsafe_allow_html=True)



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
                
                encrypted_pass = encrypt_password(u_pass)
                new_u = pd.DataFrame([[u_name, encrypted_pass]], columns=["username", "password"])
                pd.concat([users, new_u]).to_csv(USERS_FILE, index=False)
                st.success(t["user_registered"])
    else:
        if st.button(t["login"], width='stretch'):
            users = pd.read_csv(USERS_FILE)
            
            valid_user = None
            for _, user_row in users.iterrows():
                if user_row["username"] == u_name:
                    stored_pass = user_row["password"]
                    
                    encrypted_input = encrypt_password(u_pass)
                    if stored_pass == encrypted_input:
                        valid_user = user_row
                        break
                    
                    elif stored_pass == u_pass:
                        valid_user = user_row
                        
                        users.loc[users["username"] == u_name, "password"] = encrypted_input
                        users.to_csv(USERS_FILE, index=False)
                        break #Si el usuario ingresó la contraseña sin cifrar pero coincide con la contraseña almacenada, se considera una coincidencia válida. En este caso, se actualiza la contraseña almacenada para ese usuario con la versión cifrada de la contraseña ingresada, y luego se guarda el DataFrame actualizado en el archivo CSV. Esto permite que los usuarios que tenían contraseñas almacenadas sin cifrar puedan iniciar sesión y al mismo tiempo mejora la seguridad al cifrar sus contraseñas para futuros inicios de sesión.

            if valid_user is not None:
                st.session_state["user"] = u_name
                st.rerun()
            else:
                st.error(t["wrong_credentials"])
    if "user" in st.session_state:
        st.success(f"Usuario: {st.session_state['user']}")
        if st.button(t["logout"], width='stretch'):
            del st.session_state["user"]
            st.rerun()
        if st.button(t["my_favorites"], width='stretch'):
            st.session_state.view = "Favorites"
            st.rerun()

    st.divider()
    st.markdown(f"### {t['navigation']}")

    if st.button(t["home_dashboard"], width='stretch'):
        st.session_state.selected_game = None
        st.session_state.view = "Dashboard"
        st.rerun()

    
    if st.button("Chat", width='stretch'):
        st.session_state.selected_game = None
        st.session_state.view = "Chat"
        st.rerun()

    st.blank = st.markdown("<br>", unsafe_allow_html=True)

    view_menu_keys = ["Dashboard", "Market Trends", "Popular Releases", "Future Trending", "Top Genres", "Top Developers", "Price Analysis", "Favorites"]
    view_menu_labels = [
        t["dashboard"], t["market_trends"], t["popular_releases"], t["future_trending"],
        t["top_genres"], t["top_developers"], t["price_analysis"], t["favorites"]
    ]
    
    
    current_index = view_menu_keys.index(st.session_state.view) if st.session_state.view in view_menu_keys else 0
    selected_label = st.selectbox("Seleccionar vista", view_menu_labels, index=current_index, label_visibility="collapsed")
    
    
    if st.session_state.view != "Chat" or selected_label != view_menu_labels[current_index]:
        st.session_state.view = view_menu_keys[view_menu_labels.index(selected_label)]

    if not df_listado.empty:
        dates = sorted(df_listado["Fecha"].unique(), reverse=True)
        st.session_state.sel_date = st.selectbox(t["select_date"], dates, index=dates.index(st.session_state.sel_date) if st.session_state.sel_date in dates else 0)

    if st.button(t["update_data"], width='stretch'):
        with st.spinner("Actualizando datos..."):
            success, message = update_data_source()
        if success:
            st.success("Datos actualizados correctamente.")
            st.experimental_rerun()
        else:
            st.error(f"Error al actualizar datos: {message}")


selected_game_id = safe_appid(st.session_state.selected_game) if 'selected_game' in st.session_state else None #Intenta obtener el appid del juego seleccionado en el estado de la sesión, asegurándose de que sea un número entero válido. Si el valor no es un número válido o es None, se establecerá en None, lo que indica que no hay un juego seleccionado con un appid válido. Esto es útil para evitar errores al intentar mostrar los detalles de un juego sin un appid válido.
if selected_game_id:
    appid = selected_game_id
    st.session_state.selected_game = selected_game_id
    g_l = df_listado[df_listado["AppID"] == appid].iloc[0] if not df_listado[df_listado["AppID"] == appid].empty else None
    g_i = df_info[df_info["AppID"] == appid].iloc[0] if not df_info[df_info["AppID"] == appid].empty else pd.Series()
    g_d = df_detalles[df_detalles["AppID"] == appid].iloc[0] if not df_detalles[df_detalles["AppID"] == appid].empty else pd.Series()

    
    g_rank = df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)]["Posicion"].iloc[0] if not df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)].empty else "N/A"
    g_players = df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)]["JugadoresConcurrentes"].iloc[0] if not df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)].empty else "N/A"
    rating = fix_nan(g_d.get('Rating'), 'N/A')
    rating_num = pd.to_numeric(rating, errors='coerce')
    reviews = fix_nan(g_d.get('Reviews'), 'N/A')
    reviews_num = pd.to_numeric(reviews, errors='coerce')
    rank_num = pd.to_numeric(g_rank, errors='coerce')
    players_num = pd.to_numeric(g_players, errors='coerce')

    st.title(f"Juego: {fix_nan(g_l['Nombre'] if g_l is not None else t['game_details'])}")

    
    tab1, tab2, tab3 = st.tabs([t["overview_tab"], t["details_tab"], t["reviews_tab"]])

    with tab1:
        game_name = fix_nan(g_l.get('Nombre') if g_l is not None else 'Game')

        
        st.markdown(f"""
        <div style="position: relative; height: 300px; border-radius: 15px; overflow: hidden; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
            <img src="{get_enhanced_game_background(appid, game_name)}" style="width: 100%; height: 100%; object-fit: cover; filter: brightness(0.4);" />
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">
                <h1 style="font-size: 3em; margin: 0; font-weight: bold;">{game_name}</h1>
                <p style="font-size: 1.2em; margin: 10px 0 0 0; opacity: 0.9;">{fix_nan(g_i.get('Desarrollador'))}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

       
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t["rating_label"], f"{rating_num}/100" if not pd.isna(rating_num) else "N/A")
        with col2:
            st.metric(t["reviews_label"], f"{int(reviews_num):,}" if not pd.isna(reviews_num) else "N/A")
        with col3:
            st.metric(t["current_rank"], f"#{int(rank_num)}" if not pd.isna(rank_num) else "N/A")
        with col4:
            st.metric(t["current_players"], f"{int(players_num):,}" if not pd.isna(players_num) else "N/A")

        
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

        
        st.markdown(f"## {t['trailer']} & {t['twitch_streams']}")

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
                st.markdown(f"[{t['watch_trailer_on_steam']}](https://store.steampowered.com/app/{appid})")

        with media_col2:
            st.markdown(f"### {t['twitch_streams']}")
            if game_name_for_twitch:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #9146FF 0%, #1e1e2e 100%); padding: 30px; border-radius: 15px; text-align: center; color: white; height: 200px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 8px 32px rgba(145, 70, 255, 0.3);">
                    <h3 style="margin: 0 0 15px 0; color: #ffffff;">{t['twitch_streams']}</h3>
                    <p style="margin: 0 0 20px 0; opacity: 0.8;">{t['watch_live_streams_of'].format(game_name=game_name)}</p>
                    <a href="{twitch_url}" target="_blank" style="background: #ffffff; color: #9146FF; padding: 12px 24px; border-radius: 25px; text-decoration: none; font-weight: bold; display: inline-block; transition: all 0.3s ease;">
                        {t['open_twitch']}
                    </a>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #9146FF 0%, #1e1e2e 100%); padding: 30px; border-radius: 15px; text-align: center; color: white; height: 200px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <h3 style="margin: 0 0 15px 0;">{t['twitch_streams']}</h3>
                    <a href="https://www.twitch.tv" target="_blank" style="background: #ffffff; color: #9146FF; padding: 12px 24px; border-radius: 25px; text-decoration: none; font-weight: bold;">
                        {t['open_twitch']}
                    </a>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown(f"## {t['information']}")

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
                <h4 style="margin: 0 0 10px 0;">Statistics</h4>
            </div>
            """, unsafe_allow_html=True)
            st.write(f"**{t['current_rank']}:** {fix_nan(g_rank)}")
            st.write(f"**{t['current_players']}:** {fix_nan(g_players)}")
            st.write(f"**{t['price']}:** {format_local_price(g_d.get('Precio', 'N/A'), st.session_state.language)}")

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

        review_snippets = generate_review_snippets(
            fix_nan(g_l.get('Nombre') if g_l is not None else 'Juego'),
            rating,
            reviews
        )
        if review_snippets:
            st.markdown("#### Algunas reseñas")
            for snippet in review_snippets:
                st.write(f"- {snippet}")
        else:
            st.write("No hay texto de reseñas disponible en el dataset; sólo podemos mostrar el rating y el número de reseñas.")

        
        if "user" in st.session_state:
            game_title = fix_nan(g_l.get('Nombre') if g_l is not None else t['game_details'])
            try:
                f_df = pd.read_csv(FAV_FILE)
                is_fav = ((f_df['username'] == st.session_state["user"]) & (f_df['appid'] == appid)).any()
            except:
                is_fav = False
            render_card_controls(appid, game_title, "detail", is_fav, t, compact=False)
    st.stop()


if st.session_state.view == "Favorites":
    st.title(f"{t['my_favorites']}")
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
                        get_aid = int(row["appid"])
                        g_name = None
                        g_row = df_listado[df_listado['AppID'] == get_aid]
                        if not g_row.empty:
                            g_name = g_row['Nombre'].iloc[0]
                        else:
                            info_row = df_info[df_info['AppID'] == get_aid]
                            if not info_row.empty:
                                g_name = info_row['Nombre'].iloc[0]
                        if not g_name:
                            g_name = f"AppID: {get_aid}"

                        with col:
                            det_row = df_detalles[df_detalles['AppID'] == get_aid]
                            price_raw = det_row['Precio'].iloc[0] if not det_row.empty else None
                            info_row = df_info[df_info['AppID'] == get_aid]
                            genres_raw = info_row['Géneros'].iloc[0] if not info_row.empty else None
                            rel_dt = info_row['Fecha_Lanzamiento'].iloc[0] if not info_row.empty else None
                            render_game_card(get_aid, fix_nan(g_name), t, f"fav_{idx}", price_raw=price_raw, genres_raw=genres_raw, rel_dt=rel_dt)
    st.stop()

 
if st.session_state.view == "Chat":
    st.title("Infosteam AI Assistant")
    st.markdown("Asistente Avanzado. Puedes hablarme en lenguaje natural o escribir fragmentos vagos de juegos.")

    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hola. He analizado los CSVs del sistema. Pregúntame cosas como: '¿qué juegos son gratis?', 'busca juegos de Valve', 'juegos con rating mayor a 90' o un título parcial como 'strike'."}
        ]

    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

   
    if user_query := st.chat_input("Escribe tu consulta analítica..."):
        with st.chat_message("user"):
            st.write(user_query)
        st.session_state.chat_messages.append({"role": "user", "content": user_query})

        ai_reply = ""
        query_lower = user_query.lower()

        
        alias_mapping = {
            r"\bcs\b": "counter-strike",
            r"\bcsgo\b": "counter-strike",
            r"\bcs2\b": "counter-strike",
            r"\bgta\b": "grand theft auto",
            r"\bpubg\b": "playerunknown",
            r"\bcod\b": "call of duty"
        }
        for alias, real_name in alias_mapping.items():
            query_lower = re.sub(alias, real_name, query_lower)

        
        if "gratis" in query_lower or "free" in query_lower:
            df_m = df_detalles.copy()
            df_m['Price_Val'] = df_m['Precio'].apply(convert_to_usd_numeric)
            gratis_df = df_m[df_m['Price_Val'] == 0.0].head(5)
            if not gratis_df.empty:
                ai_reply = "### Juegos Populares Gratuitos Detectados:\n\n"
                for _, r in gratis_df.iterrows():
                    ai_reply += f"- **{r['Nombre']}** (Rating: {fix_nan(r.get('Rating'), 'N/A')}/100)\n"
            else:
                ai_reply = "No localicé juegos marcados explícitamente como gratuitos en los datos actuales."

        elif "desarrollador" in query_lower or "creador" in query_lower or "de valve" in query_lower:
            dev_search = query_lower.replace("desarrollador", "").replace("creador", "").replace("de", "").replace("busca", "").strip()
            if not dev_search: dev_search = "valve"
            
            dev_df = df_info[df_info['Desarrollador'].fillna('').astype(str).str.lower().str.contains(dev_search)].head(5)
            if not dev_df.empty:
                ai_reply = f"### Juegos del desarrollador que coincide con '{dev_search.title()}':\n\n"
                for _, r in dev_df.iterrows():
                    ai_reply += f"- **{r['Nombre']}** | Géneros: {r.get('Géneros','-')}\n"
            else:
                ai_reply = f"No encontré ningún desarrollador que contenga el término '{dev_search}' en nuestros registros actuales."

        elif "mejor rating" in query_lower or "puntuacion alta" in query_lower or "rating mayor" in query_lower or "buen rating" in query_lower:
            df_r = df_detalles.copy()
            df_r['Rating_Num'] = pd.to_numeric(df_r['Rating'], errors='coerce').fillna(0)
            mejo_df = df_r.sort_values('Rating_Num', ascending=False).head(5)
            ai_reply = "### Los 5 Juegos con Mejor Puntuación Analizados:\n\n"
            for _, r in mejo_df.iterrows():
                ai_reply += f"- **{r['Nombre']}**: {int(r['Rating_Num'])}/100 de valoración positiva.\n"

        else:
            clean_search = query_lower.replace("busca", "").replace("informacion", "").replace("sobre", "").replace("info", "").replace("del", "").replace("juego", "").strip()
            
            found_games = []
            if len(clean_search) > 1 and not df_info.empty:
                for _, row in df_info.iterrows():
                    g_name = str(row.get('Nombre', '')).lower()
                    if clean_search in g_name or g_name in clean_search:
                        found_games.append(row)
                        if len(found_games) >= 3: break

            if found_games:
                ai_reply = f"Analizando la base de datos, localicé {len(found_games)} juego(s) vinculados a tu criterio:\n\n"
                for game in found_games:
                    appid_found = int(game['AppID'])
                    det_row = df_detalles[df_detalles['AppID'] == appid_found]
                    precio_game = det_row['Precio'].iloc[0] if not det_row.empty else "N/A"
                    rating_game = det_row['Rating'].iloc[0] if not det_row.empty else "N/A"
                    
                    df_day_dt = df_listado[df_listado["Fecha"] == st.session_state.sel_date]
                    listado_row = df_day_dt[df_day_dt['AppID'] == appid_found]
                    players_game = listado_row['JugadoresConcurrentes'].iloc[0] if not listado_row.empty else "N/A"

                    precio_local = format_local_price(precio_game, st.session_state.language)
                    
                    ai_reply += f"### {game['Nombre']}\n"
                    ai_reply += f"- **Desarrollador:** {game.get('Desarrollador', '-')}\n"
                    ai_reply += f"- **Géneros:** {game.get('Géneros', '-')}\n"
                    ai_reply += f"- **Precio Real:** {precio_local}\n"
                    ai_reply += f"- **Rating:** {rating_game}/100\n"
                    if isinstance(players_game, (int, float)):
                        ai_reply += f"- **Jugadores concurrentes hoy:** {int(players_game):,}\n"
                    else:
                        ai_reply += f"- **Jugadores concurrentes hoy:** {players_game}\n"
                    ai_reply += "\n"
            
            elif "hola" in query_lower or "saludos" in query_lower or "buenas" in query_lower:
                ai_reply = "Hola. Estoy listo. Puedes pedirme listas de juegos por desarrolladores, gratuitos, top ratings o ingresar un trozo de un título."
            elif "mas jugado" in query_lower or "top 1" in query_lower:
                df_day_dt = df_listado[df_listado["Fecha"] == st.session_state.sel_date]
                if not df_day_dt.empty:
                    top_1 = df_day_dt.iloc[0]
                    ai_reply = f"El líder absoluto de hoy es **{top_1['Nombre']}** registrando **{int(top_1['JugadoresConcurrentes']):,}** usuarios activos."
                else:
                    ai_reply = "Sin datos de ranking para la fecha seleccionada."
            else:
                ai_reply = "No encontré coincidencias semánticas directas. Intenta simplificar la búsqueda ingresando palabras clave separadas (ej: 'Counter', 'Dota', 'Valve' o 'gratis')."

        with st.chat_message("assistant"):
            st.write(ai_reply)
        st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply})
        st.rerun()
    st.stop()

# ---------- 9. ANALYTICS VIEWS ---------- 
df_day = df_listado[df_listado["Fecha"] == st.session_state.sel_date].copy()

if st.session_state.view == "Market Trends":
    st.title(t["market_trends_title"])
    market_df = df_detalles.copy()
    market_df['Reviews_Num'] = pd.to_numeric(market_df['Reviews'], errors='coerce').fillna(0)
    top = market_df.sort_values('Reviews_Num', ascending=False).head(24)
    if top.empty:
        st.info("No data available")
    else:
        cols_per_row = 4 #Número de columnas por fila para mostrar las tarjetas de los juegos. En este caso, se mostrarán 4 tarjetas por fila, lo que permite una presentación más compacta y organizada de los juegos populares en la sección de tendencias del mercado.
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

elif st.session_state.view == "Top Genres": #Esta sección se enfoca en analizar la popularidad de los géneros de juegos presentes en el dataset. Primero, se extraen y cuentan los géneros de los juegos para visualizar cuáles son los más comunes. Luego, se muestra una selección de juegos populares dentro de esos géneros, ordenados por número de jugadores concurrentes y número de reseñas, proporcionando a los usuarios una visión clara de qué tipos de juegos están dominando el mercado actualmente.
    st.title(t["genre_popularity_title"])
    genre_df = df_info[['AppID', 'Nombre', 'Géneros', 'Fecha_Lanzamiento']].copy()
    genre_df['Genre_List'] = genre_df['Géneros'].apply(get_genre_tokens)

    flattened = [genre for row in genre_df['Genre_List'] for genre in row]
    counts = pd.Series(flattened).value_counts().sort_values(ascending=False)
    fig = go.Figure(data=[go.Bar(x=counts.index, y=counts.values)])
    fig.update_layout(xaxis={'categoryorder':'total descending'}, height=400)
    st.plotly_chart(fig, use_container_width=True)

    popularity_df = genre_df.merge(df_detalles[['AppID', 'Reviews']], on='AppID', how='left')
    popularity_df['Reviews_Num'] = pd.to_numeric(popularity_df['Reviews'], errors='coerce').fillna(0)
    if not df_day.empty:
        player_map = df_day.set_index('AppID')['JugadoresConcurrentes'].to_dict()
        popularity_df['Current_Players'] = popularity_df['AppID'].map(player_map).fillna(0)
    else:
        popularity_df['Current_Players'] = 0

    sample = popularity_df.sort_values(['Current_Players', 'Reviews_Num'], ascending=False).head(24)
    cols_per_row = 4
    for r in range(0, len(sample), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            idx = r + i
            if idx < len(sample):
                row = sample.iloc[idx]
                aid = int(row.get('AppID', 0)) if not pd.isna(row.get('AppID', 0)) else 0
                with col:
                    render_game_card(
                        aid,
                        fix_nan(row.get('Nombre')),
                        t,
                        f"tg_{idx}",
                        genres_raw=', '.join(row.get('Genre_List', [])),
                        rel_dt=row.get('Fecha_Lanzamiento')
                    )
    st.stop()

elif st.session_state.view == "Top Developers":
    st.title(t["top_developers_title"])
    devs = df_info['Desarrollador'].value_counts().sort_values(ascending=False).head(15)
    fig = go.Figure(data=[go.Bar(x=devs.index, y=devs.values)])
    fig.update_layout(xaxis={'categoryorder':'total descending'}, height=400)
    st.plotly_chart(fig, use_container_width=True)
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
    popular_list = popular_releases.sort_values('peak_last_week', ascending=False).reset_index(drop=True)
    if popular_list.empty:
        st.info("No popular releases found.")
    else:
        popular_list = popular_list.loc[popular_list['peak_last_week'] > 0].head(3)
        if popular_list.empty:
            popular_list = popular_releases.sort_values('peak_last_week', ascending=False).head(3).reset_index(drop=True)

        cols = st.columns(3)
        for idx, row in enumerate(popular_list.itertuples(index=False)):
            with cols[idx]:
                aid = int(getattr(row, 'AppID', 0)) if not pd.isna(getattr(row, 'AppID', 0)) else 0
                name = fix_nan(getattr(row, 'Nombre', None))
                rel_dt = getattr(row, 'Fecha_Lanzamiento', None)
                rel_str = parse_date_safe(rel_dt).strftime('%Y-%m-%d') if not pd.isna(parse_date_safe(rel_dt)) else fix_nan(rel_dt)
                peak = int(getattr(row, 'peak_last_week', 0)) if not pd.isna(getattr(row, 'peak_last_week', 0)) else 0
                badge = f"TOP {idx + 1}"
                render_dashboard_card(aid, name, t, f"pop_{idx}", small_image_height=140, badge=badge, peak=peak)
                st.caption(f"{t['release_date']}: {rel_str}  •  {t['weekly_peak']}: {peak}")
    st.stop()

elif st.session_state.view == "Future Trending":
    st.title(t["future_trending_title"])
    st.subheader(t["future_trending_title"])
    st.markdown(t["future_trending_description"])
    render_trend_formula_card(t)

    trend_ref_date = get_latest_data_date()
    trend_df = compute_trend_scores(trend_ref_date, limit=12)
    if trend_df.empty:
        st.info(t.get("no_trend_data", "No trend data available."))
    else:
        trend_df = trend_df.sort_values('Trend Score', ascending=False)
        st.markdown(f"### {t.get('trend_forecast_chart', 'Top Trend Games')}")
        fig = go.Figure(data=[go.Bar(x=trend_df['Nombre'], y=trend_df['Trend Score'])])
        fig.update_layout(xaxis={'categoryorder':'total descending'}, height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("### " + t.get('trend_formula_title', 'Formula de tendencia'))
        st.dataframe(trend_df[['Nombre', 'Weekly peak', 'Growth 7d', 'Recency', 'Trend Score']].rename(columns={
            'Nombre': t.get('name_filter', 'Name'),
            'Weekly peak': t.get('weekly_peak', 'Weekly peak'),
            'Growth 7d': 'Growth 7d',
            'Recency': 'Recency',
            'Trend Score': 'Trend Score'
        }))

        with st.expander(t.get('trend_formula_title', 'Formula de tendencia')):
            st.markdown(t['trend_formula_equation'])
            st.markdown(t['trend_formula_note'])

elif st.session_state.view == "Price Analysis":
    st.title(t["price_analysis_title"])
    df_p = df_detalles.copy()
    df_p['Price_Val'] = df_p['Precio'].apply(convert_to_usd_numeric)
    price_sorted = df_p.sort_values('Price_Val', ascending=False).head(20)
    fig = go.Figure(data=[go.Bar(x=price_sorted['Nombre'], y=price_sorted['Price_Val'])])
    fig.update_layout(xaxis={'categoryorder':'total descending'}, height=400)
    st.plotly_chart(fig, use_container_width=True)
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

 
st.title(t["dashboard_title"])


m1, m2, m3, m4 = st.columns(4)
selected_peak_date = st.session_state.sel_date if st.session_state.sel_date else get_latest_data_date()
m1.metric(t["players_online"], f"{int(df_day['JugadoresConcurrentes'].sum()):,}")
m2.metric(t["games_tracked"], f"{len(df_day)}")
m3.metric(t["top_game"], fix_nan(df_day.iloc[0]["Nombre"]) if len(df_day) > 0 else "N/A")
m4.metric(t["peak_24h"], f"{get_peak_last_24h(selected_peak_date):,}")

st.divider()

t1, t2, t3, t4, t5, t6 = st.tabs([t["live_rankings"], t["performance_trend"], t["data_explorer"], t["peak_24h_section"], t["popular_releases_title"], t["trend_forecast_title"]])

with t1:
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
                    pos = int(game.get('Posicion', 0)) if not pd.isna(game.get('Posicion', 0)) else 0
                    players = int(game.get('JugadoresConcurrentes', 0)) if not pd.isna(game.get('JugadoresConcurrentes', 0)) else 0
                    render_game_card(aid, fix_nan(game_name), t, f"lr_{idx}", extra_caption=f"#{pos}  •  {players:,}")
    if st.button(t["toggle_top"]):
        st.session_state.show_more = not st.session_state.show_more
        st.rerun()

with t2:
    st.header(t["historical_trends_header"])
    dates_list = sorted(df_listado["Fecha"].unique(), reverse=True)
    if len(dates_list) < 2:
        st.info(t.get('no_24h_data', 'Not enough data for trends'))
    else:
        st.subheader(t["market_share"])
        sel_g = st.multiselect(t["compare_games"], sorted(df_listado["Nombre"].unique()), default=df_day.head(5)["Nombre"].tolist())
        if sel_g:
            selected_date = pd.to_datetime(st.session_state.sel_date, format="%Y-%m-%d", errors="coerce")
            if pd.isna(selected_date):
                st.info("Fecha seleccionada no válida para el filtro de una week.")
            else:
                one_week_ago = selected_date - pd.Timedelta(days=6)
                filtered = df_listado[df_listado["Nombre"].isin(sel_g)].copy()
                filtered["Fecha_dt"] = pd.to_datetime(filtered["Fecha"], format="%Y-%m-%d", errors="coerce")
                filtered = filtered[(filtered["Fecha_dt"] >= one_week_ago) & (filtered["Fecha_dt"] <= selected_date)]
                pivot = (
                    filtered.pivot_table(index="Fecha_dt", columns="Nombre", values="JugadoresConcurrentes")
                    .fillna(0)
                )
                if not pivot.empty:
                    st.line_chart(pivot.sort_index())
                else:
                    st.info(t["no_weekly_data"])
        else:
            st.info(t["select_at_least_one_game"])

        top_today = df_day.sort_values("JugadoresConcurrentes", ascending=False).head(10)
        if not top_today.empty:
            st.subheader("Top 10 juegos hoy por jugadores concurrentes")
            fig = go.Figure(data=[go.Bar(x=top_today['Nombre'], y=top_today['JugadoresConcurrentes'])])
            fig.update_layout(xaxis={'categoryorder':'total descending'}, height=400)
            st.plotly_chart(fig, use_container_width=True)

        prev_date = dates_list[1]
        cur = df_listado[df_listado["Fecha"] == st.session_state.sel_date]
        prev = df_listado[df_listado["Fecha"] == prev_date]
        merged = (
            cur.set_index('AppID')[['JugadoresConcurrentes']]
            .rename(columns={'JugadoresConcurrentes': 'cur_players'})
            .join(
                prev.set_index('AppID')[['JugadoresConcurrentes']]
                .rename(columns={'JugadoresConcurrentes': 'prev_players'}),
                how='left'
            )
            .fillna(0)
        )
        merged['growth'] = merged['cur_players'].astype(float) - merged['prev_players'].astype(float)
        movers = merged.sort_values('growth', ascending=False).head(10).reset_index()
        if not movers.empty:
            movers = movers.merge(df_listado[['AppID', 'Nombre']].drop_duplicates(subset=['AppID']), on='AppID', how='left')
            st.subheader("Top 10 crecimiento diario")
            fig = go.Figure(data=[go.Bar(x=movers['Nombre'], y=movers['growth'])])
            fig.update_layout(xaxis={'categoryorder':'total descending'}, height=400)
            st.plotly_chart(fig, use_container_width=True)

with t3:
    st.header(t.get('data_explorer', t['data_explorer']))

    explorer_df = df_day.copy()
    explorer_df = explorer_df.merge(
        df_info[['AppID', 'Géneros', 'Desarrollador']], on='AppID', how='left'
    ).merge(
        df_detalles[['AppID', 'Precio', 'Rating']], on='AppID', how='left'
    )
    platform_df = df_plataformas[df_plataformas['Fecha'] == st.session_state.sel_date][['AppID', 'Plataformas']]
    explorer_df = explorer_df.merge(platform_df, on='AppID', how='left')

    explorer_df['Precio'] = explorer_df['Precio'].apply(convert_to_usd_numeric)
    explorer_df['JugadoresConcurrentes'] = pd.to_numeric(explorer_df['JugadoresConcurrentes'], errors='coerce').fillna(0)
    explorer_df['Genre_List'] = explorer_df['Géneros'].apply(get_genre_tokens)

    genre_options = sorted({genre for row in explorer_df['Genre_List'] for genre in row})
    dev_options = sorted(explorer_df['Desarrollador'].dropna().astype(str).unique())
    platform_options = sorted({p.strip() for row in explorer_df['Plataformas'].dropna().astype(str).str.split(',') for p in row if p.strip()})

    pmin = int(explorer_df['Precio'].min()) if not explorer_df['Precio'].dropna().empty else 0
    pmax = int(explorer_df['Precio'].max()) if not explorer_df['Precio'].dropna().empty else 0
    jmin = int(explorer_df['JugadoresConcurrentes'].min()) if not explorer_df['JugadoresConcurrentes'].empty else 0
    jmax = int(explorer_df['JugadoresConcurrentes'].max()) if not explorer_df['JugadoresConcurrentes'].empty else 0

    st.subheader(t["filters_title"])
    f1, f2 = st.columns(2)
    with f1:
        selected_names = st.multiselect(t["name_filter"], sorted(explorer_df['Nombre'].dropna().astype(str).unique()), default=[])
        selected_genres = st.multiselect(t["genre_filter"], genre_options, default=[])
        selected_developers = st.multiselect(t["developer_filter"], dev_options, default=[])
    with f2:
        selected_platforms = st.multiselect(t["platform_filter"], platform_options, default=[])
        selected_price = st.slider(t["price_range"], pmin, pmax, (pmin, pmax)) if pmin < pmax else (pmin, pmax)
        selected_players = st.slider(t["players_range"], jmin, jmax, (jmin, jmax)) if jmin < jmax else (jmin, jmax)

    filtered = explorer_df.copy()
    if selected_names:
        normalized_names = [name.strip().lower() for name in selected_names]
        filtered = filtered[filtered['Nombre'].fillna('').astype(str).apply(lambda x: x.strip().lower() in normalized_names)]
    if selected_genres:
        normalized = [genre.strip().lower() for genre in selected_genres]
        filtered = filtered[filtered['Genre_List'].apply(lambda genres: any(genre in [g.lower() for g in genres] for genre in normalized))]
    if selected_developers:
        normalized_devs = [dev.strip().lower() for dev in selected_developers]
        filtered = filtered[filtered['Desarrollador'].fillna('').apply(lambda x: x.strip().lower() in normalized_devs)]
    if selected_platforms:
        normalized_plats = [plat.strip().lower() for plat in selected_platforms]
        filtered = filtered[filtered['Plataformas'].fillna('').apply(lambda x: any(plat in [p.strip().lower() for p in x.split(',')] for plat in normalized_plats))]
    if selected_price:
        filtered = filtered[(filtered['Precio'].fillna(0) >= selected_price[0]) & (filtered['Precio'].fillna(0) <= selected_price[1])]
    if selected_players:
        filtered = filtered[(filtered['JugadoresConcurrentes'] >= selected_players[0]) & (filtered['JugadoresConcurrentes'] <= selected_players[1])]

    has_active_filters = bool(
        selected_names or selected_genres or selected_developers or selected_platforms or
        selected_price != (pmin, pmax) or selected_players != (jmin, jmax)
    )

    if filtered.empty and has_active_filters:
        st.warning(f"{t['no_filtered_results']} {t['fallback_to_top']}")
        filtered = explorer_df.copy()

    st.markdown(f"{t['filtered_results']} {len(filtered)}")
    sample = filtered.sort_values('JugadoresConcurrentes', ascending=False).head(12).reset_index(drop=True)
    cols_per_row = 4
    for r in range(0, len(sample), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            idx = r + i
            if idx < len(sample):
                row = sample.iloc[idx]
                aid = int(row.get('AppID', 0)) if not pd.isna(row.get('AppID', 0)) else 0
                with col:
                    render_dashboard_card(
                        aid,
                        fix_nan(row.get('Nombre')),
                        t,
                        f"de_{idx}",
                        players=row.get('JugadoresConcurrentes')
                    )

with t4:
    st.subheader(t["peak_24h_section"])
    peak_date = st.session_state.sel_date if st.session_state.sel_date else get_latest_data_date()
    peak_value = get_peak_last_24h(peak_date)
    st.metric(t["peak_24h"], f"{peak_value:,}")
    if peak_date is not None and not pd.isna(parse_date_safe(peak_date)):
        st.write(f"{t['data_date']} {parse_date_safe(peak_date).strftime('%Y-%m-%d')}")

    if len(df_day) > 0:
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
    if 'is_popular' in popular_releases.columns:
        popular_releases = popular_releases.loc[popular_releases['is_popular']]
    popular_releases = popular_releases.loc[popular_releases['peak_last_week'] > 0]
    if len(popular_releases) < 3:
        fallback_releases = compute_popular_releases(popular_ref_date)
        fallback_releases = fallback_releases.loc[fallback_releases['peak_last_week'] > 0].sort_values('peak_last_week', ascending=False)
        popular_releases = fallback_releases.head(3)
    popular_short = popular_releases.sort_values('peak_last_week', ascending=False).head(3).reset_index(drop=True)
    if popular_short.empty:
        st.info(t.get('no_filtered_results', 'No popular releases found.'))
    else:
        cols_per_row = 3
        cols = st.columns(cols_per_row)
        for idx, col in enumerate(cols):
            if idx < len(popular_short):
                row = popular_short.iloc[idx]
                aid = int(row.get('AppID', 0))
                name = fix_nan(row.get('Nombre'))
                badge = f"TOP {idx + 1}"
                with col:
                    render_dashboard_card(aid, name, t, f"popdash_{idx}", peak=row.get('peak_last_week'), badge=badge)

with t6:
    st.subheader(t["trend_forecast_title"])
    st.markdown(t["trend_forecast_description"])
    render_trend_formula_card(t)
    
    trend_ref_date = get_latest_data_date()
    trend_df = compute_trend_scores(trend_ref_date, limit=12)
    
    if trend_df.empty:
        st.info("No trend data available.")
    else:
        trend_df = trend_df.sort_values('Trend Score', ascending=False)
        fig = go.Figure(data=[go.Bar(x=trend_df['Nombre'], y=trend_df['Trend Score'])])
        fig.update_layout(xaxis={'categoryorder':'total descending'}, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Top Trend Games")
        cols_per_row = 4
        for r in range(0, len(trend_df), cols_per_row):
            cols = st.columns(cols_per_row)
            for i, col in enumerate(cols):
                idx = r + i
                if idx < len(trend_df):
                    row = trend_df.iloc[idx]
                    aid = int(row['AppID']) if not pd.isna(row['AppID']) else 0
                    name = fix_nan(row.get('Nombre'))
                    score = row.get('Trend Score', 0)
                    with col:
                        st.metric(label=name, value=f"{score:.0f}")

st.divider()
st.caption(t["copyright"])