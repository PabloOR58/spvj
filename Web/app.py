import streamlit as st
import pandas as pd
import os
import re

# ---------- CONFIGURACIÓN ----------
st.set_page_config(page_title="infosteam - Pro Dashboard", page_icon="🎮", layout="wide")

# Iconos de plataforma (URLs estables)
LOGOS = {
    "windows": "https://img.icons8.com/color/48/000000/windows-10.png",
    "mac": "https://img.icons8.com/ios-filled/50/ffffff/mac-os.png",
    "linux": "https://img.icons8.com/color/48/000000/tux.png"
}

# ---------- FUNCIONES ----------
def convert_to_usd(price_str):
    if pd.isna(price_str) or price_str == "" or price_str == "N/A": return "N/A"
    p = str(price_str).replace('"', '').replace("'", "").upper()
    if any(word in p for word in ["GRATIS", "FREE", "0"]): return "Free to Play"
    try:
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", p.replace(',', '.'))
        if not nums: return p
        val = float(nums[0])
        rates = {"€": 1.08, "฿": 0.028, "РУБ": 0.011, "AED": 0.27, "CLP": 0.0011, "CDN$": 0.74, "¥": 0.0067}
        for s, r in rates.items():
            if s in p: return f"${round(val * r, 2)}"
        return f"${val}"
    except: return p

def get_game_image(appid): return f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"
def get_game_background(appid): return f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/page_bg_generated_v6b.jpg"

# ---------- CARGA DE DATOS ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "Clean")

@st.cache_data(ttl=300)
def load_data():
    df_l = pd.read_csv(os.path.join(CLEAN_DIR, "listado_juegos.csv")) if os.path.exists(os.path.join(CLEAN_DIR, "listado_juegos.csv")) else pd.DataFrame()
    df_i = pd.read_csv(os.path.join(CLEAN_DIR, "info_juegos.csv")) if os.path.exists(os.path.join(CLEAN_DIR, "info_juegos.csv")) else pd.DataFrame()
    df_d = pd.read_csv(os.path.join(CLEAN_DIR, "detalles_juegos.csv"), on_bad_lines="skip") if os.path.exists(os.path.join(CLEAN_DIR, "detalles_juegos.csv")) else pd.DataFrame()
    if not df_d.empty:
        df_d['AppID'] = pd.to_numeric(df_d['AppID'], errors='coerce')
        df_d['Precio_USD'] = df_d['Precio'].apply(convert_to_usd)
    return df_l, df_i, df_d

df_listado, df_info, df_detalles = load_data()

# ---------- NAVEGACIÓN ----------
if "selected_game" not in st.session_state: st.session_state.selected_game = None

# Sidebar (Menú según tu boceto)
with st.sidebar:
    st.title("📑 Menú")
    with st.expander("ℹ️ About", expanded=True): st.write("• Blog\n• Discord\n• Social Media")
    with st.expander("👤 Account", expanded=True): st.button("Sign in via Steam", use_container_width=True)
    with st.expander("🏆 Rankings", expanded=True):
        if not df_listado.empty:
            dates = sorted(df_listado["Fecha"].unique(), reverse=True)
            sel_date = st.selectbox("Fecha", dates)
        st.write("• Genres\n• Developers\n• Price")
    if st.button("🏠 Home"): 
        st.session_state.selected_game = None
        st.rerun()

