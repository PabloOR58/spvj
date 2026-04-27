import streamlit as st
import pandas as pd
import os
import re
import json
from datetime import datetime

try:
    import genai
except ImportError:
    genai = None

# ---------- 1. PAGE CONFIGURATION ---------- 
st.set_page_config(
    page_title="infosteam | Professional Dashboard",
    page_icon="🎮",
    layout="wide"
)

IMG_ERROR = "https://i.imgur.com/8N9V6vT.png"
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
    image = get_game_image(appid)
    if image and "steamstatic.com" in image:
        return image

    if game_name:
        unsplash_image = search_game_image_unsplash(game_name)
        if unsplash_image:
            return unsplash_image

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

def search_game_image_unsplash(game_name):
    """Search for game images using Unsplash API (free, no API key needed)"""
    try:
        import requests
        # Clean and prepare game name for search
        search_term = game_name.lower().strip()

        # Handle special cases and abbreviations
        special_cases = {
            'fivem': 'gta v fivem multiplayer',
            'fife': 'gta v fivem',
            'gta v': 'grand theft auto v',
            'gta 5': 'grand theft auto v',
            'csgo': 'counter strike global offensive',
            'cs:go': 'counter strike global offensive',
            'lol': 'league of legends',
            'dota': 'dota 2 defense of the ancients',
            'wow': 'world of warcraft',
            'fortnite': 'fortnite battle royale',
            'minecraft': 'minecraft game',
            'among us': 'among us crewmate',
            'amongus': 'among us crewmate',
            'rocket league': 'rocket league soccer',
            'rocketleague': 'rocket league soccer',
            'apex': 'apex legends battle royale',
            'apex legends': 'apex legends battle royale',
            'valorant': 'valorant tactical shooter',
            'overwatch': 'overwatch team shooter',
            'pubg': 'playerunknown battlegrounds',
            'rainbow six': 'rainbow six siege',
            'r6': 'rainbow six siege',
            'cod': 'call of duty modern warfare',
            'call of duty': 'call of duty modern warfare',
            'fifa': 'fifa soccer football',
            'nba': 'nba basketball',
            'madden': 'madden nfl football',
            'nhl': 'nhl hockey',
            'the sims': 'the sims life simulation',
            'sims': 'the sims life simulation',
            'civilization': 'civilization strategy game',
            'civ': 'civilization strategy game'
        }

        # Apply special cases
        for key, value in special_cases.items():
            if key in search_term:
                search_term = value
                break

        # Remove special characters and prepare for URL
        search_term = re.sub(r'[^\w\s]', '', search_term)
        search_query = search_term.replace(' ', '+') + '+game'

        url = f"https://api.unsplash.com/search/photos?query={search_query}&per_page=1&orientation=landscape"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if data.get('results') and len(data['results']) > 0:
                # Return the first result with proper dimensions
                image_url = data['results'][0]['urls']['regular']
                return image_url

    except Exception as e:
        # If Unsplash fails, continue to fallback
        pass

    return None

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
        if should_check_steam:
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
if "sel_date" not in st.session_state:
    if not df_listado.empty:
        dates = sorted(df_listado["Fecha"].unique(), reverse=True)
        st.session_state.sel_date = dates[0]
    else:
        st.session_state.sel_date = None

