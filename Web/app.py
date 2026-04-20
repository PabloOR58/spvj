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

# Imagen de reserva si Steam falla (puedes cambiarla por cualquier URL de imagen)
IMG_ERROR = "https://i.imgur.com/8N9V6vT.png"

# Iconos de plataforma
LOGOS = {
    "windows": "https://img.icons8.com/color/48/000000/windows-10.png",
    "mac": "https://img.icons8.com/ios-filled/50/ffffff/mac-os.png",
    "linux": "https://img.icons8.com/color/48/000000/tux.png"
}

# ---------- FUNCIONES DE APOYO ----------

def fix_nan(val, default="-"):
    """Evita mostrar la palabra 'nan' en la interfaz."""
    if pd.isna(val) or str(val).lower() == "nan" or str(val).strip() == "":
        return default
    return str(val)

def convert_to_usd(price_str):
    """Limpia y convierte precios a USD."""
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
    """Genera la URL de la carátula de Steam."""
    try:
        clean_id = str(int(float(appid)))
    except:
        clean_id = "0"
    return f"https://cdn.akamai.steamstatic.com/steam/apps/{clean_id}/header.jpg"

def get_game_background(appid):
    """Genera la URL del fondo de Steam."""
    try:
        clean_id = str(int(float(appid)))
    except:
        return IMG_ERROR
    return f"https://cdn.akamai.steamstatic.com/steam/apps/{clean_id}/page_bg_generated_v6b.jpg"

# ---------- CARGA DE DATOS ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "Clean")

@st.cache_data(ttl=300)
def load_data():
    try:
        df_l = pd.read_csv(os.path.join(CLEAN_DIR, "listado_juegos.csv"))
        df_i = pd.read_csv(os.path.join(CLEAN_DIR, "info_juegos.csv"))
        df_d = pd.read_csv(os.path.join(CLEAN_DIR, "detalles_juegos.csv"), on_bad_lines="skip")
        
        # Normalizar AppIDs a enteros para evitar errores de vinculación
        for df in [df_l, df_i, df_d]:
            if not df.empty and 'AppID' in df.columns:
                df['AppID'] = pd.to_numeric(df['AppID'], errors='coerce').fillna(0).astype(int)
        return df_l, df_i, df_d
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_listado, df_info, df_detalles = load_data()

# ---------- GESTIÓN DE NAVEGACIÓN ----------
if "selected_game" not in st.session_state: st.session_state.selected_game = None
if "show_more" not in st.session_state: st.session_state.show_more = False

with st.sidebar:
    st.title("📑 Menú Principal")
    with st.expander("ℹ️ About", expanded=True): st.write("• Blog\n• Discord\n• Social Media")
    with st.expander("🏆 Rankings", expanded=True):
        if not df_listado.empty:
            dates = sorted(df_listado["Fecha"].unique(), reverse=True)
            sel_date = st.selectbox("Seleccionar Fecha:", dates)
    if st.button("🏠 Volver al Inicio"): 
        st.session_state.selected_game = None
        st.session_state.show_more = False
        st.rerun()

# ---------- VISTA A: DETALLE DEL JUEGO ----------
if st.session_state.selected_game:
    appid = st.session_state.selected_game
    
    # Búsqueda segura de filas
    g_l = df_listado[df_listado["AppID"] == appid].iloc[0] if not df_listado[df_listado["AppID"] == appid].empty else None
    g_i = df_info[df_info["AppID"] == appid].iloc[0] if not df_info[df_info["AppID"] == appid].empty else pd.Series()
    g_d = df_detalles[df_detalles["AppID"] == appid].iloc[0] if not df_detalles[df_detalles["AppID"] == appid].empty else pd.Series()

    st.title(f"🎮 {fix_nan(g_l['Nombre'] if g_l is not None else 'Detalle')}")
    col_a, col_b = st.columns([1.5, 1])
    
    with col_a:
        # Imagen de fondo con Fallback
        st.markdown(f'<img src="{get_game_background(appid)}" onerror="this.src=\'{IMG_ERROR}\';" style="width:100%; border-radius:10px;">', unsafe_allow_html=True)
        st.subheader("📋 Información Técnica")
        st.write(f"**Desarrollador:** {fix_nan(g_i.get('Desarrollador'))}")
        st.write(f"**Géneros:** {fix_nan(g_i.get('Géneros'))}")
        
        st.write("**Plataformas:**")
        p_str = fix_nan(g_i.get('Plataformas'), "").lower()
        l_cols = st.columns(10)
        if "win" in p_str: l_cols[0].image(LOGOS["windows"], width=35)
        if "mac" in p_str or "apple" in p_str: l_cols[1].image(LOGOS["mac"], width=30)
        if "linux" in p_str: l_cols[2].image(LOGOS["linux"], width=35)

    with col_b:
        # Carátula con Fallback
        st.markdown(f'<img src="{get_game_image(appid)}" onerror="this.src=\'{IMG_ERROR}\';" style="width:100%; border-radius:10px;">', unsafe_allow_html=True)
        st.subheader("📊 Métricas")
        
        st.metric("Precio Est.", convert_to_usd(g_d.get('Precio', 'N/A')))
        st.metric("Rating", f"⭐ {fix_nan(g_d.get('Rating'))}/100")
        st.metric("Reseñas", f"💬 {fix_nan(g_d.get('Reviews'))}")
        
        st.link_button("🚀 Abrir en Steam Store", f"https://store.steampowered.com/app/{appid}", use_container_width=True)
    st.stop()

