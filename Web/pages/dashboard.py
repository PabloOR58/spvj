"""
Página principal del dashboard
"""
import streamlit as st
import pandas as pd
import re
from utils.data_utils import fix_nan, get_genre_tokens
from utils.game_utils import display_platforms_section
from utils.price_utils import convert_to_usd_numeric
from utils.analytics import compute_popular_releases, compute_trend_scores, get_latest_data_date
from components.metrics import render_hero_banner, render_trend_formula_card
from components.charts import render_advanced_html_dashboard, render_bar_chart, render_line_chart
from components.cards import render_game_card, render_dashboard_card
from components.forms import render_filters


def display_dashboard_page(t, df_listado, df_info, df_detalles, df_plataformas):
    """Renderiza la página principal del dashboard"""
    st.title(t["dashboard_title"])
    
    df_day = df_listado[df_listado["Fecha"] == st.session_state.sel_date].copy()
    
    render_hero_banner(t, df_day)
    
    more_label = "Ver menos juegos" if st.session_state.show_more else "Ver más juegos"
    if st.button(more_label, key="toggle_pro_more"):
        st.session_state.show_more = not st.session_state.show_more
        st.rerun()
    
    render_advanced_html_dashboard(t, df_day, show_more=st.session_state.show_more)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t["players_online"], f"{int(df_day['JugadoresConcurrentes'].sum()):,}")
    m2.metric(t["games_tracked"], f"{len(df_day)}")
    m3.metric(t["top_game"], fix_nan(df_day.iloc[0]["Nombre"]) if len(df_day) > 0 else "N/A")
    m4.metric(t["peak_24h"], f"{len(df_day):,}")

    st.divider()

    t1, t2, t3, t4, t5, t6 = st.tabs([
        t["live_rankings"], t["performance_trend"], t["data_explorer"],
        t["peak_24h_section"], t["popular_releases_title"], t["trend_forecast_title"]
    ])

    with t1:
        render_live_rankings_tab(t, df_day, df_info, df_detalles, df_plataformas)

    with t2:
        render_performance_trend_tab(t, df_listado)

    with t3:
        render_data_explorer_tab(t, df_day, df_info, df_detalles, df_plataformas)

    with t4:
        render_peak_24h_tab(t, df_day, df_info, df_detalles, df_plataformas)

    with t5:
        render_popular_releases_tab(t, df_listado, df_info, df_detalles, df_plataformas)

    with t6:
        render_trends_tab(t, df_listado, df_info)


def render_live_rankings_tab(t, df_day, df_info, df_detalles, df_plataformas):
    """Tab de clasificación en vivo"""
    st.header(t["live_rankings"])
    limit = 100 if st.session_state.show_more else 10
    top_df = df_day.head(limit).reset_index(drop=True)
    
    for r in range(0, len(top_df), 5):
        cols = st.columns(5)
        for i, col in enumerate(cols):
            idx = r + i
            if idx < len(top_df):
                game = top_df.iloc[idx]
                aid = int(game.get("AppID", 0))
                with col:
                    game_name = fix_nan(game.get("Nombre"))
                    pos = int(game.get('Posicion', 0)) if not pd.isna(game.get('Posicion', 0)) else 0
                    players = int(game.get('JugadoresConcurrentes', 0)) if not pd.isna(game.get('JugadoresConcurrentes', 0)) else 0
                    render_game_card(aid, fix_nan(game_name), t, f"lr_{idx}", df_listado, df_info, df_detalles, df_plataformas, extra_caption=f"#{pos}  •  {players:,}")


def render_performance_trend_tab(t, df_listado):
    """Tab de tendencias de rendimiento"""
    st.header(t["performance_trend"])
    st.subheader(t["historical_trends_header"])
    
    dates_list = sorted(df_listado["Fecha"].unique(), reverse=True)
    if len(dates_list) < 2:
        st.info(t.get('no_24h_data', 'Not enough data'))
    else:
        st.subheader(t["market_share"])
        sel_g = st.multiselect(t["compare_games"], sorted(df_listado["Nombre"].unique()), default=[])
        if sel_g:
            selected_date = pd.to_datetime(st.session_state.sel_date, format="%Y-%m-%d", errors="coerce")
            if pd.isna(selected_date):
                st.info("Fecha no válida")
            else:
                one_week_ago = selected_date - pd.Timedelta(days=6)
                filtered = df_listado[df_listado["Nombre"].isin(sel_g)].copy()
                filtered["Fecha_dt"] = pd.to_datetime(filtered["Fecha"], format="%Y-%m-%d", errors="coerce")
                filtered = filtered[(filtered["Fecha_dt"] >= one_week_ago) & (filtered["Fecha_dt"] <= selected_date)]
                pivot = filtered.pivot_table(index="Fecha_dt", columns="Nombre", values="JugadoresConcurrentes").fillna(0)
                if not pivot.empty:
                    st.line_chart(pivot.sort_index())
                else:
                    st.info(t["no_weekly_data"])


