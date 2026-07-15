"""
infosteam - Professional Steam Games Dashboard
Main application file (cleaned and modular)
"""
import streamlit as st
import sys
import subprocess
import os
import pandas as pd

# Importar configuración y utilidades
from utils.config import (
    BASE_DIR, DOWNLOAD_SCRIPT, USERS_FILE, FAV_FILE,
    CACHE_TTL_SHORT
)
from utils.translations import LANGUAGE_NAMES, LANGUAGE_CODES, LANGUAGE_CODE_TO_NAME, get_translations
from utils.data_utils import init_user_files, load_data, fix_nan
from styles.theme import PAGE_CONFIG_STYLE
from components.forms import render_login_form, handle_login, handle_register
from pages.dashboard import display_dashboard_page
from pages.game_detail import display_game_detail_page
from pages.favorites import display_favorites_page
from pages.chat import display_chat_page


# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="infosteam | Professional Dashboard",
    page_icon="https://img.icons8.com/ios-filled/50/ffffff/steam.png",
    layout="wide"
)

st.markdown(PAGE_CONFIG_STYLE, unsafe_allow_html=True)

# ============================================
# INITIALIZE DATA
# ============================================
init_user_files()

@st.cache_data(ttl=CACHE_TTL_SHORT)
def load_all_data():
    """Carga todos los datos de los CSVs"""
    return load_data()

df_listado, df_info, df_detalles, df_plataformas = load_all_data()

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if "selected_game" not in st.session_state:
    st.session_state.selected_game = None
if "show_more" not in st.session_state:
    st.session_state.show_more = False
if "view" not in st.session_state:
    st.session_state.view = "Dashboard"
if "language_name" not in st.session_state:
    st.session_state.language_name = "Español"
elif st.session_state.language_name not in LANGUAGE_NAMES:
    st.session_state.language_name = LANGUAGE_CODE_TO_NAME.get(st.session_state.language_name, "Español")
if "language" not in st.session_state:
    st.session_state.language = LANGUAGE_CODES.get(st.session_state.language_name, "es")
if "sel_date" not in st.session_state:
    if not df_listado.empty:
        dates = sorted(df_listado["Fecha"].unique(), reverse=True)
        st.session_state.sel_date = dates[0]
    else:
        st.session_state.sel_date = None
if "pd" not in st.session_state:
    st.session_state.pd = pd

# ============================================
# SIDEBAR - NAVIGATION & AUTHENTICATION
# ============================================
with st.sidebar:
    current_t = get_translations(st.session_state.language)
    
    # Language selector
    language_index = LANGUAGE_NAMES.index(st.session_state.language_name) if st.session_state.language_name in LANGUAGE_NAMES else 0
    st.selectbox(current_t["language_label"], LANGUAGE_NAMES, index=language_index, key="language_name")
    if st.session_state.language_name not in LANGUAGE_CODES:
        st.session_state.language_name = LANGUAGE_CODE_TO_NAME.get(st.session_state.language_name, "Español")
    st.session_state.language = LANGUAGE_CODES.get(st.session_state.language_name, "es")
    t = get_translations(st.session_state.language)

    # Authentication
    st.markdown(f"### {t['account']}")
    auth_mode = st.radio(t["mode"], [t["login"], t["register"]], label_visibility="collapsed")
    u_name, u_pass = render_login_form(t)

    if auth_mode == t["register"]:
        handle_register(u_name, u_pass, t)
    else:
        handle_login(u_name, u_pass, t)

    # User session
    if "user" in st.session_state:
        st.success(f"Usuario: {st.session_state['user']}")
        if st.button(t["logout"], use_container_width=True):
            del st.session_state["user"]
            st.rerun()
        if st.button(t["my_favorites"], use_container_width=True):
            st.session_state.view = "Favorites"
            st.rerun()

    st.divider()
    
    # Navigation
    st.markdown(f"### {t['navigation']}")

    if st.button(t["home_dashboard"], use_container_width=True):
        st.session_state.selected_game = None
        st.session_state.view = "Dashboard"
        st.rerun()

    if st.button("Chat", use_container_width=True):
        st.session_state.selected_game = None
        st.session_state.view = "Chat"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # View menu
    view_menu_keys = ["Dashboard", "Market Trends", "Popular Releases", "Future Trending", "Top Genres", "Top Developers", "Price Analysis", "Favorites"]
    view_menu_labels = [
        t["dashboard"], t["market_trends"], t["popular_releases"], t["future_trending"],
        t["top_genres"], t["top_developers"], t["price_analysis"], t["favorites"]
    ]

    current_index = view_menu_keys.index(st.session_state.view) if st.session_state.view in view_menu_keys else 0
    selected_label = st.selectbox("Seleccionar vista", view_menu_labels, index=current_index, label_visibility="collapsed")
    st.session_state.view = view_menu_keys[view_menu_labels.index(selected_label)]

    # Date selector
    if not df_listado.empty:
        dates = sorted(df_listado["Fecha"].unique(), reverse=True)
        st.session_state.sel_date = st.selectbox(t["select_date"], dates, index=dates.index(st.session_state.sel_date) if st.session_state.sel_date in dates else 0)

    # Update data
    if st.button(t["update_data"], use_container_width=True):
        with st.spinner("Actualizando datos..."):
            try:
                result = subprocess.run(
                    [sys.executable, DOWNLOAD_SCRIPT],
                    cwd=BASE_DIR,
                    capture_output=True,
                    text=True,
                    timeout=180
                )
                if result.returncode == 0:
                    load_all_data.clear()
                    st.success("Datos actualizados correctamente.")
                    st.rerun()
                else:
                    st.error(f"Error: {result.stderr or result.stdout}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ============================================
# MAIN CONTENT - ROUTING
# ============================================
t = get_translations(st.session_state.language)

# Game detail view
if st.session_state.selected_game:
    appid = st.session_state.selected_game
    display_game_detail_page(appid, t, df_listado, df_info, df_detalles, df_plataformas)
    st.stop()

# Favorites view
if st.session_state.view == "Favorites":
    display_favorites_page(t, df_listado, df_info, df_detalles, df_plataformas)
    st.stop()

# Chat view
if st.session_state.view == "Chat":
    display_chat_page(t, df_listado, df_info, df_detalles, df_plataformas)
    st.stop()

# Main dashboard
display_dashboard_page(t, df_listado, df_info, df_detalles, df_plataformas)

st.divider()
st.caption(t["copyright"])
