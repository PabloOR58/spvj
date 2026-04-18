import streamlit as st
import pandas as pd
import os
import re

# ---------- CONFIGURACIÓN ----------
st.set_page_config(page_title="infosteam | Dashboard", page_icon="🎮", layout="wide")

# Iconos de plataforma
LOGOS = {
    "windows": "https://img.icons8.com/color/48/000000/windows-10.png",
    "mac": "https://img.icons8.com/ios-filled/50/ffffff/mac-os.png",
    "linux": "https://img.icons8.com/color/48/000000/tux.png"
}

# ---------- FUNCIONES DE LIMPIEZA (PARA EVITAR EL 'NAN') ----------
def fix_nan(val, default="-"):
    """Si el valor es NaN, nulo o 'nan', devuelve el valor por defecto."""
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
    if pd.isna(appid) or str(appid) == "0" or not str(appid).isdigit():
        return "https://i.imgur.com/8N9V6vT.png"
    return f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"

def get_game_background(appid):
    if pd.isna(appid) or str(appid) == "0" or not str(appid).isdigit():
        return "https://i.imgur.com/8N9V6vT.png"
    return f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/page_bg_generated_v6b.jpg"

# ---------- CARGA DE DATOS ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "Clean")

@st.cache_data(ttl=300)
def load_data():
    try:
        df_l = pd.read_csv(os.path.join(CLEAN_DIR, "listado_juegos.csv"))
        df_i = pd.read_csv(os.path.join(CLEAN_DIR, "info_juegos.csv"))
        df_d = pd.read_csv(os.path.join(CLEAN_DIR, "detalles_juegos.csv"), on_bad_lines="skip")
        
        # Normalizar AppIDs
        for df in [df_l, df_i, df_d]:
            if not df.empty and 'AppID' in df.columns:
                df['AppID'] = pd.to_numeric(df['AppID'], errors='coerce').fillna(0).astype(int)
        
        return df_l, df_i, df_d
    except Exception as e:
        st.error(f"Error cargando archivos: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_listado, df_info, df_detalles = load_data()

# ---------- NAVEGACIÓN ----------
if "selected_game" not in st.session_state: st.session_state.selected_game = None
if "show_more" not in st.session_state: st.session_state.show_more = False

with st.sidebar:
    st.title("📑 Menú")
    with st.expander("ℹ️ About", expanded=True): st.write("• Blog\n• Discord\n• Social Media")
    with st.expander("🏆 Rankings", expanded=True):
        if not df_listado.empty:
            dates = sorted(df_listado["Fecha"].unique(), reverse=True)
            sel_date = st.selectbox("Fecha", dates)
    if st.button("🏠 Home"): 
        st.session_state.selected_game = None
        st.session_state.show_more = False
        st.rerun()

# ---------- VISTA DETALLE (+ INFO) ----------
if st.session_state.selected_game:
    appid = st.session_state.selected_game
    
    # Obtener filas de forma segura
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
        
        st.write("**Plataformas:**")
        p_str = fix_nan(g_i.get('Plataformas'), "").lower()
        l_cols = st.columns(10)
        if "win" in p_str: l_cols[0].image(LOGOS["windows"], width=35)
        if "mac" in p_str or "apple" in p_str: l_cols[1].image(LOGOS["mac"], width=30)
        if "linux" in p_str: l_cols[2].image(LOGOS["linux"], width=35)

    with c2:
        st.image(get_game_image(appid), use_container_width=True)
        st.subheader("📊 Valoraciones")
        
        # Conversión de precio segura
        precio_raw = g_d.get('Precio', 'N/A')
        precio_usd = convert_to_usd(precio_raw)
        
        st.metric("Precio Est.", precio_usd)
        st.metric("Rating", f"⭐ {fix_nan(g_d.get('Rating'))}/100")
        st.metric("Reseñas", f"💬 {fix_nan(g_d.get('Reviews'))}")
        
        st.link_button("🚀 Ver en Steam", f"https://store.steampowered.com/app/{appid}", use_container_width=True)
    st.stop()

# ---------- DASHBOARD PRINCIPAL ----------
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

t1, t2, t3, t4 = st.tabs(["📊 Rankings", "📈 7-Day Trend", "📋 Data Table", "💸 Sales"])

with t1:
    num = 50 if st.session_state.show_more else 10
    top_df = df_day.head(num).reset_index(drop=True)
    
    for r in range(0, len(top_df), 5):
        cols = st.columns(5)
        for i, col in enumerate(cols):
            idx = r + i
            if idx < len(top_df):
                game = top_df.iloc[idx]
                curr_id = game.get("AppID", 0)
                with col:
                    st.image(get_game_image(curr_id), use_container_width=True)
                    st.markdown(f"**#{int(game.get('Posicion', 0))} {fix_nan(game.get('Nombre'))}**")
                    if st.button("+ info", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.selected_game = int(curr_id)
                        st.rerun()
                    st.caption(f"👥 {int(game.get('JugadoresConcurrentes', 0)):,} jug.")
    
    st.write("---")
    if not st.session_state.show_more:
        if st.button("🔽 Mostrar más juegos (Top 50)", use_container_width=True):
            st.session_state.show_more = True
            st.rerun()
    else:
        if st.button("🔼 Mostrar menos", use_container_width=True):
            st.session_state.show_more = False
            st.rerun()

with t2:
    st.line_chart(df_day.head(5).set_index("Nombre")["JugadoresConcurrentes"])

with t3:
    st.dataframe(df_day[["Posicion", "Nombre", "JugadoresConcurrentes"]], use_container_width=True, hide_index=True)

with t4:
    if not df_detalles.empty:
        st.dataframe(df_detalles[['Nombre', 'Precio', 'Rating']], use_container_width=True, hide_index=True)

st.divider()
st.caption("© 2026 infosteam — Dashboard de Seguimiento")