# ---------- 6. SIDEBAR ---------- 
with st.sidebar:
    st.title("🎮 infosteam")
    st.markdown("### 🔐 Account")
    if "user" not in st.session_state:
        auth_mode = st.radio("Mode", ["Login", "Register"], label_visibility="collapsed")
        u_name = st.text_input("User")
        u_pass = st.text_input("Password", type="password")

        if auth_mode == "Register":
            if st.button("Create Account", width='stretch'):
                users = pd.read_csv(USERS_FILE)
                if u_name in users["username"].values: st.error("User exists!")
                else:
                    new_u = pd.DataFrame([[u_name, u_pass]], columns=["username", "password"])
                    pd.concat([users, new_u]).to_csv(USERS_FILE, index=False)
                    st.success("User registered!")
        else:
            if st.button("Login", width='stretch'):
                users = pd.read_csv(USERS_FILE)
                valid = users[(users["username"] == u_name) & (users["password"] == u_pass)]
                if not valid.empty:
                    st.session_state["user"] = u_name
                    st.rerun()
                else: st.error("Wrong credentials")
    else:
        st.success(f"👤 Welcome, {st.session_state['user']}")
        if st.button("Logout", width='stretch'):
            del st.session_state["user"]
            st.rerun()
        if st.button("⭐ My Favorites", width='stretch'):
            st.session_state.view = "Favorites"
            st.rerun()

    st.divider()
    st.markdown("### 📑 Navigation")
    sections = ["Dashboard", "Market Trends", "Top Genres", "Top Developers", "Price Analysis", "Favorites"]
    st.session_state.view = st.selectbox("Menu", sections, index=sections.index(st.session_state.view) if st.session_state.view in sections else 0)

    if not df_listado.empty:
        dates = sorted(df_listado["Fecha"].unique(), reverse=True)
        st.session_state.sel_date = st.selectbox("Select Date:", dates, index=dates.index(st.session_state.sel_date) if st.session_state.sel_date in dates else 0)

    if st.button("🏠 Home Dashboard", width='stretch'):
        st.session_state.selected_game = None
        st.session_state.view = "Dashboard"
        st.rerun()

    if st.button("🔄 Update Data", width='stretch'):
        load_data.clear()
        st.rerun()