# ---------- PANTALLA DE DETALLE (+ INFO) ----------
if st.session_state.selected_game:
    appid = st.session_state.selected_game
    g_l = df_listado[df_listado["AppID"] == appid].iloc[0] if appid in df_listado["AppID"].values else None
    g_i = df_info[df_info["AppID"] == appid].iloc[0] if appid in df_info["AppID"].values else None
    g_d = df_detalles[df_detalles["AppID"] == appid].iloc[0] if appid in df_detalles["AppID"].values else None

    st.title(f"🎮 {g_l['Nombre'] if g_l is not None else 'Detalle'}")
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.image(get_game_background(appid), use_container_width=True)
        st.subheader("📋 Información")
        if g_i is not None:
            st.write(f"**Desarrollador:** {g_i.get('Desarrollador', 'N/A')}")
            st.write(f"**Géneros:** {g_i.get('Géneros', 'N/A')}")
            st.write("**Plataformas:**")
            p_str = str(g_i.get('Plataformas', '')).lower()
            l_cols = st.columns(10)
            if "windows" in p_str or "win" in p_str: l_cols[0].image(LOGOS["windows"], width=35)
            if "mac" in p_str or "apple" in p_str: l_cols[1].image(LOGOS["mac"], width=30)
            if "linux" in p_str: l_cols[2].image(LOGOS["linux"], width=35)
    with c2:
        st.image(get_game_image(appid), use_container_width=True)
        if g_d is not None:
            st.metric("Precio", g_d.get('Precio_USD', 'N/A'))
            # Búsqueda flexible de Rating y Reviews
            r_val = g_d.get('Rating', 'N/A')
            rev_val = g_d.get('Reviews', 'N/A')
            st.metric("Rating", f"⭐ {r_val}/100")
            st.metric("Reseñas", f"💬 {rev_val}")
        st.link_button("🚀 Ver en Steam", f"https://store.steampowered.com/app/{appid}", use_container_width=True)
    st.stop()

# ---------- PANTALLA PRINCIPAL ----------
st.title("🎮 infosteam")
if df_listado.empty: st.stop()

df_day = df_listado[df_listado["Fecha"] == sel_date].copy()

# Pestañas principales con la nueva pestaña de Sales
t1, t2, t3, t4 = st.tabs(["📊 Rankings", "📈 Tendencia", "📋 Datos", "💸 Sales"])

with t1:
    top10 = df_day.head(10).reset_index(drop=True)
    for r in range(0, 10, 5):
        cols = st.columns(5)
        for i, col in enumerate(cols):
            idx = r + i
            if idx < len(top10):
                game = top10.iloc[idx]
                with col:
                    st.image(get_game_image(game["AppID"]), use_container_width=True)
                    st.markdown(f"**#{int(game['Posicion'])} {game['Nombre']}**")
                    if st.button("+ info", key=f"b_{game['AppID']}", use_container_width=True):
                        st.session_state.selected_game = game["AppID"]
                        st.rerun()
                    st.caption(f"👥 {int(game['JugadoresConcurrentes']):,} jug.")

with t2:
    st.subheader("Tendencia de Jugadores")
    st.line_chart(df_day.head(10).set_index("Nombre")["JugadoresConcurrentes"])

with t3:
    st.dataframe(df_day[["Posicion", "Nombre", "JugadoresConcurrentes", "AppID"]], use_container_width=True, hide_index=True)

with t4:
    st.subheader("💸 Ofertas y Descuentos")
    if not df_detalles.empty:
        # Unión flexible para mostrar lanzamiento si existe
        l_col = 'Lanzamiento' if 'Lanzamiento' in df_info.columns else 'Fecha'
        df_m = pd.merge(df_detalles, df_info[['AppID', l_col]] if l_col in df_info.columns else df_info[['AppID']], on='AppID', how='left')
        
        txt = st.text_input("Filtrar por nombre:")
        res = df_m[df_m['Nombre'].str.contains(txt, case=False, na=False)] if txt else df_m
        
        # Columnas finales de la tabla de ventas
        cols_mostrar = ['Nombre', 'Precio', 'Precio_USD', 'Rating']
        if l_col in res.columns: cols_mostrar.append(l_col)
        
        st.dataframe(res[cols_mostrar], use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos de detalles disponibles para mostrar ofertas.")

st.divider()
<<<<<<< HEAD
st.caption("© 2026 infosteam — Data from Steam Web API")
=======
st.caption("© 2026 infosteam — Dashboard de Seguimiento de Steam")
>>>>>>> main
