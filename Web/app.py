import streamlit as st
import pandas as pd
import os
import re
import subprocess
from datetime import datetime

# ---------- CONFIGURACIÓN ----------
st.set_page_config(page_title="infosteam | Dashboard", page_icon="🎮", layout="wide")

# ---------- FUNCIÓN PARA EJECUTAR PIPELINE ----------
def run_pipeline():
    try:
        result = subprocess.run(
            ["python", "data_pipeline.py"],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        return str(e)

# Iconos de plataforma
LOGOS = {
    "windows": "https://img.icons8.com/color/48/000000/windows-10.png",
    "mac": "https://img.icons8.com/ios-filled/50/ffffff/mac-os.png",
    "linux": "https://img.icons8.com/color/48/000000/tux.png"
}

# ---------- FUNCIONES ----------
def fix_nan(val, default="-"):
    if pd.isna(val) or str(val).lower() == "nan" or str(val).strip() == "":
        return default
    return str(val)

def convert_to_usd(price_str):
    if pd.isna(price_str) or str(price_str).lower() == "nan": return "N/A"
    p = str(price_str).upper()
    if any(word in p for word in ["GRATIS", "FREE", "0"]): return "Free to Play"
    try:
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", p.replace(',', '.'))
        if not nums: return p
        val = float(nums[0])
        rates = {"€": 1.08, "฿": 0.028, "РУБ": 0.011, "AED": 0.27, "CLP": 0.0011, "CDN$": 0.74, "¥": 0.0067}
        for s, r in rates.items():
            if s in p: return f"${round(val * r, 2)}"
        return f"${val}"
    except:
        return p

def get_game_image(appid):
    if pd.isna(appid) or str(appid) == "0" or not str(appid).isdigit():
        return "https://i.imgur.com/8N9V6vT.png"
    return f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"

def get_game_background(appid):
    if pd.isna(appid) or str(appid) == "0" or not str(appid).isdigit():
        return "https://i.imgur.com/8N9V6vT.png"
    return f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/page_bg_generated_v6b.jpg"

# ---------- CARGA DE DATOS ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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
    except Exception as e:
        st.error(f"Error cargando archivos: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_listado, df_info, df_detalles = load_data()

# ---------- SESSION ----------
if "selected_game" not in st.session_state: st.session_state.selected_game = None
if "show_more" not in st.session_state: st.session_state.show_more = False

# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("📑 Menú")

    st.caption(f"Última carga: {datetime.now().strftime('%H:%M:%S')}")

    # 🔥 BOTÓN IMPORTANTE
    if st.button("🔄 Actualizar datos", use_container_width=True):
        with st.spinner("Actualizando datos..."):
            output = run_pipeline()
            st.cache_data.clear()
            st.success("Datos actualizados")

            with st.expander("📜 Ver logs"):
                st.text(output)

            st.rerun()

    st.divider()

    with st.expander("ℹ️ About", expanded=True):
        st.write("• Blog\n• Discord\n• Social Media")

    with st.expander("🏆 Rankings", expanded=True):
        if not df_listado.empty:
            dates = sorted(df_listado["Fecha"].unique(), reverse=True)
            sel_date = st.selectbox("Fecha", dates)

    if st.button("🏠 Home"):
        st.session_state.selected_game = None
        st.session_state.show_more = False
        st.rerun()

# ---------- DETALLE ----------
if st.session_state.selected_game:
    appid = st.session_state.selected_game

    g_l_row = df_listado[df_listado["AppID"] == appid]
    g_l = g_l_row.iloc[0] if not g_l_row.empty else None

    g_i_row = df_info[df_info["AppID"] == appid]
    g_i = g_i_row.iloc[0] if not g_i_row.empty else pd.Series()

    g_d_row = df_detalles[df_detalles["AppID"] == appid]
    g_d = g_d_row.iloc[0] if not g_d_row.empty else pd.Series()

    st.title(f"🎮 {fix_nan(g_l['Nombre'] if g_l is not None else 'Detalle')}")

    c1, c2 = st.columns([1.5, 1])

    with c1:
        st.image(get_game_background(appid), use_container_width=True)
        st.subheader("📋 Información Técnica")
        st.write(f"**Desarrollador:** {fix_nan(g_i.get('Desarrollador'))}")
        st.write(f"**Géneros:** {fix_nan(g_i.get('Géneros'))}")

    with c2:
        st.image(get_game_image(appid), use_container_width=True)
        st.subheader("📊 Valoraciones")

        precio_usd = convert_to_usd(g_d.get('Precio', 'N/A'))

        st.metric("Precio Est.", precio_usd)
        st.metric("Rating", f"⭐ {fix_nan(g_d.get('Rating'))}/100")
        st.metric("Reseñas", f"💬 {fix_nan(g_d.get('Reviews'))}")

        st.link_button("🚀 Ver en Steam", f"https://store.steampowered.com/app/{appid}")

    st.stop()

# ---------- DASHBOARD ----------
st.title("🎮 infosteam")

if df_listado.empty:
    st.warning("No hay datos disponibles.")
    st.stop()

df_day = df_listado[df_listado["Fecha"] == sel_date].copy()

m1, m2, m3 = st.columns(3)
m1.metric("🟢 Online", f"{int(df_day['JugadoresConcurrentes'].sum()):,}")
m2.metric("🎮 Tracked", f"{len(df_day)}")
m3.metric("🏆 King", fix_nan(df_day.iloc[0]["Nombre"] if not df_day.empty else "N/A"))

st.divider()

t1, t2, t3 = st.tabs(["📊 Rankings", "📈 Trend", "📋 Data"])

with t1:
    top_df = df_day.head(10)

    for i in range(len(top_df)):
        game = top_df.iloc[i]
        st.write(f"#{game['Posicion']} - {game['Nombre']} ({game['JugadoresConcurrentes']:,})")

with t2:
    st.line_chart(df_day.head(5).set_index("Nombre")["JugadoresConcurrentes"])

with t3:
    st.dataframe(df_day)

st.divider()
st.caption("© 2026 infosteam")