def render_data_explorer_tab(t, df_day, df_info, df_detalles, df_plataformas):
    """Tab de explorador de datos"""
    st.header(t.get('data_explorer', 'Data Explorer'))

    explorer_df = df_day.copy()
    explorer_df = explorer_df.merge(df_info[['AppID', 'Géneros', 'Desarrollador']], on='AppID', how='left')
    explorer_df = explorer_df.merge(df_detalles[['AppID', 'Precio', 'Rating']], on='AppID', how='left')
    explorer_df['Precio'] = explorer_df['Precio'].apply(convert_to_usd_numeric)
    explorer_df['JugadoresConcurrentes'] = pd.to_numeric(explorer_df['JugadoresConcurrentes'], errors='coerce').fillna(0)
    explorer_df['Genre_List'] = explorer_df['Géneros'].apply(get_genre_tokens)

    genre_options = sorted({genre for row in explorer_df['Genre_List'] for genre in row})
    dev_options = sorted(explorer_df['Desarrollador'].dropna().astype(str).unique())

    st.subheader(t["filters_title"])
    selected_names, selected_genres, selected_devs, _, selected_price, selected_players = render_filters(
        t, explorer_df, genre_options, dev_options, []
    )


def render_peak_24h_tab(t, df_day, df_info, df_detalles, df_plataformas):
    """Tab de pico 24h"""
    st.subheader(t["peak_24h_section"])
    st.metric(t["peak_24h"], f"{int(df_day['JugadoresConcurrentes'].sum()):,}")

    if len(df_day) > 0:
        top24_df = df_day.sort_values('JugadoresConcurrentes', ascending=False).head(12).reset_index(drop=True)
        cols_per_row = 4
        for r in range(0, len(top24_df), cols_per_row):
            cols = st.columns(cols_per_row)
            for i, col in enumerate(cols):
                idx = r + i
                if idx < len(top24_df):
                    row = top24_df.iloc[idx]
                    aid = int(row.get('AppID', 0))
                    with col:
                        render_dashboard_card(aid, fix_nan(row.get('Nombre')), t, f"p24_{idx}", df_listado, df_info, df_detalles, df_plataformas, players=row.get('JugadoresConcurrentes'))


def render_popular_releases_tab(t, df_listado, df_info, df_detalles, df_plataformas):
    """Tab de lanzamientos populares"""
    st.subheader(t["popular_releases_title"])
    st.markdown(t["popular_releases_description"])

    popular_ref_date = get_latest_data_date(df_listado)
    popular_releases = compute_popular_releases(popular_ref_date, df_info, df_listado)
    if 'is_popular' in popular_releases.columns:
        popular_releases = popular_releases.loc[popular_releases['is_popular']]
    popular_short = popular_releases.sort_values('peak_last_week', ascending=False).head(3).reset_index(drop=True)
    
    if popular_short.empty:
        st.info("No popular releases found.")
    else:
        cols = st.columns(3)
        for idx, col in enumerate(cols):
            if idx < len(popular_short):
                row = popular_short.iloc[idx]
                aid = int(row.get('AppID', 0))
                name = fix_nan(row.get('Nombre'))
                badge = f"TOP {idx + 1}"
                with col:
                    render_dashboard_card(aid, name, t, f"popdash_{idx}", df_listado, df_info, df_detalles, df_plataformas, peak=row.get('peak_last_week'), badge=badge)


def render_trends_tab(t, df_listado, df_info):
    """Tab de tendencias futuras"""
    st.subheader(t["trend_forecast_title"])
    st.markdown(t["trend_forecast_description"])
    render_trend_formula_card(t)

    trend_ref_date = get_latest_data_date(df_listado)
    trend_df = compute_trend_scores(trend_ref_date, 12, df_info, df_listado)

    if trend_df.empty:
        st.info("No trend data available.")
    else:
        trend_df = trend_df.sort_values('Trend Score', ascending=False)
        st.markdown("### Top Trend Games")
        cols_per_row = 4
        for r in range(0, len(trend_df), cols_per_row):
            cols = st.columns(cols_per_row)
            for i, col in enumerate(cols):
                idx = r + i
                if idx < len(trend_df):
                    row = trend_df.iloc[idx]
                    aid = int(row['AppID']) if not pd.isna(row['AppID']) else 0
                    name = fix_nan(row.get('Nombre'))
                    score = row.get('Trend Score', 0)
                    with col:
                        st.metric(label=name, value=f"{score:.0f}")