# ---------- VISTA B: DASHBOARD PRINCIPAL ----------
st.title("🎮 infosteam")
if df_listado.empty: st.stop()

df_day = df_listado[df_listado["Fecha"] == sel_date].copy()

# Métricas Top
m1, m2, m3 = st.columns(3)
m1.metric("🟢 Players Online", f"{int(df_day['JugadoresConcurrentes'].sum()):,}")
m2.metric("🎮 Games Tracked", f"{len(df_day)}")
m3.metric("🏆 King of the Day", fix_nan(df_day.iloc[0]["Nombre"]))
st.divider()

t1, t2, t3, t4 = st.tabs(["📊 Rankings", "📈 7-Day Trend", "📋 Data Table", "💸 Sales"])

with t1:
    # Lógica de Mostrar Más
    limit = 50 if st.session_state.show_more else 10
    top_df = df_day.head(limit).reset_index(drop=True)
    
    for r in range(0, len(top_df), 5):
        cols = st.columns(5)
        for i, col in enumerate(cols):
            idx = r + i
            if idx < len(top_df):
                game = top_df.iloc[idx]
                curr_id = game.get("AppID", 0)
                with col:
                    # Imagen con sistema Fallback HTML para evitar cuadros rotos
                    st.markdown(
                        f"""
                        <div style="height: 140px; overflow: hidden; border-radius: 5px; background: #161921;">
                            <img src="{get_game_image(curr_id)}" 
                                 onerror="this.onerror=null;this.src='{IMG_ERROR}';" 
                                 style="width: 100%; height: 100%; object-fit: cover;">
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    st.markdown(f"**#{int(game.get('Posicion', 0))} {fix_nan(game.get('Nombre'))}**")
                    if st.button("+ info", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.selected_game = int(curr_id)
                        st.rerun()
                    st.caption(f"👥 {int(game.get('JugadoresConcurrentes', 0)):,} jug.")
    
    st.write("---")
    if not st.session_state.show_more:
        if st.button("🔽 Mostrar Ranking Completo (Top 50)", use_container_width=True):
            st.session_state.show_more = True
            st.rerun()
    else:
        if st.button("🔼 Ver solo Top 10", use_container_width=True):
            st.session_state.show_more = False
            st.rerun()

with t2:
    st.header("📈 Análisis de Tendencias")
    # Lógica de 7 días
    all_dates = sorted(df_listado["Fecha"].unique(), reverse=True)
    date_idx = all_dates.index(sel_date)
    trend_dates = all_dates[max(0, date_idx):min(len(all_dates), date_idx + 7)]
    df_trend = df_listado[df_listado["Fecha"].isin(trend_dates)].copy()
    
    selected_g = st.multiselect("Comparar juegos:", sorted(df_trend["Nombre"].unique()), default=df_day.head(5)["Nombre"].tolist())
    if selected_g:
        c_data = df_trend[df_trend["Nombre"].isin(selected_g)].pivot_table(index="Fecha", columns="Nombre", values="JugadoresConcurrentes")
        st.line_chart(c_data)
        
        st.divider()
        c_area, c_bar = st.columns(2)
        with c_area:
            st.subheader("🎭 Cuota de Mercado (Top 5)")
            st.area_chart(df_trend[df_trend["Nombre"].isin(df_day.head(5)["Nombre"])].pivot_table(index="Fecha", columns="Nombre", values="JugadoresConcurrentes"))
        with c_bar:
            st.subheader("🔥 Volatilidad Semanal")
            st.bar_chart(df_trend[df_trend["Nombre"].isin(selected_g[:5])].groupby("Nombre")["JugadoresConcurrentes"].agg(["max", "min"]))

with t3:
    st.dataframe(df_day[["Posicion", "Nombre", "JugadoresConcurrentes", "AppID"]], use_container_width=True, hide_index=True)

with t4:
    st.subheader("💸 Tabla de Ofertas Actuales")
    if not df_detalles.empty:
        st.dataframe(df_detalles[['Nombre', 'Precio', 'Rating']], use_container_width=True, hide_index=True)

st.divider()
st.caption("© 2026 infosteam — Sistema de Monitorización de Datos de Steam")