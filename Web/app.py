import streamlit as st
import pandas as pd
import os
import re

# ---------- PAGE CONFIGURATION ----------
st.set_page_config(
    page_title="infosteam | Professional Dashboard",
    page_icon="🎮",
    layout="wide"
)

# Fallback image if Steam fails
IMG_ERROR = "https://i.imgur.com/8N9V6vT.png"

# ---------- DATA PERSISTENCE (LOGIN/FAVORITES) ----------
USERS_FILE = "users.csv"
FAV_FILE = "favoritos.csv"

def init_user_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["username", "password"]).to_csv(USERS_FILE, index=False)
    if not os.path.exists(FAV_FILE):
        pd.DataFrame(columns=["username", "appid"]).to_csv(FAV_FILE, index=False)

init_user_files()

# Platform Logos
LOGOS = {
    "windows": "https://img.icons8.com/color/48/000000/windows-10.png",
    "mac": "https://img.icons8.com/ios-filled/50/ffffff/mac-os.png",
    "linux": "https://img.icons8.com/color/48/000000/tux.png"
}

# ---------- HELPER FUNCTIONS ----------
def fix_nan(val, default="-"):
    if pd.isna(val) or str(val).lower() == "nan" or str(val).strip() == "":
        return default
    return str(val)

def convert_to_usd_numeric(price_str):
    """Clean and convert prices to float for analytics."""
    if pd.isna(price_str) or str(price_str).lower() == "nan": return 0.0
    p = str(price_str).upper()
    if any(word in p for word in ["GRATIS", "FREE", "0"]): return 0.0
    try:
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", p.replace(',', '.'))
        if not nums: return 0.0
        val = float(nums[0])
        # Exchange rates to USD
        rates = {"€": 1.08, "฿": 0.028, "РУБ": 0.011, "AED": 0.27, "CLP": 0.0011, "CDN$": 0.74, "¥": 0.0067}
        for s, r in rates.items():
            if s in p: return val * r
        return val
    except: return 0.0

def format_usd(price_str):
    """Returns formatted string for UI display."""
    val = convert_to_usd_numeric(price_str)
    return "Free to Play" if val == 0.0 else f"${round(val, 2)}"

def get_game_image(appid):
    try: clean_id = str(int(float(appid)))
    except: clean_id = "0"
    return f"https://cdn.akamai.steamstatic.com/steam/apps/{clean_id}/header.jpg"

def get_game_background(appid):
    try: clean_id = str(int(float(appid)))
    except: return IMG_ERROR
    return f"https://cdn.akamai.steamstatic.com/steam/apps/{clean_id}/page_bg_generated_v6b.jpg"

# ---------- DATA LOADING ----------
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

# ---------- SESSION STATE ----------
if "selected_game" not in st.session_state: st.session_state.selected_game = None
if "show_more" not in st.session_state: st.session_state.show_more = False
if "view" not in st.session_state: st.session_state.view = "Dashboard"

# ---------- SIDEBAR NAVIGATION ----------
with st.sidebar:
    st.title("🎮 infosteam")
    
    # 🔐 ACCOUNT SECTION
    st.markdown("### 🔐 Account")
    if "user" not in st.session_state:
        auth_mode = st.radio("Mode", ["Login", "Register"], label_visibility="collapsed")
        user_input = st.text_input("Username")
        pw_input = st.text_input("Password", type="password")

        if auth_mode == "Register":
            if st.button("Create Account", use_container_width=True):
                users = pd.read_csv(USERS_FILE)
                if user_input in users["username"].values: st.error("User already exists")
                else:
                    new_user = pd.DataFrame([[user_input, pw_input]], columns=["username", "password"])
                    pd.concat([users, new_user]).to_csv(USERS_FILE, index=False)
                    st.success("Account created!")
        else:
            if st.button("Sign In", use_container_width=True):
                users = pd.read_csv(USERS_FILE)
                valid = users[(users["username"] == user_input) & (users["password"] == pw_input)]
                if not valid.empty:
                    st.session_state["user"] = user_input
                    st.rerun()
                else: st.error("Invalid credentials")
    else:
        st.write(f"Logged in as: **{st.session_state['user']}**")
        if st.button("Logout", use_container_width=True):
            del st.session_state["user"]
            st.rerun()
        if st.button("⭐ My Favorites", use_container_width=True):
            st.session_state.view = "Favorites"
            st.rerun()

    st.divider()
    
    # 📑 MAIN MENU
    st.markdown("### 📑 Navigation")
    # Using clean names for the view state
    nav_options = ["Dashboard", "Market Trends", "Top Genres", "Developers", "Price Analysis"]
    st.session_state.view = st.selectbox("Switch View", nav_options, index=nav_options.index(st.session_state.view) if st.session_state.view in nav_options else 0)

    if not df_listado.empty:
        dates = sorted(df_listado["Fecha"].unique(), reverse=True)
        sel_date = st.selectbox("Select Date", dates)

    if st.button("🏠 Reset to Home", use_container_width=True): 
        st.session_state.selected_game = None
        st.session_state.view = "Dashboard"
        st.rerun()

