import streamlit as st
import pandas as pd
import os
import subprocess
import re

# ---------- CONFIGURACIÓN DE PÁGINA ----------
st.set_page_config(
    page_title="infosteam - Pro Dashboard",
    page_icon="🎮",
    layout="wide",
)

# --- Estilos CSS mejorados ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #66c0f4; }
    .stButton>button { border-radius: 5px; }
    .css-154489f { background-color: #161921; } 
    </style>
    """, unsafe_allow_html=True)

# ---------- FUNCIONES DE APOYO ----------

def convert_to_usd(price_str):
    if pd.isna(price_str) or price_str == "" or price_str == "N/A":
        return "N/A"
    p = str(price_str).replace('"', '').replace("'", "").upper()
    if any(word in p for word in ["GRATIS", "FREE", "0"]):
        return "Free to Play"
    try:
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", p.replace(',', '.'))
        if not nums: return p
        val = float(nums[0])
        rates = {"€": 1.08, "฿": 0.028, "РУБ": 0.011, "AED": 0.27, "CLP": 0.0011, "CDN$": 0.74, "¥": 0.0067}
        for symbol, rate in rates.items():
            if symbol in p: return f"${round(val * rate, 2)}"
        return f"${val}"
    except:
        return p

def get_game_image(appid):
    return f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"

def get_game_background(appid):
    return f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/page_bg_generated_v6b.jpg"

# ---------- CARGA DE DATOS ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "Clean")
LISTADO_CSV = os.path.join(CLEAN_DIR, "listado_juegos.csv")
INFO_CSV = os.path.join(CLEAN_DIR, "info_juegos.csv")
DETALLES_CSV = os.path.join(CLEAN_DIR, "detalles_juegos.csv")

@st.cache_data(ttl=300)
def load_data():
    df_l = pd.read_csv(LISTADO_CSV) if os.path.exists(LISTADO_CSV) else pd.DataFrame()
    df_i = pd.read_csv(INFO_CSV) if os.path.exists(INFO_CSV) else pd.DataFrame()
    df_d = pd.read_csv(DETALLES_CSV, on_bad_lines="skip") if os.path.exists(DETALLES_CSV) else pd.DataFrame()
    if not df_d.empty:
        df_d['AppID'] = pd.to_numeric(df_d['AppID'], errors='coerce')
        df_d['Precio_USD_Val'] = df_d['Precio'].apply(convert_to_usd)
    return df_l, df_i, df_d

df_listado, df_info, df_detalles = load_data()

# ---------- GESTIÓN DE NAVEGACIÓN ----------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_game" not in st.session_state:
    st.session_state.selected_game = None

# --- MENÚ LATERAL ---
with st.sidebar:
    st.title("📑 Menú Principal")
    
    with st.expander("ℹ️ About", expanded=False):
        st.write("📝 **Blog**")
        st.write("💬 **Discord**")
    
    with st.expander("👤 Account", expanded=False):
        st.button("Sign in via Steam", use_container_width=True)
    
    with st.expander("🏆 Rankings", expanded=True):
        if not df_listado.empty:
            dates = sorted(df_listado["Fecha"].unique(), reverse=True)
            selected_date = st.selectbox("Fecha de Snapshot", dates)
        else:
            selected_date = None
        
        if st.button("📊 Ver Rankings"):
            st.session_state.page = "home"
            st.session_state.selected_game = None
            st.rerun()

    # --- NUEVA SECCIÓN DE SALES ---
    with st.expander("💸 Sales & Offers", expanded=True):
        st.write("Busca las mejores ofertas.")
        if st.button("🔥 Ir a Sales"):
            st.session_state.page = "sales"
            st.session_state.selected_game = None
            st.rerun()

    st.divider()
    if st.button("🏠 Inicio", use_container_width=True):
        st.session_state.page = "home"
        st.session_state.selected_game = None
        st.rerun()

    st.divider()
    st.caption(f"Available dates: {len(dates)}")
    st.caption(f"Range: {dates[-1]} → {dates[0]}")

# 1. PANTALLA: SALES (NUEVA)
if st.session_state.page == "sales":
    st.title("💸 Steam Sales & Special Offers")
    st.caption("Filtra y encuentra juegos con descuento o mejores valoraciones.")
    
    if df_detalles.empty:
        st.warning("No hay datos de detalles disponibles.")
    else:
        # Unimos detalles con info para tener lanzamiento y géneros
        df_sales = pd.merge(df_detalles, df_info[['AppID', 'Lanzamiento', 'Géneros']], on='AppID', how='left')
        
        # Filtros en la parte superior
        col_f1, col_f2, col_f3 = st.columns(3)
        search = col_f1.text_input("Buscar por nombre", "")
        min_rating = col_f2.slider("Rating mínimo", 0, 100, 0)
        
        # Procesamos datos para la tabla
        df_display = df_sales.copy()
        
        # Filtro de búsqueda
        if search:
            df_display = df_display[df_display['Nombre'].str.contains(search, case=False, na=False)]
        
        # Filtro de rating
        df_display['Rating_Num'] = pd.to_numeric(df_display['Rating'], errors='coerce').fillna(0)
        df_display = df_display[df_display['Rating_Num'] >= min_rating]

        # Seleccionamos y renombramos columnas para la tabla solicitada
        df_final_table = df_display[[
            'Nombre', 'Precio', 'Precio_USD_Val', 'Rating', 'Lanzamiento'
        ]].rename(columns={
            'Precio': 'Precio Original',
            'Precio_USD_Val': 'Precio USD (Est.)',
            'Rating': 'Valoración (%)'
        })

        st.dataframe(df_final_table, use_container_width=True, hide_index=True)
    st.stop()

# 2. PANTALLA: DETALLE DEL JUEGO
if st.session_state.selected_game:
    appid = st.session_state.selected_game
    g_list = df_listado[df_listado["AppID"] == appid].iloc[0] if appid in df_listado["AppID"].values else None
    g_info = df_info[df_info["AppID"] == appid].iloc[0] if appid in df_info["AppID"].values else None
    g_det = df_detalles[df_detalles["AppID"] == appid].iloc[0] if appid in df_detalles["AppID"].values else None
    
    st.title(f"🎮 {g_list['Nombre'] if g_list is not None else 'Detalles'}")
    
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.image(get_game_background(appid), use_container_width=True)
        st.subheader("📋 Información Detallada")
        if g_info is not None:
            st.write(f"**🏢 Desarrollador:** {g_info.get('Desarrollador', 'N/A')}")
            st.write(f"**🏷️ Géneros:** {g_info.get('Géneros', 'N/A')}")
            st.write(f"**📅 Lanzamiento:** {g_info.get('Lanzamiento', 'N/A')}")

    with col2:
        st.image(get_game_image(appid), use_container_width=True)
        if g_det is not None:
            st.metric("Precio", g_det['Precio_USD_Val'])
            st.metric("Rating", f"{g_det.get('Rating', 'N/A')}/100")
            st.metric("Reseñas", g_det.get('Reviews', 'N/A'))
        st.link_button("🚀 Ver en Steam", f"https://store.steampowered.com/app/{appid}", use_container_width=True)
    st.stop()

# 3. PANTALLA: HOME / RANKINGS
if st.session_state.page == "home":
    df_day = df_listado[df_listado["Fecha"] == selected_date].copy()
    st.title("🎮 infosteam")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Jugadores Online", f"{df_day['JugadoresConcurrentes'].sum():,}")
    m2.metric("Juegos Trackeados", len(df_day))
    m3.metric("Líder", df_day.iloc[0]["Nombre"])

    tab1, tab2, tab3 = st.tabs(["📊 Rankings", "📈 Tendencia", "📋 Datos"])

    with tab1:
        top10 = df_day.head(10).reset_index(drop=True)
        for row_start in range(0, len(top10), 5):
            cols = st.columns(5)
            for i, col in enumerate(cols):
                idx = row_start + i
                if idx < len(top10):
                    game = top10.iloc[idx]
                    with col:
                        st.image(get_game_image(game["AppID"]), use_container_width=True)
                        st.markdown(f"**#{int(game['Posicion'])} {game['Nombre']}**")
                        if st.button("+ info", key=f"btn_{game['AppID']}", use_container_width=True):
                            st.session_state.selected_game = game["AppID"]
                            st.rerun()
                        st.caption(f"👥 {int(game['JugadoresConcurrentes']):,} jug.")
    
    with tab2:
        st.subheader("📈 Evolución de Jugadores")
        # Gráfico dinámico basado en tendencia
        date_idx = dates.index(selected_date)
        trend_dates = dates[max(0, date_idx):min(len(dates), date_idx + 7)]
        if len(trend_dates) > 1:
            df_trend = df_listado[df_listado["Fecha"].isin(trend_dates)].copy()
            selected_games = st.multiselect("Comparar:", sorted(df_trend["Nombre"].unique().tolist()), default=df_day.head(3)["Nombre"].tolist())
            if selected_games:
                chart_data = df_trend[df_trend["Nombre"].isin(selected_games)].pivot_table(index="Fecha", columns="Nombre", values="JugadoresConcurrentes", aggfunc="first")
                st.line_chart(chart_data)

    with tab3:
        st.dataframe(df_day[["Posicion", "Nombre", "JugadoresConcurrentes", "AppID"]], use_container_width=True, hide_index=True)

st.divider()
st.caption("© 2026 infosteam — Dashboard de Seguimiento de Steam")