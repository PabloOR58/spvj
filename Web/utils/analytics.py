"""
Análisis y cálculos de datos para tendencias y ranking
"""
import pandas as pd
from utils.data_utils import parse_date_safe


def peak_players_last_week(appid, ref_date, df_listado):
    """Obtiene el pico de jugadores de la última semana"""
    end_dt = parse_date_safe(ref_date)
    if pd.isna(end_dt) or df_listado.empty:
        return 0
    game_rows = df_listado[df_listado['AppID'] == int(appid)].copy()
    if game_rows.empty:
        return 0
    game_rows['__date'] = pd.to_datetime(game_rows['Fecha'], errors='coerce')
    window = game_rows[(game_rows['__date'] > (end_dt - pd.Timedelta(days=7))) & (game_rows['__date'] <= end_dt)]
    if window.empty:
        return 0
    values = pd.to_numeric(window['JugadoresConcurrentes'], errors='coerce').fillna(0)
    return int(values.max())


def get_previous_week_peak(appid, ref_date, df_listado):
    """Obtiene el pico de jugadores de la semana anterior"""
    end_dt = parse_date_safe(ref_date)
    if pd.isna(end_dt) or df_listado.empty:
        return 0
    game_rows = df_listado[df_listado['AppID'] == int(appid)].copy()
    if game_rows.empty:
        return 0
    game_rows['__date'] = pd.to_datetime(game_rows['Fecha'], errors='coerce')
    prev_window = game_rows[(game_rows['__date'] > (end_dt - pd.Timedelta(days=14))) & (game_rows['__date'] <= (end_dt - pd.Timedelta(days=7)))]
    if prev_window.empty:
        return 0
    values = pd.to_numeric(prev_window['JugadoresConcurrentes'], errors='coerce').fillna(0)
    return int(values.max())


def get_peak_last_24h(ref_date, df_listado):
    """Obtiene el pico total de jugadores de las últimas 24h"""
    end_dt = parse_date_safe(ref_date)
    if pd.isna(end_dt) or df_listado.empty:
        return 0
    day_rows = df_listado.copy()
    day_rows['__date'] = pd.to_datetime(day_rows['Fecha'], errors='coerce')
    window = day_rows[day_rows['__date'] == end_dt]
    if window.empty:
        return 0
    values = pd.to_numeric(window['JugadoresConcurrentes'], errors='coerce').fillna(0)
    return int(values.sum())


def get_latest_data_date(df_listado):
    """Obtiene la fecha más reciente de datos"""
    if df_listado.empty:
        return pd.Timestamp.today()
    dates = pd.to_datetime(df_listado['Fecha'], errors='coerce')
    return dates.max()


def get_recent_releases(ref_date, days, df_info):
    """Obtiene los lanzamientos recientes"""
    ref_dt = parse_date_safe(ref_date)
    if pd.isna(ref_dt) or df_info.empty:
        return pd.DataFrame()
    rel = df_info.copy()
    rel['__release_dt'] = rel['Fecha_Lanzamiento'].apply(parse_date_safe)
    window_start = ref_dt - pd.Timedelta(days=days)
    mask = (
        rel['__release_dt'].notna() &
        (rel['__release_dt'] <= ref_dt) &
        (rel['__release_dt'] >= window_start)
    )
    return rel.loc[mask].copy()


def compute_trend_scores(ref_date, limit, df_info, df_listado):
    """Calcula los scores de tendencia para juegos"""
    ref_dt = parse_date_safe(ref_date)
    if pd.isna(ref_dt) or df_info.empty:
        return pd.DataFrame()

    rows = []
    for _, row in df_info.iterrows():
        appid = int(row.get('AppID', 0)) if not pd.isna(row.get('AppID', 0)) else 0
        if appid <= 0:
            continue
        weekly_peak = peak_players_last_week(appid, ref_dt, df_listado)
        prev_peak = get_previous_week_peak(appid, ref_dt, df_listado)
        growth_7d = weekly_peak - prev_peak
        release_dt = parse_date_safe(row.get('Fecha_Lanzamiento'))
        age_days = (ref_dt - release_dt).days if pd.notna(release_dt) else 90
        recency_score = max(0, 30 - age_days)
        score = (weekly_peak * 0.6) + (growth_7d * 0.3) + (recency_score * 0.1)
        rows.append({
            'AppID': appid,
            'Nombre': row.get('Nombre'),
            'Weekly peak': weekly_peak,
            'Growth 7d': growth_7d,
            'Recency': recency_score,
            'Trend Score': round(score, 2),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.sort_values('Trend Score', ascending=False).head(limit).reset_index(drop=True)


def compute_popular_releases(ref_date, df_info, df_listado):
    """Calcula los lanzamientos populares"""
    recent = get_recent_releases(ref_date, 30, df_info)
    if recent.empty:
        return pd.DataFrame(
            columns=['AppID', 'Nombre', 'Fecha_Lanzamiento', 'peak_last_week', 'is_popular']
        )

    rows = []
    for _, row in recent.iterrows():
        appid = int(row.get('AppID', 0))
        release_dt = parse_date_safe(row.get('Fecha_Lanzamiento'))
        peak_week = peak_players_last_week(appid, ref_date, df_listado)
        rows.append({
            'AppID': appid,
            'Nombre': row.get('Nombre'),
            'Fecha_Lanzamiento': release_dt,
            'peak_last_week': peak_week,
        })

    df_recent = pd.DataFrame(rows)
    df_recent['is_popular'] = False

    for idx, row in df_recent.iterrows():
        if pd.isna(row['Fecha_Lanzamiento']):
            continue
        window_start = row['Fecha_Lanzamiento'] - pd.Timedelta(days=7)
        window_end = row['Fecha_Lanzamiento'] + pd.Timedelta(days=7)
        peers = df_recent[(df_recent['AppID'] != row['AppID']) &
                          (df_recent['Fecha_Lanzamiento'] >= window_start) &
                          (df_recent['Fecha_Lanzamiento'] <= window_end)]
        if peers.empty:
            df_recent.at[idx, 'is_popular'] = True
        else:
            df_recent.at[idx, 'is_popular'] = int(row['peak_last_week']) > int(peers['peak_last_week'].max())

    return df_recent.sort_values(['is_popular', 'peak_last_week'], ascending=[False, False]).reset_index(drop=True)