# ---------- ROUTING LOGIC ----------

# 1. FAVORITES VIEW
if st.session_state.view == "Favorites":
    st.title("⭐ My Favorite Games")
    if "user" not in st.session_state:
        st.warning("Please login to view favorites")
    else:
        favs = pd.read_csv(FAV_FILE)
        user_favs = favs[favs["username"] == st.session_state["user"]]
        if user_favs.empty: st.info("No favorites added yet.")
        else:
            for i, row in user_favs.iterrows():
                aid = int(row["appid"])
                c1, c2, c3 = st.columns([1, 4, 1])
                with c1: st.image(get_game_image(aid))
                with c2: st.markdown(f"**AppID:** {aid}")
                with c3:
                    if st.button("🗑️", key=f"del_{aid}_{i}"):
                        favs = favs[~((favs["username"] == st.session_state["user"]) & (favs["appid"] == aid))]
                        favs.to_csv(FAV_FILE, index=False)
                        st.rerun()
    st.stop()

# 2. GAME DETAIL VIEW
if st.session_state.selected_game:
    appid = st.session_state.selected_game
    g_l = df_listado[df_listado["AppID"] == appid].iloc[0] if not df_listado[df_listado["AppID"] == appid].empty else None
    g_i = df_info[df_info["AppID"] == appid].iloc[0] if not df_info[df_info["AppID"] == appid].empty else pd.Series()
    g_d = df_detalles[df_detalles["AppID"] == appid].iloc[0] if not df_detalles[df_detalles["AppID"] == appid].empty else pd.Series()

    st.title(f"🎮 {fix_nan(g_l['Nombre'] if g_l is not None else 'Game Detail')}")
    ca, cb = st.columns([1.5, 1])
    with ca:
        st.markdown(f'<img src="{get_game_background(appid)}" onerror="this.src=\'{IMG_ERROR}\';" style="width:100%; border-radius:10px;">', unsafe_allow_html=True)
        st.subheader("📋 Technical Info")
        st.write(f"**Developer:** {fix_nan(g_i.get('Desarrollador'))}")
        st.write(f"**Genres:** {fix_nan(g_i.get('Géneros'))}")
        st.write("**Platforms:**")
        p_str = fix_nan(g_i.get('Plataformas'), "").lower()
        pc1, pc2, pc3 = st.columns([1, 1, 8])
        if "win" in p_str: pc1.image(LOGOS["windows"], width=30)
        if "mac" in p_str or "apple" in p_str: pc2.image(LOGOS["mac"], width=25)
    with cb:
        st.image(get_game_image(appid), use_container_width=True)
        st.subheader("📊 Statistics")
        st.metric("Estimated Price", format_usd(g_d.get('Precio', 'N/A')))
        st.metric("User Rating", f"⭐ {fix_nan(g_d.get('Rating'))}/100")
        st.metric("Reviews", f"💬 {fix_nan(g_d.get('Reviews'))}")
        st.link_button("🚀 Open Steam Store", f"https://store.steampowered.com/app/{appid}", use_container_width=True)
    st.stop()

# 3. ANALYTICS VIEWS
df_day = df_listado[df_listado["Fecha"] == sel_date].copy()

if st.session_state.view == "Market Trends":
    st.title("💸 Current Sales & Market")
    if not df_detalles.empty:
        st.dataframe(df_detalles[['Nombre', 'Precio', 'Rating', 'Reviews']], use_container_width=True, hide_index=True)
    st.stop()

