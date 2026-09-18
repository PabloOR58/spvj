"""
Página de favoritos
"""
import streamlit as st
import pandas as pd
from utils.config import FAV_FILE
from utils.data_utils import fix_nan
from components.cards import render_game_card


def display_favorites_page(t, df_listado, df_info, df_detalles, df_plataformas):
    """Renderiza la página de favoritos"""
    st.title(f"{t['my_favorites']}")
    
    if "user" not in st.session_state:
        st.warning(t["please_login_favorites"])
        return
    
    try:
        favs_df = pd.read_csv(FAV_FILE)
    except:
        favs_df = pd.DataFrame(columns=["username", "appid"])
    
    user_favs = favs_df[favs_df["username"] == st.session_state["user"]]
    
    if user_favs.empty:
        st.info(t["favorites_empty"])
        return
    
    favs_list = user_favs.reset_index(drop=True)
    cols_per_row = 4
    
    for r in range(0, len(favs_list), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            idx = r + i
            if idx < len(favs_list):
                row = favs_list.iloc[idx]
                get_aid = int(row["appid"])
                
                g_name = None
                g_row = df_listado[df_listado['AppID'] == get_aid]
                if not g_row.empty:
                    g_name = g_row['Nombre'].iloc[0]
                else:
                    info_row = df_info[df_info['AppID'] == get_aid]
                    if not info_row.empty:
                        g_name = info_row['Nombre'].iloc[0]
                
                if not g_name:
                    g_name = f"AppID: {get_aid}"

                with col:
                    det_row = df_detalles[df_detalles['AppID'] == get_aid]
                    price_raw = det_row['Precio'].iloc[0] if not det_row.empty else None
                    info_row = df_info[df_info['AppID'] == get_aid]
                    genres_raw = info_row['Géneros'].iloc[0] if not info_row.empty else None
                    rel_dt = info_row['Fecha_Lanzamiento'].iloc[0] if not info_row.empty else None
                    
                    render_game_card(
                        get_aid, fix_nan(g_name), t, f"fav_{idx}",
                        df_listado, df_info, df_detalles, df_plataformas,
                        price_raw=price_raw, genres_raw=genres_raw, rel_dt=rel_dt
                    )
