import streamlit as st
import pandas as pd
import os
import subprocess
import re

# ---------- CONFIGURACIÓN DE PÁGINA ----------
st.set_page_config(
    page_title="infosteam - Game Explorer",
    page_icon="🎮",
    layout="wide",
)

# ---------- FUNCIONES DE APOYO ----------

def convert_to_usd(price_str):
    """Limpia el precio del CSV y lo convierte a dólares basándose en símbolos."""
    if pd.isna(price_str) or price_str == "" or price_str == "N/A":
        return "N/A"
    
    p = str(price_str).replace('"', '').replace("'", "").upper()
    
    if any(word in p for word in ["GRATIS", "FREE", "0"]):
        return "Free to Play"

    try:
        # Extraer el valor numérico
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", p.replace(',', '.'))
        if not nums: return p
        val = float(nums[0])

        # Conversiones basadas en símbolos (Tasas aproximadas 2026)
        if "€" in p: return f"${round(val * 1.08, 2)}"
        if "฿" in p: return f"${round(val * 0.028, 2)}"
        if "РУБ" in p: return f"${round(val * 0.011, 2)}"
        if "AED" in p: return f"${round(val * 0.27, 2)}"
        if "CLP" in p: return f"${round(val * 0.0011, 2)}"
        if "CDN$" in p: return f"${round(val * 0.74, 2)}"
        if "¥" in p: return f"${round(val * 0.0067, 2)}"
        
        return f"${val}"
    except:
        return p

def get_game_image(appid):
    """Imagen de cabecera principal."""
    return f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"

def get_game_background(appid):
    """Imagen de fondo generada por Steam."""
    return f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/page_bg_generated_v6b.jpg"

# ---------- RUTAS ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "Clean")
LISTADO_CSV = os.path.join(CLEAN_DIR, "listado_juegos.csv")
INFO_CSV = os.path.join(CLEAN_DIR, "info_juegos.csv")
DETALLES_CSV = os.path.join(CLEAN_DIR, "detalles_juegos.csv")
DOWNLOAD_SCRIPT = os.path.join(BASE_DIR, "Src", "download.py")

# ---------- CARGA DE DATOS ----------
@st.cache_data(ttl=300)
def load_data():
    df_l = pd.read_csv(LISTADO_CSV) if os.path.exists(LISTADO_CSV) else pd.DataFrame()
    df_i = pd.read_csv(INFO_CSV) if os.path.exists(INFO_CSV) else pd.DataFrame()
    df_d = pd.read_csv(DETALLES_CSV, on_bad_lines="skip") if os.path.exists(DETALLES_CSV) else pd.DataFrame()
    
    if not df_d.empty:
        df_d['AppID'] = pd.to_numeric(df_d['AppID'], errors='coerce')
        df_d['Precio_USD'] = df_d['Precio'].apply(convert_to_usd)
    
    return df_l, df_i, df_d

df_listado, df_info, df_detalles = load_data()

# ---------- GESTIÓN DE NAVEGACIÓN ----------
if "selected_game" not in st.session_state:
    st.session_state.selected_game = None

def select_game(appid):
    st.session_state.selected_game = appid

def go_back():
    st.session_state.selected_game = None

# ---------- PANTALLA A: DETALLE COMPLETO ----------
if st.session_state.selected_game:
    appid = st.session_state.selected_game
    
    # Buscar info en los 3 DataFrames
    g_list = df_listado[df_listado["AppID"] == appid].iloc[0] if appid in df_listado["AppID"].values else None
    g_info = df_info[df_info["AppID"] == appid].iloc[0] if appid in df_info["AppID"].values else None
    g_det = df_detalles[df_detalles["AppID"] == appid].iloc[0] if appid in df_detalles["AppID"].values else None
    
    name = g_list["Nombre"] if g_list is not None else "Juego Desconocido"

    if st.button("⬅️ Volver al Ranking"):
        go_back()
        st.rerun()

    st.title(f"🎮 {name}")
    st.write(f"**AppID:** {appid}")
    st.divider()

    col_img, col_info = st.columns([1, 1.5])
    
    with col_img:
        st.image(get_game_image(appid), use_container_width=True)
        st.link_button("🚀 Abrir en Steam Store", f"https://store.steampowered.com/app/{appid}", use_container_width=True)
        
    with col_info:
        st.subheader("📊 Ficha Técnica")
        c1, c2, c3 = st.columns(3)
        if g_det is not None:
            c1.metric("Precio (USD)", g_det['Precio_USD'])
            c2.metric("Rating", f"{g_det.get('Rating', 'N/A')}/100")
            c3.metric("Reseñas", f"{g_det.get('Reviews', 'N/A')}")
        
        st.write("---")
        if g_info is not None:
            st.write(f"**🏢 Desarrollador:** {g_info.get('Desarrollador', 'N/A')}")
            st.write(f"**🏷️ Géneros:** {g_info.get('Géneros', 'N/A')}")
            st.write(f"**💻 Plataformas:** {g_info.get('Plataformas', 'Windows')}")
        
        if g_list is not None:
            st.success(f"🔥 **{int(g_list['JugadoresConcurrentes']):,}** personas jugando ahora mismo.")

    st.divider()
    st.subheader("🖼️ Arte de Fondo")
    st.image(get_game_background(appid), use_container_width=True)
    st.stop() # Bloqueamos el resto para que no se vea el ranking debajo

