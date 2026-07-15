"""
Componentes de tarjetas de juegos y controles
"""
import streamlit as st
import pandas as pd
from utils.data_utils import fix_nan, safe_appid, parse_date_safe
from utils.game_utils import get_enhanced_game_image, get_enhanced_game_background
from utils.price_utils import format_local_price
from utils.config import FAV_FILE, IMG_ERROR


def render_card_controls(aid, name, key_prefix, is_fav, t, df_listado, df_info, df_detalles, df_plataformas, compact=False):
    """Renderiza controles de tarjeta (detalles + favoritos)"""
    from utils.game_utils import display_platforms_section
    
    safe_id = safe_appid(aid)
    det_key = f"{key_prefix}_det_dash" if compact else f"{key_prefix}_det"
    remove_key = f"{key_prefix}_removefav_dash" if compact else f"{key_prefix}_removefav"
    add_key = f"{key_prefix}_addfav_dash" if compact else f"{key_prefix}_addfav"

    c1, c2 = st.columns([1, 1])
    with c1:
        if safe_id is None:
            st.button(t["details"], key=det_key, disabled=True)
        elif st.button(t["details"], key=det_key):
            st.session_state.selected_game = safe_id
            st.rerun()
    with c2:
        if "user" not in st.session_state:
            return
        try:
            f_df = pd.read_csv(FAV_FILE)
        except:
            f_df = pd.DataFrame(columns=["username", "appid"])
        if is_fav:
            if safe_id is not None and st.button(t.get('remove_from_favorites', 'Quitar de favoritos'), key=remove_key):
                f_df = f_df[~((f_df['username'] == st.session_state['user']) & (f_df['appid'] == safe_id))]
                f_df.to_csv(FAV_FILE, index=False)
                st.success(t.get('remove_from_favorites', 'Quitar de favoritos'))
                st.rerun()
        else:
            if safe_id is not None and st.button(t.get('add_to_favorites', 'Añadir a favoritos'), key=add_key):
                new_fav = pd.DataFrame([[st.session_state['user'], safe_id]], columns=["username", "appid"])
                pd.concat([f_df, new_fav], ignore_index=True).to_csv(FAV_FILE, index=False)
                st.success(f"{t.get('saved', 'Guardado')} {name}")
                st.rerun()


def render_game_card(aid, name, t, key_prefix, df_listado, df_info, df_detalles, df_plataformas, 
                     price_raw=None, genres_raw=None, rating=None, reviews=None, rel_dt=None, extra_caption=None):
    """Renderiza una tarjeta de juego estándar"""
    from utils.game_utils import display_platforms_section
    
    title_attr = f"{name}"
    img_url = get_enhanced_game_image(aid, name)
    
    badge_html = ''
    is_fav = False
    safe_id = safe_appid(aid)
    if "user" in st.session_state and safe_id is not None:
        try:
            f_df = pd.read_csv(FAV_FILE)
            is_fav = ((f_df['username'] == st.session_state['user']) & (f_df['appid'] == safe_id)).any()
        except:
            is_fav = False
        if is_fav:
            badge_html = '<div class="badge pulse" style="position:absolute; right:8px; top:8px; background:#ff6b81; color:#ffffff; padding:4px 8px; border-radius:12px; font-weight:700; font-size:11px;" title="Favorito">FAVORITO</div>'
        else:
            badge_html = '<div class="badge" style="position:absolute; right:8px; top:8px; background:#4b5563; color:#ffffff; padding:4px 8px; border-radius:12px; font-weight:700; font-size:11px;" title="'+t.get('add_to_favorites','Añadir a favoritos')+'">DISPONIBLE</div>'

    overlay_lines = []
    if rel_dt is not None:
        try:
            rel_str = parse_date_safe(rel_dt).strftime('%Y-%m-%d') if not pd.isna(parse_date_safe(rel_dt)) else fix_nan(rel_dt)
            overlay_lines.append(f"{t['release_date']}: {rel_str}")
        except:
            pass
    if genres_raw:
        overlay_lines.append(f"{t['genres_label']}: {fix_nan(genres_raw)}")
    if rating is not None:
        overlay_lines.append(f"{t['rating_label']}: {fix_nan(rating)}")
    if reviews is not None and not pd.isna(reviews):
        overlay_lines.append(f"{t['reviews_label']}: {int(pd.to_numeric(reviews, errors='coerce')):,}")
    if safe_id is not None:
        try:
            info_row = df_info[df_info['AppID'] == safe_id]
            det_row = df_detalles[df_detalles['AppID'] == safe_id]
            if not info_row.empty:
                dev = fix_nan(info_row['Desarrollador'].iloc[0])
                if dev and dev.lower() != 'nan':
                    overlay_lines.insert(0, f"{t['developer_label']}: {dev}")
                platforms = display_platforms_section(aid, st.session_state.language, df_plataformas)
                if platforms:
                    overlay_lines.append(platforms)
            if not det_row.empty and rating is None:
                det_rating = fix_nan(det_row['Rating'].iloc[0], None)
                if pd.notna(det_rating):
                    overlay_lines.append(f"{t['rating_label']}: {det_rating}")
            if not det_row.empty and (reviews is None or pd.isna(reviews)):
                det_reviews = pd.to_numeric(det_row['Reviews'].iloc[0], errors='coerce')
                if not pd.isna(det_reviews):
                    overlay_lines.append(f"{t['reviews_label']}: {int(det_reviews):,}")
        except:
            pass
    if extra_caption:
        overlay_lines.append(extra_caption)
    overlay_html = ''
    if overlay_lines:
        overlay_html = '<div class="game-card__overlay">' + '<br>'.join(overlay_lines) + '</div>'

    st.markdown(f'<div class="game-card" style="height: 140px; overflow: hidden; border-radius: 8px; background: #161921; position:relative;"><img src="{img_url}" onerror=\'this.src="{IMG_ERROR}";\' title="{title_attr}">{overlay_html}{badge_html}</div>', unsafe_allow_html=True)
    st.markdown(f"**{name}**")
    lines = []
    if rel_dt is not None:
        try:
            rel_str = parse_date_safe(rel_dt).strftime('%Y-%m-%d') if not pd.isna(parse_date_safe(rel_dt)) else fix_nan(rel_dt)
            lines.append(f"{t['release_date']}: {rel_str}")
        except:
            pass
    if extra_caption:
        lines.append(extra_caption)
    if lines:
        st.caption("  •  ".join(lines))

    if genres_raw:
        st.write(f"**{t['genres_label']}:** {fix_nan(genres_raw)}")
    if rating is not None:
        st.write(f"**{t['rating_label']}:** {fix_nan(rating)}")
    if reviews is not None and not pd.isna(reviews):
        st.write(f"**{t['reviews_label']}:** {int(pd.to_numeric(reviews, errors='coerce')):,}")

    render_card_controls(aid, name, key_prefix, is_fav, t, df_listado, df_info, df_detalles, df_plataformas, compact=False)


