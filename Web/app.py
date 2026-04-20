import streamlit as st
import pandas as pd
import os
import re
import subprocess
import sys
from datetime import datetime

# ---------- CONFIG ----------
st.set_page_config(
    page_title="infosteam | Dashboard Profesional",
    page_icon="🎮",
    layout="wide"
)

IMG_ERROR = "https://i.imgur.com/8N9V6vT.png"

LOGOS = {
    "windows": "https://img.icons8.com/color/48/000000/windows-10.png",
    "mac": "https://img.icons8.com/ios-filled/50/ffffff/mac-os.png",
    "linux": "https://img.icons8.com/color/48/000000/tux.png"
}

# ---------- PATHS ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "Clean")
SRC_DIR = os.path.join(BASE_DIR, "Src")

DOWNLOAD_SCRIPT = os.path.join(SRC_DIR, "download.py")

# ---------- HELPERS ----------
def fix_nan(val, default="-"):
    if pd.isna(val) or str(val).lower() == "nan" or str(val).strip() == "":
        return default
    return str(val)

def convert_to_usd(price_str):
    if pd.isna(price_str) or str(price_str).lower() == "nan":
        return "N/A"

    p = str(price_str).upper()

    if any(x in p for x in ["GRATIS", "FREE", "0"]):
        return "Free to Play"

    try:
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", p.replace(",", "."))
        if not nums:
            return p

        val = float(nums[0])

        rates = {
            "€": 1.08,
            "฿": 0.028,
            "РУБ": 0.011,
            "AED": 0.27,
            "CLP": 0.0011,
            "CDN$": 0.74,
            "¥": 0.0067
        }

        for s, r in rates.items():
            if s in p:
                return f"${round(val * r, 2)}"

        return f"${val}"
    except:
        return p

def get_game_image(appid):
    try:
        return f"https://cdn.akamai.steamstatic.com/steam/apps/{int(float(appid))}/header.jpg"
    except:
        return IMG_ERROR

def get_game_background(appid):
    try:
        return f"https://cdn.akamai.steamstatic.com/steam/apps/{int(float(appid))}/page_bg_generated_v6b.jpg"
    except:
        return IMG_ERROR


# ---------- LOAD DATA ----------
@st.cache_data(ttl=300)
def load_data():
    try:
        df_l = pd.read_csv(os.path.join(CLEAN_DIR, "listado_juegos.csv"))
        df_i = pd.read_csv(os.path.join(CLEAN_DIR, "info_juegos.csv"))
        df_d = pd.read_csv(os.path.join(CLEAN_DIR, "detalles_juegos.csv"), on_bad_lines="skip")

        for df in [df_l, df_i, df_d]:
            if not df.empty and "AppID" in df.columns:
                df["AppID"] = pd.to_numeric(df["AppID"], errors="coerce").fillna(0).astype(int)

        return df_l, df_i, df_d
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_listado, df_info, df_detalles = load_data()


# ---------- SESSION ----------
if "selected_game" not in st.session_state:
    st.session_state.selected_game = None

if "show_more" not in st.session_state:
    st.session_state.show_more = False

if "last_update" not in st.session_state:
    st.session_state.last_update = None


# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("📑 Menú")

    # última actualización
    if st.session_state.last_update:
        st.caption(f"🕒 Última actualización: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.caption("🕒 Última actualización: nunca")

    # ---------- BOTÓN UPDATE REAL ----------
    if st.button("🔄 Actualizar datos ahora", use_container_width=True):
        with st.spinner("Ejecutando download.py..."):
            try:
                result = subprocess.run(
                    [sys.executable, DOWNLOAD_SCRIPT],
                    capture_output=True,
                    text=True,
                    cwd=BASE_DIR,
                    timeout=300
                )
                
                st.write("### 📄 LOG")
                st.code(result.stdout if result.stdout else "Sin output")
                
                if result.returncode != 0:
                    st.error("❌ Error ejecutando download.py")
                    st.code(result.stderr if result.stderr else "Sin error details")
                else:
                    st.success("✅ Datos actualizados correctamente")
                    st.session_state.last_update = datetime.now()
                    st.cache_data.clear()
                    st.rerun()
            except subprocess.TimeoutExpired:
                st.error("❌ Timeout: el script tardó demasiado tiempo")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    if st.button("🏠 Inicio"):
        st.session_state.selected_game = None
        st.session_state.show_more = False
        st.rerun()


# ---------- VISTA DETALLE ----------
if st.session_state.selected_game:
    appid = st.session_state.selected_game

    g_l = df_listado[df_listado["AppID"] == appid]
    g_l = g_l.iloc[0] if not g_l.empty else None

    g_i = df_info[df_info["AppID"] == appid]
    g_i = g_i.iloc[0] if not g_i.empty else pd.Series()

    g_d = df_detalles[df_detalles["AppID"] == appid]
    g_d = g_d.iloc[0] if not g_d.empty else pd.Series()

    st.title(f"🎮 {fix_nan(g_l['Nombre'] if g_l is not None else 'Juego')}")

    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.image(get_game_background(appid), use_container_width=True)
        st.subheader("📋 Info")
        st.write(f"Desarrollador: {fix_nan(g_i.get('Desarrollador'))}")

    with col2:
        st.image(get_game_image(appid), use_container_width=True)
        st.metric("Precio", convert_to_usd(g_d.get("Precio")))
        st.metric("Rating", fix_nan(g_d.get("Rating")))
        st.metric("Reviews", fix_nan(g_d.get("Reviews")))

        st.link_button("Steam", f"https://store.steampowered.com/app/{appid}")

    st.stop()


# ---------- MAIN ----------
st.title("🎮 infosteam")

if df_listado.empty:
    st.stop()

dates = sorted(df_listado["Fecha"].unique(), reverse=True)
sel_date = dates[0]

df_day = df_listado[df_listado["Fecha"] == sel_date]

# metrics
c1, c2, c3 = st.columns(3)
c1.metric("Players", int(df_day["JugadoresConcurrentes"].sum()))
c2.metric("Games", len(df_day))
c3.metric("Top 1", fix_nan(df_day.iloc[0]["Nombre"]))

st.divider()

# ---------- TABLE ----------
limit = 50 if st.session_state.show_more else 10
top = df_day.head(limit)

for i in range(0, len(top), 5):
    cols = st.columns(5)

    for j, col in enumerate(cols):
        idx = i + j
        if idx < len(top):
            game = top.iloc[idx]
            appid = game["AppID"]

            with col:
                st.image(get_game_image(appid), use_container_width=True)
                st.write(f"#{game['Posicion']} {game['Nombre']}")

                if st.button("+ info", key=f"g_{idx}"):
                    st.session_state.selected_game = appid
                    st.rerun()

                st.caption(f"{game['JugadoresConcurrentes']:,}")

if not st.session_state.show_more:
    if st.button("Mostrar más"):
        st.session_state.show_more = True
        st.rerun()

st.divider()
st.caption("© 2026 infosteam")