elif st.session_state.view == "Top Genres":
    st.title("📂 Genre Popularity")
    if not df_info.empty:
        counts = df_info['Géneros'].str.split(', ').explode().value_counts()
        st.bar_chart(counts)
        st.dataframe(df_info[['Nombre', 'Géneros', 'Desarrollador']], use_container_width=True)
    st.stop()

elif st.session_state.view == "Developers":
    st.title("👨‍💻 Industry Leaders")
    if not df_info.empty:
        devs = df_info['Desarrollador'].value_counts().head(20)
        st.bar_chart(devs)
        st.dataframe(df_info[['Desarrollador', 'Nombre']], use_container_width=True)
    st.stop()

elif st.session_state.view == "Price Analysis":
    st.title("💰 Price Distribution")
    if not df_detalles.empty:
        df_p = df_detalles.copy()
        df_p['Price_Val'] = df_p['Precio'].apply(convert_to_usd_numeric)
        st.subheader("Highest Priced Games in Rankings")
        st.bar_chart(df_p.sort_values('Price_Val', ascending=False).head(20).set_index('Nombre')['Price_Val'])
    st.stop()

# 4. MAIN DASHBOARD (HOME)
st.title("🎮 infosteam")
m1, m2, m3 = st.columns(3)
m1.metric("🟢 Active Players", f"{int(df_day['JugadoresConcurrentes'].sum()):,}")
m2.metric("🎮 Tracked Titles", f"{len(df_day)}")
m3.metric("🏆 Daily King", fix_nan(df_day.iloc[0]["Nombre"]))
st.divider()

t1, t2, t3 = st.tabs(["📊 Live Rankings", "📈 Performance Trend", "📋 Data Explorer"])

with t1:
    limit = 50 if st.session_state.show_more else 10
    top_df = df_day.head(limit).reset_index(drop=True)
    for r in range(0, len(top_df), 5):
        cols = st.columns(5)
        for i, col in enumerate(cols):
            idx = r + i
            if idx < len(top_df):
                game = top_df.iloc[idx]
                aid = game.get("AppID", 0)
                with col:
                    st.markdown(f'<div style="height: 140px; overflow: hidden; border-radius: 5px; background: #161921;"><img src="{get_game_image(aid)}" onerror="this.src=\'{IMG_ERROR}\';" style="width: 100%; height: 100%; object-fit: cover;"></div>', unsafe_allow_html=True)
                    st.markdown(f"**#{int(game.get('Posicion', 0))} {fix_nan(game.get('Nombre'))}**")
                    if st.button("Details", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.selected_game = int(aid)
                        st.rerun()
                    if "user" in st.session_state:
                        if st.button("❤️ Favorite", key=f"fav_{idx}", use_container_width=True):
                            f_df = pd.read_csv(FAV_FILE)
                            new_fav = pd.DataFrame([[st.session_state["user"], aid]], columns=["username","appid"])
                            pd.concat([f_df, new_fav]).drop_duplicates().to_csv(FAV_FILE, index=False)
                            st.toast("Added to favorites!", icon="✅")
                    st.caption(f"👥 {int(game.get('JugadoresConcurrentes', 0)):,} players")
    if st.button("Expand to Top 50" if not st.session_state.show_more else "Show Top 10"):
        st.session_state.show_more = not st.session_state.show_more
        st.rerun()

with t2:
    dates_list = sorted(df_listado["Fecha"].unique(), reverse=True)
    d_idx = dates_list.index(sel_date)
    tr_dates = dates_list[max(0, d_idx):min(len(dates_list), d_idx + 7)]
    df_tr = df_listado[df_listado["Fecha"].isin(tr_dates)].copy()
    sel_g = st.multiselect("Compare Titles:", sorted(df_tr["Nombre"].unique()), default=df_day.head(5)["Nombre"].tolist())
    if sel_g:
        st.line_chart(df_tr[df_tr["Nombre"].isin(sel_g)].pivot_table(index="Fecha", columns="Nombre", values="JugadoresConcurrentes"))

with t3:
    st.dataframe(df_day[["Posicion", "Nombre", "JugadoresConcurrentes", "AppID"]], use_container_width=True, hide_index=True)

st.divider()
st.caption("© 2026 infosteam — High-Fidelity Steam Data Monitoring")

