"""
Componentes de gráficos y visualizaciones
"""
import streamlit as st
import plotly.graph_objects as go
import json
from utils.data_utils import fix_nan


def render_advanced_html_dashboard(t, df_day, show_more=False):
    """Renderiza dashboard avanzado con Chart.js"""
    top_games = []
    if not df_day.empty:
        limit = 24 if show_more else 8
        for _, row in df_day.head(limit).iterrows():
            top_games.append({
                "name": fix_nan(row.get("Nombre")),
                "rank": int(row.get("Posicion")) if not st.session_state.get("pd").isna(row.get("Posicion")) else None,
                "players": int(row.get("JugadoresConcurrentes")) if not st.session_state.get("pd").isna(row.get("JugadoresConcurrentes")) else 0,
                "appid": int(row.get("AppID")) if not st.session_state.get("pd").isna(row.get("AppID")) else None,
            })

    summary_cards = {
        "players": int(df_day["JugadoresConcurrentes"].sum()) if not df_day.empty else 0,
        "games": len(df_day),
        "top_game": fix_nan(df_day.iloc[0]["Nombre"]) if not df_day.empty else "N/A",
        "active_games": int((df_day["JugadoresConcurrentes"] > 0).sum()) if not df_day.empty else 0,
        "limit": 24 if show_more else 8,
    }

    games_json = json.dumps(top_games)
    html = """
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-3y16fY/1OfRkELRYh6Q+g+fp6cKPa7I9z+gM8Qkzn8oj7W0lTxfDKEk23y5q68sH" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <div class="container-fluid" style="margin-top: 24px; margin-bottom: 24px; color: #e2e8f0;">
      <div class="row g-3">
        <div class="col-12">
          <div class="p-4 rounded-4" style="background: rgba(15, 23, 42, 0.96); border: 1px solid rgba(148, 163, 184, 0.14); box-shadow: 0 26px 70px rgba(0, 0, 0, 0.25);">
            <div class="d-flex flex-column flex-md-row justify-content-between align-items-start gap-3">
              <div>
                <span class="d-inline-block mb-3" style="text-transform: uppercase; letter-spacing: 1px; color: #a78bfa; font-weight: 700;">Interfaz Pro</span>
                <h2 class="mb-3" style="font-size: clamp(2rem, 2.6vw, 2.8rem);">Vista avanzada de métricas y tendencias</h2>
                <p class="mb-0" style="color: #cbd5e1; max-width: 720px;">Panel interactivo construido con HTML y JS para dar una experiencia sofisticada, con tarjetas de datos, gráfico de top juegos y tabla filtrable.</p>
              </div>
              <div class="d-flex gap-2 flex-wrap">
                <span class="badge rounded-pill bg-gradient" style="background: linear-gradient(135deg, #7c3aed, #22c55e); font-size: 0.9rem;">Streamlit + HTML</span>
                <span class="badge rounded-pill bg-gradient" style="background: linear-gradient(135deg, #0ea5e9, #6366f1); font-size: 0.9rem;">Chart.js</span>
              </div>
            </div>
          </div>
        </div>

        <div class="col-12 col-xl-3">
          <div class="p-4 rounded-4" style="background: rgba(30, 41, 59, 0.94); border: 1px solid rgba(148, 163, 184, 0.12);">
            <h5 class="mb-3" style="color: #cbd5e1;">Jugadores totales</h5>
            <div class="display-6 fw-bold">__PLAYERS__</div>
            <p class="mb-0 text-muted">Total en la fecha seleccionada.</p>
          </div>
        </div>
        <div class="col-12 col-xl-3">
          <div class="p-4 rounded-4" style="background: rgba(30, 41, 59, 0.94); border: 1px solid rgba(148, 163, 184, 0.12);">
            <h5 class="mb-3" style="color: #cbd5e1;">Juegos monitorizados</h5>
            <div class="display-6 fw-bold">__GAMES__</div>
            <p class="mb-0 text-muted">Cantidad de títulos cargados en el dataset.</p>
          </div>
        </div>
        <div class="col-12 col-xl-3">
          <div class="p-4 rounded-4" style="background: rgba(30, 41, 59, 0.94); border: 1px solid rgba(148, 163, 184, 0.12);">
            <h5 class="mb-3" style="color: #cbd5e1;">Juego Líder</h5>
            <div class="display-6 fw-bold">__TOP_GAME__</div>
            <p class="mb-0 text-muted">El título con mayor prioridad en el ranking actual.</p>
          </div>
        </div>
        <div class="col-12 col-xl-3">
          <div class="p-4 rounded-4" style="background: rgba(30, 41, 59, 0.94); border: 1px solid rgba(148, 163, 184, 0.12);">
            <h5 class="mb-3" style="color: #cbd5e1;">Activos</h5>
            <div class="display-6 fw-bold">__ACTIVE_GAMES__</div>
            <p class="mb-0 text-muted">Títulos con jugadores en línea.</p>
          </div>
        </div>

        <div class="col-12 col-lg-7">
          <div class="p-4 rounded-4" style="background: rgba(15, 23, 42, 0.98); border: 1px solid rgba(148, 163, 184, 0.12);">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h5 class="mb-0" style="color: #cbd5e1;">Top juegos por jugadores</h5>
                <small class="text-muted">Mostrando los __DISPLAY_LIMIT__ juegos principales</small>
              </div>
              <small class="text-muted">Actualizado al momento</small>
            </div>
            <canvas id="topPlayersChart" height="260"></canvas>
          </div>
        </div>

        <div class="col-12 col-lg-5">
          <div class="p-4 rounded-4" style="background: rgba(15, 23, 42, 0.98); border: 1px solid rgba(148, 163, 184, 0.12);">
            <div class="mb-3">
              <h5 class="mb-2" style="color: #cbd5e1;">Buscar juegos</h5>
              <input id="gameSearch" type="search" class="form-control form-control-dark" placeholder="Filtrar por nombre..." style="background: rgba(255,255,255,0.04); border-color: rgba(148,163,184,0.2); color: #f8fafc;" />
            </div>
            <div class="table-responsive" style="max-height: 360px; overflow-y: auto;">
              <table class="table table-borderless text-white mb-0">
                <thead>
                  <tr style="border-bottom: 1px solid rgba(148,163,184,0.16);">
                    <th class="text-muted">Rank</th>
                    <th class="text-muted">Juego</th>
                    <th class="text-muted">Jugadores</th>
                  </tr>
                </thead>
                <tbody id="gameTableBody"></tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
    <script>
      const topGames = __GAMES_JSON__;

      function buildTable(filtered) {
        const tbody = document.getElementById('gameTableBody');
        tbody.innerHTML = '';
        filtered.forEach(game => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td style="color:#a5b4fc;">${game.rank || '-'}</td>
            <td style="color:#e2e8f0;"><a href="https://store.steampowered.com/app/${game.appid}" target="_blank" style="color:#e2e8f0; text-decoration:none;">${game.name}</a></td>
            <td style="color:#cbd5e1;">${game.players.toLocaleString()}</td>
          `;
          tbody.appendChild(row);
        });
      }

      function renderChart() {
        const labels = topGames.map(game => game.name);
        const values = topGames.map(game => game.players);
        const ctx = document.getElementById('topPlayersChart').getContext('2d');
        new Chart(ctx, {
          type: 'bar',
          data: {
            labels,
            datasets: [{
              label: 'Jugadores concurrentes',
              data: values,
              backgroundColor: 'rgba(99, 102, 241, 0.85)',
              borderRadius: 12,
              maxBarThickness: 32,
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { display: false },
              tooltip: { mode: 'index', intersect: false }
            },
            scales: {
              x: { ticks: { color: '#cbd5e1' }, grid: { display: false } },
              y: { ticks: { color: '#cbd5e1' }, grid: { color: 'rgba(148, 163, 184, 0.12)' } }
            }
          }
        });
      }

      buildTable(topGames);
      renderChart();

      document.getElementById('gameSearch').addEventListener('input', (event) => {
        const query = event.target.value.toLowerCase();
        const filtered = topGames.filter(game => game.name.toLowerCase().includes(query));
        buildTable(filtered);
      });
    </script>
    """
    html = html.replace("__PLAYERS__", f"{summary_cards['players']:,}")
    html = html.replace("__GAMES__", str(summary_cards['games']))
    html = html.replace("__TOP_GAME__", summary_cards["top_game"])
    html = html.replace("__ACTIVE_GAMES__", str(summary_cards["active_games"]))
    html = html.replace("__DISPLAY_LIMIT__", str(summary_cards["limit"]))
    html = html.replace("__GAMES_JSON__", games_json)
    st.components.v1.html(html, height=840)


def render_bar_chart(title, x_data, y_data, x_category_order='total descending'):
    """Renderiza un gráfico de barras"""
    fig = go.Figure(data=[go.Bar(x=x_data, y=y_data)])
    fig.update_layout(xaxis={'categoryorder': x_category_order}, height=400)
    st.plotly_chart(fig, use_container_width=True)


def render_line_chart(title, data_dict):
    """Renderiza un gráfico de líneas"""
    st.line_chart(data_dict.sort_index())