# ---------- 7. VIEW: GAME DETAIL ---------- 
if st.session_state.selected_game:
    appid = st.session_state.selected_game
    g_l = df_listado[df_listado["AppID"] == appid].iloc[0] if not df_listado[df_listado["AppID"] == appid].empty else None
    g_i = df_info[df_info["AppID"] == appid].iloc[0] if not df_info[df_info["AppID"] == appid].empty else pd.Series()
    g_d = df_detalles[df_detalles["AppID"] == appid].iloc[0] if not df_detalles[df_detalles["AppID"] == appid].empty else pd.Series()

    st.title(f"🎮 {fix_nan(g_l['Nombre'] if g_l is not None else 'Game Details')}")
    
    # Tabs for more detailed view
    tab1, tab2, tab3 = st.tabs(["📖 Overview", "ℹ️ Details", "⭐ Reviews"])
    
    with tab1:
        bg_title = f"Background of {fix_nan(g_l.get('Nombre') if g_l is not None else 'Game')}"
        img_title = f"Click for details - {fix_nan(g_l.get('Nombre') if g_l is not None else 'Game')}"
        ca, cb = st.columns([1.5, 1])
        with ca:
            game_name = fix_nan(g_l.get('Nombre') if g_l is not None else 'Game')
            st.markdown(f'<img src="{get_enhanced_game_background(appid, game_name)}" onerror=\'this.src="{IMG_ERROR}";\' style="width:100%; border-radius:10px;" title="{bg_title}">', unsafe_allow_html=True)
            st.subheader("📋 Information")
            st.write(f"**Developer:** {fix_nan(g_i.get('Desarrollador'))}")
            p_str = fix_nan(g_i.get('Plataformas'), "").lower()
            pc = st.columns(10)
            if "win" in p_str: pc[0].image(LOGOS["windows"], width=35)
            if "mac" in p_str or "apple" in p_str: pc[1].image(LOGOS["mac"], width=30)
            if "linux" in p_str: pc[2].image(LOGOS["linux"], width=35)
        with cb:
            game_name = fix_nan(g_l.get('Nombre') if g_l is not None else 'Game')
            st.markdown(f'<img src="{get_enhanced_game_image(appid, game_name)}" onerror=\'this.src="{IMG_ERROR}";\' style="width:100%; border-radius:10px;" title="{img_title}">', unsafe_allow_html=True)
            st.metric("Price", format_usd(g_d.get('Precio', 'N/A')))
        
        rating = fix_nan(g_d.get('Rating'), 'N/A')
        rating_num = pd.to_numeric(rating, errors='coerce')
        if not pd.isna(rating_num):
            st.metric("Rating", f"⭐ {rating_num}/100")
        else:
            st.metric("Rating", "⭐ N/A")
        
        reviews = fix_nan(g_d.get('Reviews'), 'N/A')
        reviews_num = pd.to_numeric(reviews, errors='coerce')
        if not pd.isna(reviews_num):
            st.metric("Reviews", f"💬 {int(reviews_num):,}")
        else:
            st.metric("Reviews", "💬 N/A")
            
            # Additional metrics
            g_rank = df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)]["Posicion"].iloc[0] if not df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)].empty else "N/A"
            g_players = df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)]["JugadoresConcurrentes"].iloc[0] if not df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)].empty else "N/A"
            
            rank_num = pd.to_numeric(g_rank, errors='coerce')
            if not pd.isna(rank_num):
                st.metric("Current Rank", f"#{int(rank_num)}")
            else:
                st.metric("Current Rank", "#N/A")
            
            players_num = pd.to_numeric(g_players, errors='coerce')
            if not pd.isna(players_num):
                st.metric("Current Players", f"👥 {int(players_num):,}")
            else:
                st.metric("Current Players", "👥 N/A")
            
            st.markdown(f"[🚀 Open in Steam](https://store.steampowered.com/app/{appid})")
    
    with tab2:
        st.subheader("📅 Release Information")
        st.write(f"**Release Date:** {fix_nan(g_i.get('Fecha_Lanzamiento'))}")
        st.write(f"**Genres:** {fix_nan(g_i.get('Géneros'))}")
        st.write(f"**Platforms:** {fix_nan(g_i.get('Plataformas'))}")
        st.write(f"**Developer:** {fix_nan(g_i.get('Desarrollador'))}")
        
        # Description section
        st.subheader("📝 About This Game")
        st.write("Detailed game description not available in current dataset. This would typically include a comprehensive overview of the game's storyline, gameplay mechanics, and features. Please visit the game's Steam page for full details.")
    
    with tab3:
        st.subheader("⭐ User Reviews")
        rating = fix_nan(g_d.get('Rating'), 'N/A')
        reviews = fix_nan(g_d.get('Reviews'), 'N/A')
        
        rating_num = pd.to_numeric(rating, errors='coerce')
        reviews_num = pd.to_numeric(reviews, errors='coerce')
        
        if not pd.isna(rating_num):
            st.metric("Overall Rating", f"{rating_num}/100")
        else:
            st.write("**Overall Rating:** Not available")
        
        if not pd.isna(reviews_num):
            st.metric("Total Reviews", f"{int(reviews_num):,}")
        else:
            st.write("**Total Reviews:** Not available")
        
        # Add favorite functionality in game detail view
        if "user" in st.session_state:
            f_df = pd.read_csv(FAV_FILE)
            is_fav = ((f_df['username'] == st.session_state["user"]) & (f_df['appid'] == appid)).any()
            if is_fav:
                if st.button("💔 Remove from Favorites", width='stretch'):
                    f_df = f_df[~((f_df['username'] == st.session_state["user"]) & (f_df['appid'] == appid))]
                    f_df.to_csv(FAV_FILE, index=False)
                    st.rerun()
            else:
                if st.button("❤️ Add to Favorites", width='stretch'):
                    new_fav = pd.DataFrame([[st.session_state["user"], appid]], columns=["username","appid"])
                    pd.concat([f_df, new_fav]).to_csv(FAV_FILE, index=False)
                    st.success("Added to favorites!")
    st.stop()

