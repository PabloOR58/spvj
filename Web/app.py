import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import ast

#Titulo de la aplicacion

st.title("Infosteam")

#Lectura del csv que queremos mostrar en la aplicacion
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir,"clean", "info_juegos.csv")
df_info_juegos= pd.read_csv(csv_path)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path_listado_juegos = os.path.join(base_dir,"clean", "listado_juegos.csv")
df_listado_juegos= pd.read_csv(csv_path_listado_juegos)



st.write(df_listado_juegos.head(3))

#Estadisticas generales
col1, col2, col3 = st.columns(3)

col1.metric("Número de juegos", df_info_juegos.shape[0])

col2.metric("Número de jugadores actuales en steam", df_listado_juegos["JugadoresConcurrentes"].sum())

col3.metric("Juego más jugado en este momento", df_listado_juegos.loc[df_listado_juegos["JugadoresConcurrentes"].idxmax(), "Nombre"])

# Selector de fecha
selected_date = st.date_input("Selecciona una fecha", value=pd.to_datetime(df_listado_juegos.iloc[0]['Fecha'] if 'Fecha' in df_listado_juegos.columns else None))

# Filtrar datos por fecha
df_filtered = df_listado_juegos[pd.to_datetime(df_listado_juegos['Fecha']).dt.date == selected_date]

if df_filtered.empty:
    st.warning("No hay datos para la fecha seleccionada")
else:
    # Gráfico de barras para los 10 juegos más jugados
    top_10_juegos = df_filtered.nlargest(10, "JugadoresConcurrentes")

    plt.figure(figsize=(12, 6))
    plt.barh(top_10_juegos["Nombre"], top_10_juegos["JugadoresConcurrentes"])
    plt.xlabel("Jugadores Concurrentes")
    plt.tight_layout()
    st.pyplot(plt)