def render_dashboard_card(aid, name, t, key_prefix, df_listado, df_info, df_detalles, df_plataformas,
                          small_image_height=110, badge=None, players=None, peak=None):
    """Renderiza una tarjeta compacta para dashboard"""
    from utils.game_utils import display_platforms_section
    
    img_url = get_enhanced_game_image(aid, name)
    
    badge_color = '#ffbf47'
    card_gradient = 'linear-gradient(135deg, #0f1720 0%, #111827 100%)'
    try:
        if badge == 'POP':
            badge_color = '#9b5cff'
            card_gradient = 'linear-gradient(135deg, #6b21a8 0%, #111827 100%)'
        elif badge == '▲':
            badge_color = '#16a34a'
            card_gradient = 'linear-gradient(135deg, #052e18 0%, #08301a 100%)'
        elif peak is not None and float(peak) < 0:
            badge_color = '#ef4444'
            card_gradient = 'linear-gradient(135deg, #2b0f0f 0%, #111827 100%)'
        elif players is not None and int(players) > 100000:
            badge_color = '#f97316'
            card_gradient = 'linear-gradient(135deg, #3a0f00 0%, #111827 100%)'
    except:
        pass
    pulse_class = ' pulse' if badge == 'POP' else ''
    badge_html = f'<div class="badge{pulse_class}" style="background:{badge_color};">{badge}</div>' if badge else ''
    
    fav_badge_html = ''
    is_fav_dash = False
    safe_id = safe_appid(aid)
    if "user" in st.session_state and safe_id is not None:
        try:
            f_df = pd.read_csv(FAV_FILE)
            is_fav_dash = ((f_df['username'] == st.session_state['user']) & (f_df['appid'] == safe_id)).any()
            if is_fav_dash:
                fav_badge_html = '<div class="badge" style="position:absolute; left:8px; top:8px; background:#ff6b81; color:#ffffff; padding:4px 6px; border-radius:12px; font-weight:700; font-size:9px;" title="Favorito">FAV</div>'
            else:
                fav_badge_html = '<div class="badge" style="position:absolute; left:8px; top:8px; background:#4b5563; color:#ffffff; padding:4px 6px; border-radius:12px; font-weight:700; font-size:9px;" title="'+t.get('add_to_favorites','Añadir a favoritos')+'">ADD</div>'
        except:
            is_fav_dash = False

    overlay_lines = []
    try:
        info_row = df_info[df_info['AppID'] == aid]
        details_row = df_detalles[df_detalles['AppID'] == aid]
        if not info_row.empty:
            developer = fix_nan(info_row['Desarrollador'].iloc[0])
            if developer and developer.lower() != 'nan':
                overlay_lines.append(f"{t['developer_label']}: {developer}")
            release_date = parse_date_safe(info_row['Fecha_Lanzamiento'].iloc[0])
            if pd.notna(release_date):
                overlay_lines.append(f"{t['release_date']}: {release_date.strftime('%Y-%m-%d')}")
            genres = fix_nan(info_row['Géneros'].iloc[0])
            if genres and genres.lower() != 'nan':
                overlay_lines.append(f"{t['genres_label']}: {genres}")
            platforms = display_platforms_section(aid, st.session_state.language, df_plataformas)
            if platforms:
                overlay_lines.append(platforms)
    except:
        pass
    if players is not None:
        overlay_lines.append(f"Jugadores: {int(players):,}")
    if peak is not None:
        overlay_lines.append(f"Pico: {int(peak):,}")
    overlay_html = ''
    if overlay_lines:
        overlay_html = '<div class="dashboard-card__overlay">' + '<br>'.join(overlay_lines[:4]) + '</div>'

    st.markdown(f'<div class="dashboard-card" style="position:relative; height:{small_image_height}px; overflow:hidden; border-radius:8px; background:{card_gradient}; box-shadow:0 6px 18px rgba(0,0,0,0.4);"><img src="{img_url}" onerror=\'this.src="{IMG_ERROR}";\'>{overlay_html}{badge_html}{fav_badge_html}</div>', unsafe_allow_html=True)
    st.markdown(f"**{name}**")
    meta = []
    if players is not None:
        meta.append(f"Jugadores: {int(players):,}")
    if peak is not None:
        meta.append(f"Pico: {int(peak):,}")
    if meta:
        st.caption("  •  ".join(meta))

    render_card_controls(aid, name, key_prefix, is_fav_dash, t, df_listado, df_info, df_detalles, df_plataformas, compact=True)