# ---------- 8. VIEW: FAVORITES ---------- 
if st.session_state.view == "Favorites":
    st.title("⭐ My Favorite Games")
    if "user" not in st.session_state:
        st.warning("Please login to see your favorites.")
    else:
        favs_df = pd.read_csv(FAV_FILE)
        user_favs = favs_df[favs_df["username"] == st.session_state["user"]]
        if user_favs.empty:
            st.info("Your favorites list is empty.")
        else:
            for idx, row in user_favs.iterrows():
                aid = int(row["appid"])
                # Get Name for display
                g_data = df_listado[df_listado["AppID"] == aid]
                g_name = g_data["Nombre"].iloc[0] if not g_data.empty else f"AppID: {aid}"
                
                c1, c2, c3 = st.columns([1, 4, 1])
                with c1:
                    st.markdown(f'<img src="{get_enhanced_game_image(aid, g_name)}" onerror=\'this.src="{IMG_ERROR}";\' style="width:100%; height:auto; border-radius:10px;" title="{g_name}">', unsafe_allow_html=True)
                with c2: 
                    st.markdown(f"### {g_name}")
                    if st.button("View Info", key=f"fav_view_{aid}"):
                        st.session_state.selected_game = aid
                        st.rerun()
                with c3:
                    if st.button("🗑️ Remove", key=f"del_{aid}_{idx}", width='stretch'):
                        favs_df = favs_df.drop(idx)
                        favs_df.to_csv(FAV_FILE, index=False)
                        st.rerun()
    st.stop()

# ---------- 9. ANALYTICS VIEWS ---------- 
df_day = df_listado[df_listado["Fecha"] == st.session_state.sel_date].copy()

if st.session_state.view == "Market Trends":
    st.title("📈 Market Trends & Sales")
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
    st.dataframe(df_p[['Nombre', 'Precio', 'Rating']].sort_values('Price_Val', ascending=False), width='stretch', hide_index=True)
    st.stop()

# ---------- 10. MAIN DASHBOARD ---------- 
st.title("🎮 Dashboard")

# Dashboard metrics
m1, m2, m3 = st.columns(3)
m1.metric("🟢 Players Online", f"{int(df_day['JugadoresConcurrentes'].sum()):,}")
m2.metric("🎮 Games Tracked", f"{len(df_day)}")
m3.metric("🏆 Top Game", fix_nan(df_day.iloc[0]["Nombre"]) if len(df_day) > 0 else "N/A")

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
                    
                    if st.button("Details", key=f"btn_{idx}", width='stretch'):
                        st.session_state.selected_game = aid
                        st.rerun()
                    
                    if "user" in st.session_state:
                        # LOGICA DE FAVORITOS CORREGIDA (EVITA DUPLICADOS)
                        if st.button("❤️ Favorite", key=f"fav_{idx}", width='stretch'):
                            f_df = pd.read_csv(FAV_FILE)
                            # Verificar si ya existe para este usuario
                            if not ((f_df['username'] == st.session_state["user"]) & (f_df['appid'] == aid)).any():
                                new_fav = pd.DataFrame([[st.session_state["user"], aid]], columns=["username","appid"])
                                pd.concat([f_df, new_fav]).to_csv(FAV_FILE, index=False)
                                st.success(f"Saved: {game.get('Nombre')}")
                            else:
                                st.info("Already in favorites")
                    
                    st.caption(f"👥 {int(game.get('JugadoresConcurrentes', 0)):,} players")

    # BOTÓN ACTUALIZADO PARA TOP 100
    if st.button("Toggle Top 10 / 100"):
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
                # General AI response using new API
                try:
                    client = genai.Client(api_key=st.secrets.get("GOOGLE_API_KEY", "your-api-key-here"))
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=f"You are a helpful game information assistant. Help users with questions about video games. If they ask about specific games, suggest they mention the game name. You have access to a database of games but need the name to provide specific info.\n\nUser question: {user_input}"
                    )
                    bot_response = response.text.strip()
                except Exception as e:
                    bot_response = f"I couldn't find a specific game in your question. Please mention a game name from our database, like 'Counter-Strike 2' or 'Dota 2'. AI service may be unavailable: {str(e)}"

            st.session_state.global_chat_history.append({"role": "assistant", "content": bot_response})
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)