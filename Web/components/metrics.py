"""
Componentes de métricas y números
"""
import streamlit as st
from utils.data_utils import fix_nan


def render_metrics_row(metrics_dict, columns=4):
    """Renderiza una fila de métricas"""
    cols = st.columns(columns)
    for idx, (label, value) in enumerate(metrics_dict.items()):
        with cols[idx % columns]:
            st.metric(label, value)


def render_hero_banner(t, df_day):
    """Renderiza el banner hero del dashboard"""
    total_players = int(df_day["JugadoresConcurrentes"].sum()) if not df_day.empty else 0
    total_games = len(df_day)
    top_game = fix_nan(df_day.iloc[0]["Nombre"]) if not df_day.empty else "N/A"
    today = st.session_state.sel_date if st.session_state.sel_date else "N/A"
    
    hero_html = f"""
    <div class="hero-banner">
      <div class="hero-left">
        <span class="eyebrow">infosteam</span>
        <h1>Dashboard profesional de juegos y tendencias</h1>
        <p>Visualiza métricas clave, rendimiento en vivo y detalles enriquecidos de Steam en una interfaz moderna y elegante.</p>
      </div>
      <div class="hero-right">
        <div class="metric-card">
          <div class="metric-label">{t['players_online']}</div>
          <div class="metric-value">{total_players:,}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{t['games_tracked']}</div>
          <div class="metric-value">{total_games}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{t['top_game']}</div>
          <div class="metric-value">{top_game}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{t['data_date']}</div>
          <div class="metric-value">{today}</div>
        </div>
      </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)


def render_trend_formula_card(t):
    """Renderiza la tarjeta con la fórmula de tendencia"""
    formula_html = f'''
    <div style="background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border-radius:18px; padding:20px; color:#e2e8f0; box-shadow:0 24px 60px rgba(15,23,42,0.35);">
      <div style="font-size:1.1rem; font-weight:700; margin-bottom:10px;">{t['trend_formula_title']}</div>
      <div style="color:#94a3b8; margin-bottom:16px; line-height:1.5;">{t['trend_formula_description']}</div>
      <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(148,163,184,0.18); padding:14px; border-radius:14px; font-family:monospace; font-size:0.95rem; color:#f8fafc; white-space:pre-wrap;">{t['trend_formula_equation']}</div>
      <div style="margin-top:14px; color:#cbd5e1; font-size:0.92rem;">{t['trend_formula_note']}</div>
    </div>
    '''
    st.markdown(formula_html, unsafe_allow_html=True)
