"""
Página de chat y asistente IA
"""
import streamlit as st
import pandas as pd
import re
from utils.data_utils import fix_nan
from utils.game_utils import get_game_image
from utils.price_utils import format_local_price, convert_to_usd_numeric


def display_chat_page(t, df_listado, df_info, df_detalles, df_plataformas):
    """Renderiza la página de chat con asistente IA"""
    st.title("Infosteam AI Assistant")
    st.markdown("Asistente Avanzado. Puedes hablarme en lenguaje natural o escribir fragmentos vagos de juegos.")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hola. He analizado los CSVs del sistema. Pregúntame cosas como: '¿qué juegos son gratis?', 'busca juegos de Valve', 'juegos con rating mayor a 90' o un título parcial como 'strike'."}
        ]

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_query := st.chat_input("Escribe tu consulta analítica..."):
        with st.chat_message("user"):
            st.write(user_query)
        st.session_state.chat_messages.append({"role": "user", "content": user_query})

        ai_reply = process_chat_query(user_query, t, df_listado, df_info, df_detalles)

        with st.chat_message("assistant"):
            st.write(ai_reply)
        st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply})
        st.rerun()


def process_chat_query(user_query, t, df_listado, df_info, df_detalles):
    """Procesa una consulta del chat"""
    query_lower = user_query.lower()

    alias_mapping = {
        r"\bcs\b": "counter-strike",
        r"\bcsgo\b": "counter-strike",
        r"\bcs2\b": "counter-strike",
        r"\bgta\b": "grand theft auto",
        r"\bpubg\b": "playerunknown",
        r"\bcod\b": "call of duty"
    }
    for alias, real_name in alias_mapping.items():
        query_lower = re.sub(alias, real_name, query_lower)

    if "gratis" in query_lower or "free" in query_lower:
        df_m = df_detalles.copy()
        df_m['Price_Val'] = df_m['Precio'].apply(convert_to_usd_numeric)
        gratis_df = df_m[df_m['Price_Val'] == 0.0].head(5)
        if not gratis_df.empty:
            ai_reply = "### Juegos Populares Gratuitos Detectados:\n\n"
            for _, r in gratis_df.iterrows():
                ai_reply += f"- **{r['Nombre']}** (Rating: {fix_nan(r.get('Rating'), 'N/A')}/100)\n"
        else:
            ai_reply = "No localicé juegos marcados explícitamente como gratuitos en los datos actuales."

    elif "desarrollador" in query_lower or "creador" in query_lower or "de valve" in query_lower:
        dev_search = query_lower.replace("desarrollador", "").replace("creador", "").replace("de", "").replace("busca", "").strip()
        if not dev_search:
            dev_search = "valve"
        dev_df = df_info[df_info['Desarrollador'].fillna('').astype(str).str.lower().str.contains(dev_search)].head(5)
        if not dev_df.empty:
            ai_reply = f"### Juegos del desarrollador que coincide con '{dev_search.title()}':\n\n"
            for _, r in dev_df.iterrows():
                ai_reply += f"- **{r['Nombre']}** | Géneros: {r.get('Géneros','-')}\n"
        else:
            ai_reply = f"No encontré ningún desarrollador que contenga el término '{dev_search}' en nuestros registros actuales."

    elif "mejor rating" in query_lower or "puntuacion alta" in query_lower or "rating mayor" in query_lower or "buen rating" in query_lower:
        df_r = df_detalles.copy()
        df_r['Rating_Num'] = pd.to_numeric(df_r['Rating'], errors='coerce').fillna(0)
        mejo_df = df_r.sort_values('Rating_Num', ascending=False).head(5)
        ai_reply = "### Los 5 Juegos con Mejor Puntuación Analizados:\n\n"
        for _, r in mejo_df.iterrows():
            ai_reply += f"- **{r['Nombre']}**: {int(r['Rating_Num'])}/100 de valoración positiva.\n"

    else:
        clean_search = query_lower.replace("busca", "").replace("informacion", "").replace("sobre", "").replace("info", "").replace("del", "").replace("juego", "").strip()
        found_games = []
        if len(clean_search) > 1 and not df_info.empty:
            for _, row in df_info.iterrows():
                g_name = str(row.get('Nombre', '')).lower()
                if clean_search in g_name or g_name in clean_search:
                    found_games.append(row)
                    if len(found_games) >= 3:
                        break

        if found_games:
            ai_reply = f"Analizando la base de datos, localicé {len(found_games)} juego(s) vinculados a tu criterio:\n\n"
            for game in found_games:
                appid_found = int(game['AppID'])
                det_row = df_detalles[df_detalles['AppID'] == appid_found]
                precio_game = det_row['Precio'].iloc[0] if not det_row.empty else "N/A"
                rating_game = det_row['Rating'].iloc[0] if not det_row.empty else "N/A"
                df_day_dt = df_listado[df_listado["Fecha"] == st.session_state.sel_date]
                listado_row = df_day_dt[df_day_dt['AppID'] == appid_found]
                players_game = listado_row['JugadoresConcurrentes'].iloc[0] if not listado_row.empty else "N/A"
                precio_local = format_local_price(precio_game, st.session_state.language)
                ai_reply += f"### {game['Nombre']}\n"
                ai_reply += f"- **Desarrollador:** {game.get('Desarrollador', '-')}\n"
                ai_reply += f"- **Géneros:** {game.get('Géneros', '-')}\n"
                ai_reply += f"- **Precio Real:** {precio_local}\n"
                ai_reply += f"- **Rating:** {rating_game}/100\n"
                if isinstance(players_game, (int, float)):
                    ai_reply += f"- **Jugadores concurrentes hoy:** {int(players_game):,}\n"
                else:
                    ai_reply += f"- **Jugadores concurrentes hoy:** {players_game}\n"
                ai_reply += "\n"
        elif "hola" in query_lower or "saludos" in query_lower or "buenas" in query_lower:
            ai_reply = "Hola. Estoy listo. Puedes pedirme listas de juegos por desarrolladores, gratuitos, top ratings o ingresar un trozo de un título."
        elif "mas jugado" in query_lower or "top 1" in query_lower:
            df_day_dt = df_listado[df_listado["Fecha"] == st.session_state.sel_date]
            if not df_day_dt.empty:
                top_1 = df_day_dt.iloc[0]
                ai_reply = f"El líder absoluto de hoy es **{top_1['Nombre']}** registrando **{int(top_1['JugadoresConcurrentes']):,}** usuarios activos."
            else:
                ai_reply = "Sin datos de ranking para la fecha seleccionada."
        else:
            ai_reply = "No encontré coincidencias semánticas directas. Intenta simplificar la búsqueda ingresando palabras clave separadas (ej: 'Counter', 'Dota', 'Valve' o 'gratis')."

    return ai_reply
