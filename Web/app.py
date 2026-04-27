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
    try: return f"https://cdn.akamai.steamstatic.com/steam/apps/{int(float(appid))}/header.jpg"
    except: return IMG_ERROR

def get_game_background(appid):
    try: return f"https://cdn.akamai.steamstatic.com/steam/apps/{int(float(appid))}/page_bg_generated_v6b.jpg"
    except: return IMG_ERROR

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

# ---------- 5. SESSION STATE ----------
if "selected_game" not in st.session_state: st.session_state.selected_game = None
if "show_more" not in st.session_state: st.session_state.show_more = False
if "view" not in st.session_state: st.session_state.view = "Dashboard"

# ---------- 6. SIDEBAR ----------
with st.sidebar:
    st.title("🎮 infosteam")
    
    st.markdown("### 🔐 Account")
    if "user" not in st.session_state:
        auth_mode = st.radio("Mode", ["Login", "Register"], label_visibility="collapsed")
        u_name = st.text_input("User")
        u_pass = st.text_input("Password", type="password")

        if auth_mode == "Register":
            if st.button("Create Account", use_container_width=True):
                users = pd.read_csv(USERS_FILE)
                if u_name in users["username"].values: st.error("User exists!")
                else:
                    new_u = pd.DataFrame([[u_name, u_pass]], columns=["username", "password"])
                    pd.concat([users, new_u]).to_csv(USERS_FILE, index=False)
                    st.success("User registered!")
        else:
            if st.button("Login", use_container_width=True):
                users = pd.read_csv(USERS_FILE)
                valid = users[(users["username"] == u_name) & (users["password"] == u_pass)]
                if not valid.empty:
                    st.session_state["user"] = u_name
                    st.rerun()
                else: st.error("Wrong credentials")
    else:
        st.success(f"👤 Welcome, {st.session_state['user']}")
        if st.button("Logout", use_container_width=True):
            del st.session_state["user"]
            st.rerun()
        if st.button("⭐ My Favorites", use_container_width=True):
            st.session_state.view = "Favorites"
            st.rerun()

    st.divider()
    st.markdown("### 📑 Navigation")
    sections = ["Dashboard", "Market Trends", "Top Genres", "Top Developers", "Price Analysis"]
    st.session_state.view = st.selectbox("Menu", sections, index=sections.index(st.session_state.view) if st.session_state.view in sections else 0)

    if not df_listado.empty:
        dates = sorted(df_listado["Fecha"].unique(), reverse=True)
        sel_date = st.selectbox("Select Date:", dates)

    if st.button("🏠 Home Dashboard", use_container_width=True): 
        st.session_state.selected_game = None
        st.session_state.view = "Dashboard"
        st.rerun()

# ---------- 7. VIEW: FAVORITES (CORRECTED) ----------
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
                g_name = df_listado[df_listado["AppID"] == aid]["Nombre"].iloc[0] if not df_listado[df_listado["AppID"] == aid].empty else f"AppID: {aid}"
                
                c1, c2, c3 = st.columns([1, 4, 1])
                with c1: st.image(get_game_image(aid))
                with c2: st.markdown(f"### {g_name}")
                with c3:
                    if st.button("🗑️ Remove", key=f"del_{aid}_{idx}", use_container_width=True):
                        favs_df = favs_df.drop(idx)
                        favs_df.to_csv(FAV_FILE, index=False)
                        st.rerun()
    st.stop()

# ---------- 8. VIEW: GAME DETAIL ----------
if st.session_state.selected_game:
    appid = st.session_state.selected_game
    g_l = df_listado[df_listado["AppID"] == appid].iloc[0] if not df_listado[df_listado["AppID"] == appid].empty else None
    g_i = df_info[df_info["AppID"] == appid].iloc[0] if not df_info[df_info["AppID"] == appid].empty else pd.Series()
    g_d = df_detalles[df_detalles["AppID"] == appid].iloc[0] if not df_detalles[df_detalles["AppID"] == appid].empty else pd.Series()

    st.title(f"🎮 {fix_nan(g_l['Nombre'] if g_l is not None else 'Game Details')}")
    ca, cb = st.columns([1.5, 1])
    with ca:
        st.markdown(f'<img src="{get_game_background(appid)}" onerror="this.src=\'{IMG_ERROR}\';" style="width:100%; border-radius:10px;">', unsafe_allow_html=True)
        st.subheader("📋 Information")
        st.write(f"**Developer:** {fix_nan(g_i.get('Desarrollador'))}")
        st.write(f"**Genres:** {fix_nan(g_i.get('Géneros'))}")
        p_str = fix_nan(g_i.get('Plataformas'), "").lower()
        pc = st.columns(10)
        if "win" in p_str: pc[0].image(LOGOS["windows"], width=35)
        if "mac" in p_str or "apple" in p_str: pc[1].image(LOGOS["mac"], width=30)
        if "linux" in p_str: pc[2].image(LOGOS["linux"], width=35)
    with cb:
        st.image(get_game_image(appid), use_container_width=True)
        st.metric("Price", format_usd(g_d.get('Precio', 'N/A')))
        st.metric("Rating", f"⭐ {fix_nan(g_d.get('Rating'))}/100")
        st.metric("Reviews", f"💬 {fix_nan(g_d.get('Reviews'))}")
        st.link_button("🚀 Open in Steam", f"https://store.steampowered.com/app/{appid}", use_container_width=True)
    st.stop()

