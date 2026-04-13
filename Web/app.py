import streamlit as st
import pandas as pd
import os
import re

# ---------- CONFIGURACIÓN ----------
st.set_page_config(page_title="infosteam - Pro Dashboard", page_icon="🎮", layout="wide")

# Estilo para iconos de plataforma
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
    with st.expander("ℹ️ About"): st.write("Blog / Discord / Social")
    with st.expander("👤 Account"): st.button("Sign in via Steam", use_container_width=True)
    with st.expander("🏆 Rankings"):
        if not df_listado.empty:
            dates = sorted(df_listado["Fecha"].unique(), reverse=True)
            sel_date = st.selectbox("Fecha", dates)
        st.write("Genres / Developers / Price")
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
            # Logos de Plataforma
            st.write("**Plataformas:**")
            p_str = str(g_i.get('Plataformas', '')).lower()
            l_cols = st.columns(10)
            if "windows" in p_str or "win" in p_str: l_cols[0].image(LOGOS["windows"], width=35)
            if "mac" in p_str or "apple" in p_str: l_cols[1].image(LOGOS["mac"], width=30)
            if "linux" in p_str: l_cols[2].image(LOGOS["linux"], width=35)
    with c2:
        st.image(get_game_image(appid), use_container_width=True)
        if g_d is not None:
            st.metric("Precio", g_d['Precio_USD'])
            # Intentar sacar reseñas y rating con nombres de columna flexibles
            r_val = g_d.get('Rating', g_d.get('Valoración', 'N/A'))
            rev_val = g_d.get('Reviews', g_d.get('Reseñas', 'N/A'))
            st.metric("