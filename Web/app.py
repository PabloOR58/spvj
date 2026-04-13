import streamlit as st
import pandas as pd
import os
import subprocess

# ---------- Page config ----------
st.set_page_config(
    page_title="infosteam - Most Played Games",
    page_icon="🎮",
    layout="wide",
)

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "Clean")
LISTADO_CSV = os.path.join(CLEAN_DIR, "listado_juegos.csv")
INFO_CSV = os.path.join(CLEAN_DIR, "info_juegos.csv")
DETALLES_CSV = os.path.join(CLEAN_DIR, "detalles_juegos.csv")
DOWNLOAD_SCRIPT = os.path.join(BASE_DIR, "Src", "download.py")


# ---------- Load data ----------
@st.cache_data(ttl=300)
def load_listado():
    """Load daily player rankings."""
    if os.path.exists(LISTADO_CSV):
        return pd.read_csv(LISTADO_CSV)
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_info():
    """Load game metadata (genres, developer)."""
    if os.path.exists(INFO_CSV):
        return pd.read_csv(INFO_CSV)
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_detalles():
    """Load game details (price, rating, reviews)."""
    if os.path.exists(DETALLES_CSV):
        return pd.read_csv(DETALLES_CSV, on_bad_lines="skip")
    return pd.DataFrame()


def get_game_image(appid):
    """Header image URL for a Steam game."""
    return f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"


# ---------- Load all data ----------
df_listado = load_listado()
df_info = load_info()
df_detalles = load_detalles()

if df_listado.empty:
    st.warning("No data found. Run the download script first.")
    st.stop()

dates = sorted(df_listado["Fecha"].unique(), reverse=True)


# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")

    # Date selector — affects the whole dashboard
    selected_date = st.selectbox("📅 Select date:", dates)

    st.divider()

    if st.button("🔄 Update data from Steam"):
        with st.spinner("Downloading from Steam API..."):
            try:
                result = subprocess.run(
                    ["python", DOWNLOAD_SCRIPT],
                    capture_output=True, text=True, timeout=300,
                    cwd=BASE_DIR,
                )
                if result.returncode == 0:
                    st.cache_data.clear()
                    st.success("Data updated!")
                    st.rerun()
                else:
                    st.error(f"Error: {result.stderr}")
            except Exception as e:
                st.error(f"Could not update: {e}")

    st.divider()

    if st.button("🔄 Refresh view"):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.caption("Data from your CSV files in Clean/.")
    st.caption(f"Available dates: {len(dates)}")
    st.caption(f"Range: {dates[-1]} → {dates[0]}")


# ---------- Filter data by selected date ----------
df_day = df_listado[df_listado["Fecha"] == selected_date].copy()

if df_day.empty:
    st.warning(f"No data for {selected_date}.")
    st.stop()


# ---------- Page header ----------
st.title("🎮 infosteam")
st.caption(f"Most Played Games on Steam — {selected_date}")


# ---------- Summary metrics ----------
c1, c2, c3 = st.columns(3)
c1.metric("🟢 Players Online", f"{df_day['JugadoresConcurrentes'].sum():,}")
c2.metric("🎮 Games Tracked", len(df_day))
c3.metric("🏆 Most Played", df_day.iloc[0]["Nombre"])
st.divider()


# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["📊 Rankings", "📈 7-Day Trend", "📋 Data Table"])


# ---- Tab 1: game cards (top 10) ----
with tab1:
    top10 = df_day.head(10).reset_index(drop=True)

    for row_start in range(0, len(top10), 5):
        cols = st.columns(5)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx >= len(top10):
                break
            game = top10.iloc[idx]
            with col:
                appid = int(game["AppID"])
                st.image(get_game_image(appid), use_container_width=True)
                st.markdown(f"**#{int(game['Posicion'])} {game['Nombre']}**")
                st.metric("Players", f"{int(game['JugadoresConcurrentes']):,}")

                # show extra info if available
                if not df_info.empty and appid in df_info["AppID"].values:
                    row_info = df_info[df_info["AppID"] == appid].iloc[0]
                    genres = row_info.get("Géneros", "")
                    if pd.notna(genres):
                        st.caption(f"🏷️ {genres}")

                if not df_detalles.empty and appid in df_detalles["AppID"].values:
                    row_det = df_detalles[df_detalles["AppID"] == appid].iloc[0]
                    price = row_det.get("Precio", "")
                    if pd.notna(price):
                        st.caption(f"💰 {price}")


# ---- Tab 2: 7-day trend ----
with tab2:
    st.subheader("📈 Player Trends")

    # find the position of selected_date and get 7 dates around it
    date_idx = dates.index(selected_date)
    trend_dates = dates[max(0, date_idx):min(len(dates), date_idx + 7)]

    if len(trend_dates) > 1:
        df_trend = df_listado[df_listado["Fecha"].isin(trend_dates)].copy()

        # top 10 games from selected date for default selection
        top_names = df_day.head(10)["Nombre"].tolist()
        all_names = sorted(df_trend["Nombre"].unique().tolist())

        selected_games = st.multiselect(
            "Select games to compare:",
            all_names,
            default=top_names[:5],
        )

        if selected_games:
            filtered = df_trend[df_trend["Nombre"].isin(selected_games)]
            chart_data = filtered.pivot_table(
                index="Fecha",
                columns="Nombre",
                values="JugadoresConcurrentes",
                aggfunc="first",
            )
            st.line_chart(chart_data)
        else:
            st.info("Select at least one game above.")
    else:
        st.info(
            "📊 Trend data needs 2+ days of snapshots. "
            "Run the download script daily to build trends."
        )

    # bar chart for the selected date
    st.subheader(f"📊 Players Comparison — {selected_date} (Top 20)")
    bar_data = df_day.head(20).set_index("Nombre")[["JugadoresConcurrentes"]].sort_values(
        "JugadoresConcurrentes", ascending=True
    )
    st.bar_chart(bar_data)


# ---- Tab 3: data table ----
with tab3:
    st.subheader(f"📋 Data — {selected_date}")

    show_cols = ["Posicion", "Nombre", "JugadoresConcurrentes", "AppID"]
    st.dataframe(df_day[show_cols], use_container_width=True, hide_index=True)

    # download
    csv_data = df_day[show_cols].to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name=f"infosteam_{selected_date}.csv",
        mime="text/csv",
    )


# ---------- Footer ----------
st.divider()
st.caption("© 2026 infosteam — Data from Steam Web API")