# ---------- 9. ANALYTICS VIEWS ----------
df_day = df_listado[df_listado["Fecha"] == sel_date].copy()

if st.session_state.view == "Market Trends":
    st.title("📈 Market Trends & Sales")
    st.dataframe(df_detalles[['Nombre', 'Precio', 'Rating', 'Reviews']], use_container_width=True, hide_index=True)
    st.stop()

elif st.session_state.view == "Top Genres":
    st.title("📂 Genre Popularity")
    counts = df_info['Géneros'].str.split(', ').explode().value_counts()
    st.bar_chart(counts)
    st.dataframe(df_info[['Nombre', 'Géneros', 'Desarrollador']], use_container_width=True, hide_index=True)
    st.stop()

elif st.session_state.view == "Top Developers":
    st.title("👨‍💻 Top Developers")
    devs = df_info['Desarrollador'].value_counts().head(15)
    st.bar_chart(devs)
    st.dataframe(df_info[['Desarrollador', 'Nombre', 'Géneros']], use_container_width=True, hide_index=True)
    st.stop()

elif st.session_state.view == "Price Analysis":
    st.title("💰 Price Analysis")
    df_p = df_detalles.copy()
    df_p['Price_Val'] = df_p['Precio'].apply(convert_to_usd_numeric)
    st.bar_chart(df_p.sort_values('Price_Val', ascending=False).head(20).set_index('Nombre')['Price_Val'])
    st.dataframe(df_p[['Nombre', 'Precio', 'Rating']].sort_values('Price_Val', ascending=False), use_container_width=True, hide_index=True)
    st.stop()

# ---------- 10. MAIN DASHBOARD ----------
st.title("🎮 Dashboard")
m1, m2, m3 = st.columns(3)
m1.metric("🟢 Players Online", f"{int(df_day['JugadoresConcurrentes'].sum()):,}")
m2.metric("🎮 Games Tracked", f"{len(df_day)}")
m3.metric("🏆 King of the Day", fix_nan(df_day.iloc[0]["Nombre"]))
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
                aid = int(game.get("AppID", 0))
                with col:
                    st.markdown(f'<div style="height: 140px; overflow: hidden; border-radius: 5px; background: #161921;"><img src="{get_game_image(aid)}" onerror="this.src=\'{IMG_ERROR}\';" style="width: 100%; height: 100%; object-fit: cover;"></div>', unsafe_allow_html=True)
                    st.markdown(f"**#{int(game.get('Posicion', 0))} {fix_nan(game.get('Nombre'))}**")
                    if st.button("Details", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.selected_game = aid
                        st.rerun()
                    if "user" in st.session_state:
                        if st.button("❤️ Favorite", key=f"fav_{idx}", use_container_width=True):
                            f_df = pd.read_csv(FAV_FILE)
                            new_fav = pd.DataFrame([[st.session_state["user"], aid]], columns=["username","appid"])
                            pd.concat([f_df, new_fav]).drop_duplicates().to_csv(FAV_FILE, index=False)
                            st.toast(f"Saved: {game.get('Nombre')}")
                    st.caption(f"👥 {int(game.get('JugadoresConcurrentes', 0)):,} players")
    if st.button("Toggle Top 10 / 50"):
        st.session_state.show_more = not st.session_state.show_more
        st.rerun()

with t2:
    st.header("📈 Historical Trends & Market Share")
    dates_list = sorted(df_listado["Fecha"].unique(), reverse=True)
    d_idx = dates_list.index(sel_date)
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
    st.dataframe(df_day[["Posicion", "Nombre", "JugadoresConcurrentes", "AppID"]], use_container_width=True, hide_index=True)

st.divider()
st.caption("© 2026 infosteam — High-End Data Monitoring")



