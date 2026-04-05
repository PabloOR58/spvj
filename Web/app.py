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

import matplotlib.pyplot as plt
# Gráfico de barras para los 10 juegos más jugados
top_10_juegos = df_listado_juegos.nlargest(10, "JugadoresConcurrentes")
plt.figure(figsize=(10, 6))
plt.barh(top_10_juegos["Nombre"], top_10_juegos["JugadoresConcurrentes"], color='skyblue')
plt.xlabel("Número de jugadores concurrentes")
plt.title("Top 10 juegos más jugados en Steam")
plt.gca().invert_yaxis()  # Invertir el eje y para mostrar el juego más jugado en la parte superior
st.pyplot(plt)  

