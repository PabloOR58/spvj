import streamlit as st
import pandas as pd
import os
import re

# ---------- CONFIGURACIÓN SEO Y PÁGINA ----------
st.set_page_config(
    page_title="infosteam | Dashboard Profesional",
    page_icon="🎮",
    layout="wide"
)

# Imagen de reserva robusta (Placeholder si Steam falla)
IMG_ERROR = "https://i.imgur.com/8N9V6vT.png"

# ---------- LOGIN / FAVORITOS ----------
USERS_FILE = "users.csv"
FAV_FILE = "favoritos.csv"

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

# ---------- FUNCIONES CORREGIDAS ----------
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
    except: return p

def get_game_image(appid):
    """Genera la URL de la carátula con validación y fallback."""
    try:
        if not appid or pd.isna(appid) or int(float(appid)) == 0:
            return IMG_ERROR
        return f"https://cdn.akamai.steamstatic.com/steam/apps/{int(float(appid))}/header.jpg"
    except:
        return IMG_ERROR

def get_game_background(appid):
    """Genera la URL del fondo con fallback."""
    try:
        if not appid or pd.isna(appid) or int(float(appid)) == 0:
            return IMG_ERROR
        return f"https://cdn.akamai.steamstatic.com/steam/apps/{int(float(appid))}/page_bg_generated_v6b.jpg"
    except:
        return IMG_ERROR

# ---------- CARGA DE DATOS ----------
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

# ---------- SESSION ----------
if "selected_game" not in st.session_state: st.session_state.selected_game = None
if "show_more" not in st.session_state: st.session_state.show_more = False
if "view" not in st.session_state: st.session_state.view = "home"

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 🔐 Cuenta")
    if "user" not in st.session_state:
        option = st.radio("Opciones", ["Login", "Registro"])
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if option == "Registro":
            if st.button("Crear cuenta"):
                users = pd.read_csv(USERS_FILE)
                if username in users["username"].values:
                    st.error("El usuario ya existe")
                else:
                    users.loc[len(users)] = [username, password]
                    users.to_csv(USERS_FILE, index=False)
                    st.success("Usuario creado")
        else:
            if st.button("Iniciar sesión"):
                users = pd.read_csv(USERS_FILE)
                user = users[(users["username"] == username) & (users["password"] == password)]
                if not user.empty:
                    st.session_state["user"] = username
                    st.success("Sesión iniciada")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    else:
        st.success(f"👤 {st.session_state['user']}")
        if st.button("Cerrar sesión"):
            del st.session_state["user"]
            st.rerun()
        if st.button("⭐ Favoritos"):
            st.session_state.view = "favoritos"
            st.rerun()

    st.title("📑 Menú")
    with st.expander("ℹ️ About", expanded=True): st.write("• Blog\n• Discord\n• Social Media")
    with st.expander("🏆 Rankings", expanded=True):
        if not df_listado.empty:
            dates = sorted(df_listado["Fecha"].unique(), reverse=True)
            sel_date = st.selectbox("Seleccionar Fecha:", dates)
    if st.button("🏠 Volver al Inicio"): 
        st.session_state.selected_game = None
        st.session_state.show_more = False
        st.session_state.view = "home"
        st.rerun()

# ---------- VISTA FAVORITOS ----------
if st.session_state.view == "favoritos":
    st.title("⭐ Mis juegos favoritos")
    if "user" not in st.session_state:
        st.warning("Debes iniciar sesión")
        st.stop()
    favs = pd.read_csv(FAV_FILE)
    user_favs = favs[favs["username"] == st.session_state["user"]]
    if user_favs.empty:
        st.info("No hay juegos en favoritos")
    else:
        for i, row in user_favs.iterrows():
            appid = int(row["appid"])
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.image(get_game_image(appid), use_container_width=True)
            with col2:
                st.write(f"🎮 AppID: {appid}")
            with col3:
                if st.button("❌", key=f"del_{appid}_{i}"):
                    favs = favs[~((favs["username"] == st.session_state["user"]) & (favs["appid"] == appid))]
                    favs.to_csv(FAV_FILE, index=False)
                    st.rerun()
    if st.button("⬅