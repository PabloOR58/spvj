"""
Componentes de formularios y controles
"""
import streamlit as st
import pandas as pd
from utils.data_utils import encrypt_password, fix_nan
from utils.config import USERS_FILE, FAV_FILE


def render_login_form(t):
    """Renderiza formulario de login"""
    u_name = st.text_input(t["user"])
    u_pass = st.text_input(t["password"], type="password")
    
    return u_name, u_pass


def handle_login(u_name, u_pass, t):
    """Maneja el login del usuario"""
    if st.button(t["login"], key="login_btn", use_container_width=True):
        users = pd.read_csv(USERS_FILE)
        valid_user = None
        for _, user_row in users.iterrows():
            if user_row["username"] == u_name:
                stored_pass = user_row["password"]
                encrypted_input = encrypt_password(u_pass)
                if stored_pass == encrypted_input:
                    valid_user = user_row
                    break
                elif stored_pass == u_pass:
                    valid_user = user_row
                    users.loc[users["username"] == u_name, "password"] = encrypted_input
                    users.to_csv(USERS_FILE, index=False)
                    break

        if valid_user is not None:
            st.session_state["user"] = u_name
            st.rerun()
        else:
            st.error(t["wrong_credentials"])


def handle_register(u_name, u_pass, t):
    """Maneja el registro de un nuevo usuario"""
    if st.button(t["create_account"], key="register_btn", use_container_width=True):
        users = pd.read_csv(USERS_FILE)
        if u_name in users["username"].values:
            st.error(t["user_exists"])
        else:
            encrypted_pass = encrypt_password(u_pass)
            new_u = pd.DataFrame([[u_name, encrypted_pass]], columns=["username", "password"])
            pd.concat([users, new_u]).to_csv(USERS_FILE, index=False)
            st.success(t["user_registered"])


def render_filters(t, df_explorer, genre_options, dev_options, platform_options):
    """Renderiza filtros de búsqueda"""
    f1, f2 = st.columns(2)
    
    with f1:
        selected_names = st.multiselect(t["name_filter"], sorted(df_explorer['Nombre'].dropna().astype(str).unique()), key="filter_names")
        selected_genres = st.multiselect(t["genre_filter"], genre_options, key="filter_genres")
        selected_developers = st.multiselect(t["developer_filter"], dev_options, key="filter_devs")
    
    with f2:
        selected_platforms = st.multiselect(t["platform_filter"], platform_options, key="filter_platforms")
        pmin = int(df_explorer['Precio'].min()) if not df_explorer['Precio'].dropna().empty else 0
        pmax = int(df_explorer['Precio'].max()) if not df_explorer['Precio'].dropna().empty else 0
        selected_price = st.slider(t["price_range"], pmin, pmax, (pmin, pmax), key="filter_price") if pmin < pmax else (pmin, pmax)
        jmin = int(df_explorer['JugadoresConcurrentes'].min()) if not df_explorer['JugadoresConcurrentes'].empty else 0
        jmax = int(df_explorer['JugadoresConcurrentes'].max()) if not df_explorer['JugadoresConcurrentes'].empty else 0
        selected_players = st.slider(t["players_range"], jmin, jmax, (jmin, jmax), key="filter_players") if jmin < jmax else (jmin, jmax)
    
    return selected_names, selected_genres, selected_developers, selected_platforms, selected_price, selected_players