# ---------- PANTALLA B: RANKING PRINCIPAL ----------
if df_listado.empty:
    st.warning("No data found. Run the download script first.")
    st.stop()

dates = sorted(df_listado["Fecha"].unique(), reverse=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    selected_date = st.selectbox("📅 Select date:", dates)
    st.divider()
    if st.button("🔄 Update from Steam"):
        subprocess.run(["python3", DOWNLOAD_SCRIPT], cwd=BASE_DIR)
        st.cache_data.clear()
        st.rerun()

# Filtrado por fecha
df_day = df_listado[df_listado["Fecha"] == selected_date].copy()

st.title("🎮 infosteam")
st.caption(f"Most Played Games on Steam — {selected_date}")

# Resumen rápido
c1, c2, c3 = st.columns(3)
c1.metric("🟢 Players Online", f"{df_day['JugadoresConcurrentes'].sum():,}")
c2.metric("🎮 Games Tracked", len(df_day))
c3.metric("🏆 Most Played", df_day.iloc[0]["Nombre"])
st.divider()

tab1, tab2, tab3 = st.tabs(["📊 Rankings", "📈 7-Day Trend", "📋 Data Table"])

with tab1:
    top10 = df_day.head(10).reset_index(drop=True)

    for row_start in range(0, len(top10), 5):
        cols = st.columns(5)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx >= len(top10): break
            game = top10.iloc[idx]
            appid = int(game["AppID"])
            with col:
                st.image(get_game_image(appid), use_container_width=True)
                st.markdown(f"**#{int(game['Posicion'])} {game['Nombre']}**")
                
                # Precio rápido
                if not df_detalles.empty:
                    row_p = df_detalles[df_detalles["AppID"] == appid]
                    if not row_p.empty:
                        st.markdown(f"💰 **{row_p.iloc[0]['Precio_USD']}**")

                # BOTÓN PARA IR A LA OTRA PANTALLA
                if st.button("Ver toda la info", key=f"btn_{appid}", use_container_width=True):
                    select_game(appid)
                    st.rerun()
                
                st.metric("Players", f"{int(game['JugadoresConcurrentes']):,}")

# Tab 2: Tendencias
with tab2:
    st.subheader("📈 Player Trends")
    date_idx = dates.index(selected_date)
    trend_dates = dates[max(0, date_idx):min(len(dates), date_idx + 7)]
    if len(trend_dates) > 1:
        df_trend = df_listado[df_listado["Fecha"].isin(trend_dates)].copy()
        top_names = df_day.head(10)["Nombre"].tolist()
        selected_games = st.multiselect("Compare:", sorted(df_trend["Nombre"].unique()), default=top_names[:5])
        if selected_games:
            filtered = df_trend[df_trend["Nombre"].isin(selected_games)]
            chart_data = filtered.pivot_table(index="Fecha", columns="Nombre", values="JugadoresConcurrentes")
            st.line_chart(chart_data)

# Tab 3: Tabla
with tab3:
    st.dataframe(df_day[["Posicion", "Nombre", "JugadoresConcurrentes", "AppID"]], use_container_width=True, hide_index=True)

st.divider()
st.caption("© 2026 infosteam — Data from Steam Web API")