"""
Página de detalles del juego
"""
import streamlit as st
import pandas as pd
from utils.data_utils import fix_nan, safe_appid, parse_date_safe
from utils.game_utils import (
    get_enhanced_game_background, get_steam_app_details, get_steam_store_tags,
    get_game_video, get_platform_icons, format_game_name_for_twitch,
    generate_review_snippets, display_platforms_section
)
from utils.price_utils import format_local_price
from utils.config import FAV_FILE
from components.cards import render_card_controls


def display_game_detail_page(appid, t, df_listado, df_info, df_detalles, df_plataformas):
    """Renderiza la página de detalle del juego"""
    
    g_l = df_listado[df_listado["AppID"] == appid].iloc[0] if not df_listado[df_listado["AppID"] == appid].empty else None
    g_i = df_info[df_info["AppID"] == appid].iloc[0] if not df_info[df_info["AppID"] == appid].empty else pd.Series()
    g_d = df_detalles[df_detalles["AppID"] == appid].iloc[0] if not df_detalles[df_detalles["AppID"] == appid].empty else pd.Series()

    steam_details = get_steam_app_details(appid)
    steam_description = fix_nan(steam_details.get("short_description"), "")
    steam_tags = get_steam_store_tags(appid)

    g_rank = df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)]["Posicion"].iloc[0] if not df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)].empty else "N/A"
    g_players = df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)]["JugadoresConcurrentes"].iloc[0] if not df_listado[(df_listado["AppID"] == appid) & (df_listado["Fecha"] == st.session_state.sel_date)].empty else "N/A"
    rating = fix_nan(g_d.get('Rating'), 'N/A')
    rating_num = pd.to_numeric(rating, errors='coerce')
    reviews = fix_nan(g_d.get('Reviews'), 'N/A')
    reviews_num = pd.to_numeric(reviews, errors='coerce')
    rank_num = pd.to_numeric(g_rank, errors='coerce')
    players_num = pd.to_numeric(g_players, errors='coerce')

    st.title(f"Juego: {fix_nan(g_l['Nombre'] if g_l is not None else t['game_details'])}")

    tab1, tab2, tab3 = st.tabs([t["overview_tab"], t["details_tab"], t["reviews_tab"]])

    with tab1:
        game_name = fix_nan(g_l.get('Nombre') if g_l is not None else 'Game')

        st.markdown(f"""
        <div class="detail-hero">
            <div>
                <img src="{get_enhanced_game_background(appid, game_name)}" alt="{game_name}" />
            </div>
            <div>
                <span class="eyebrow">Versión profesional</span>
                <h1>{game_name}</h1>
                <p>{fix_nan(g_i.get('Desarrollador'))}</p>
                <div class="tag-bar">
                    {''.join(f'<span class="tag-chip">{tag}</span>' for tag in steam_tags[:6])}
                </div>
                <p class="detail-description" style="margin-top: 18px; color: #d1d5db; line-height: 1.7;">{steam_description or 'Descripción no disponible en Steam.'}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t["rating_label"], f"{rating_num}/100" if not pd.isna(rating_num) else "N/A")
        with col2:
            st.metric(t["reviews_label"], f"{int(reviews_num):,}" if not pd.isna(reviews_num) else "N/A")
        with col3:
            st.metric(t["current_rank"], f"#{int(rank_num)}" if not pd.isna(rank_num) else "N/A")
        with col4:
            st.metric(t["current_players"], f"{int(players_num):,}" if not pd.isna(players_num) else "N/A")

        st.markdown("---")
        col_a, col_b, col_c = st.columns([1, 1, 2])
        with col_a:
            st.markdown(f"[![Steam](https://img.icons8.com/color/48/000000/steam.png)](https://store.steampowered.com/app/{appid})", unsafe_allow_html=True)
            st.caption(f"[{t['open_steam']}](https://store.steampowered.com/app/{appid})")
        with col_b:
            game_name_for_twitch = format_game_name_for_twitch(game_name)
            twitch_url = f"https://www.twitch.tv/directory/game/{game_name_for_twitch}" if game_name_for_twitch else "https://www.twitch.tv"
            st.markdown(f"[![Twitch](https://img.icons8.com/color/48/9146FF/twitch.png)]({twitch_url})", unsafe_allow_html=True)
            st.caption(f"[{t['open_twitch']}]({twitch_url})")
        with col_c:
            st.metric(t["price"], format_local_price(g_d.get('Precio', 'N/A'), st.session_state.language))

        st.markdown("---")

        st.markdown(f"## {t['trailer']} & {t['twitch_streams']}")

        media_col1, media_col2 = st.columns(2)

        with media_col1:
            st.markdown(f"### {t['trailer']}")
            video_url = get_game_video(appid)
            if video_url:
                video_html = f"""
                <video controls style="width:100%; border-radius:10px; box-shadow: 0 4px 16px rgba(0,0,0,0.2);" poster="{get_enhanced_game_background(appid, game_name)}">
                    <source src="{video_url}" type="application/x-mpegURL">
                    Your browser does not support HLS video playback.
                </video>
                """
                st.components.v1.html(video_html, height=250)
            else:
                st.markdown(f"[{t['watch_trailer_on_steam']}](https://store.steampowered.com/app/{appid})")

        with media_col2:
            st.markdown(f"### {t['twitch_streams']}")
            if game_name_for_twitch:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #9146FF 0%, #1e1e2e 100%); padding: 30px; border-radius: 15px; text-align: center; color: white; height: 200px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 8px 32px rgba(145, 70, 255, 0.3);">
                    <h3 style="margin: 0 0 15px 0; color: #ffffff;">{t['twitch_streams']}</h3>
                    <p style="margin: 0 0 20px 0; opacity: 0.8;">{t['watch_live_streams_of'].format(game_name=game_name)}</p>
                    <a href="{twitch_url}" target="_blank" style="background: #ffffff; color: #9146FF; padding: 12px 24px; border-radius: 25px; text-decoration: none; font-weight: bold; display: inline-block; transition: all 0.3s ease;">
                        {t['open_twitch']}
                    </a>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f"## {t['information']}")

        info_col1, info_col2 = st.columns(2)

        with info_col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white; margin-bottom: 15px;">
                <h4 style="margin: 0 0 10px 0;">{t['about_game']}</h4>
            </div>
            """, unsafe_allow_html=True)
            st.write(f"**{t['developer_label']}:** {fix_nan(g_i.get('Desarrollador'))}")
            st.write(f"**{t['genres_label']}:** {fix_nan(g_i.get('Géneros'))}")
            st.write(f"**{t['platforms_label']}:** {display_platforms_section(appid, st.session_state.language, df_plataformas)}")
            st.write(f"**{t['release_information']}:** {fix_nan(g_i.get('Fecha_Lanzamiento'))}")

        with info_col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 15px; color: white; margin-bottom: 15px;">
                <h4 style="margin: 0 0 10px 0;">Statistics</h4>
            </div>
            """, unsafe_allow_html=True)
            st.write(f"**{t['current_rank']}:** {fix_nan(g_rank)}")
            st.write(f"**{t['current_players']}:** {fix_nan(g_players)}")
            st.write(f"**{t['price']}:** {format_local_price(g_d.get('Precio', 'N/A'), st.session_state.language)}")

    with tab2:
        st.markdown(f"### {t['details_tab']}")
        detail_rows = {
            t['developer_label']: fix_nan(g_i.get('Desarrollador')),
            t['genres_label']: fix_nan(g_i.get('Géneros')),
            t['platforms_label']: display_platforms_section(appid, st.session_state.language, df_plataformas),
            t['release_information']: fix_nan(g_i.get('Fecha_Lanzamiento')),
            t['price']: format_local_price(g_d.get('Precio', 'N/A'), st.session_state.language),
            t['rating_label']: fix_nan(g_d.get('Rating'), 'N/A'),
            t['reviews_label']: fix_nan(g_d.get('Reviews'), 'N/A'),
            t['current_rank']: fix_nan(g_rank),
            t['current_players']: fix_nan(g_players),
        }
        st.table(pd.DataFrame.from_dict(detail_rows, orient="index", columns=["Value"]))

    with tab3:
        st.markdown(f"### {t['reviews_tab']}")
        if not pd.isna(rating_num):
            st.metric(t["rating_label"], f"{rating_num}/100")
        else:
            st.write(f"**{t['rating_label']}:** N/A")
        if not pd.isna(reviews_num):
            st.metric(t["reviews_label"], f"{int(reviews_num):,}")
        else:
            st.write(f"**{t['reviews_label']}:** N/A")

        review_snippets = generate_review_snippets(
            fix_nan(g_l.get('Nombre') if g_l is not None else 'Juego'),
            rating,
            reviews
        )
        if review_snippets:
            st.markdown("#### Algunas reseñas")
            for snippet in review_snippets:
                st.write(f"- {snippet}")
        else:
            st.write("No hay texto de reseñas disponible en el dataset.")

        if "user" in st.session_state:
            game_title = fix_nan(g_l.get('Nombre') if g_l is not None else t['game_details'])
            try:
                f_df = pd.read_csv(FAV_FILE)
                is_fav = ((f_df['username'] == st.session_state["user"]) & (f_df['appid'] == appid)).any()
            except:
                is_fav = False
            render_card_controls(appid, game_title, "detail", is_fav, t, df_listado, df_info, df_detalles, df_plataformas, compact=False)
