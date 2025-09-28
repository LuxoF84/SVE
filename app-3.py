import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# -----------------------------
# Cargar datos desde GitHub
# -----------------------------
url = "https://raw.githubusercontent.com/LuxoF84/SVE/main/estadias.xlsx"
df = pd.read_excel(url, parse_dates=["Fecha"])

# -----------------------------
# Configuración del dashboard
# -----------------------------
st.set_page_config(page_title="Dashboard Logístico", layout="wide")
st.title("📊 Dashboard de Inventarios y Estadías")

# -----------------------------
# Filtros
# -----------------------------
st.sidebar.header("🔎 Filtros")

fechas = sorted(df["Fecha"].unique())
fecha_sel = st.sidebar.selectbox("Seleccionar Fecha", fechas, index=len(fechas)-1)

grupos = ["Todos"] + list(df["Grupo"].unique())
grupo_sel = st.sidebar.selectbox("Seleccionar Grupo", grupos)

# Aplicar filtros
df_filtrado = df[df["Fecha"] == fecha_sel]
if grupo_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Grupo"] == grupo_sel]

# -----------------------------
# KPIs globales
# -----------------------------
st.subheader("🔑 Indicadores Clave")

total_capacidad = df_filtrado["Capacidad m3"].sum()
total_stock = df_filtrado["Vol. Stock"].sum()
utilizacion = (total_stock / total_capacidad) * 100 if total_capacidad > 0 else 0
holgura = df_filtrado["Holgura m3"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Capacidad Total (m³)", f"{total_capacidad:,.0f}")
col2.metric("Stock Actual (m³)", f"{total_stock:,.0f}")
col3.metric("% Utilización", f"{utilizacion:.1f}%")
col4.metric("Holgura Total (m³)", f"{holgura:,.0f}")

# -----------------------------
# Velocímetros por Grupo
# -----------------------------
st.subheader("⏱️ Utilización por Grupo (Velocímetros)")

col1, col2, col3, col4 = st.columns(4)
grupos = df_filtrado["Grupo"].unique()

for i, grupo in enumerate(grupos):
    df_g = df_filtrado[df_filtrado["Grupo"] == grupo]
    if not df_g.empty:
        valor = df_g["% Utilizacion"].values[0]
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=valor,
            title={'text': f"{grupo}"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green" if valor < 70 else "orange" if valor < 90 else "red"}
            }
        ))
        if i == 0:
            col1.plotly_chart(gauge, use_container_width=True)
        elif i == 1:
            col2.plotly_chart(gauge, use_container_width=True)
        elif i == 2:
            col3.plotly_chart(gauge, use_container_width=True)
        elif i == 3:
            col4.plotly_chart(gauge, use_container_width=True)

# -----------------------------
# Ocupación por Grupo (Barras)
# -----------------------------
st.subheader("📦 Ocupación por Grupo")

fig_bar = px.bar(
    df_filtrado,
    x="Grupo",
    y="Vol. Stock",
    color="Grupo",
    text="Vol. Stock",
    title="Volumen de Stock por Grupo"
)
st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# Distribución de Stock (Pie)
# -----------------------------
st.subheader("🥧 Distribución de % de Stock por Grupo")

fig_pie = px.pie(
    df_filtrado,
    names="Grupo",
    values="Vol. Stock",
    title="Participación de Stock por Grupo"
)
st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------
# Heatmap de Antigüedad
# -----------------------------
st.subheader("🔥 Heatmap de Antigüedad de Cargas")

max_fecha = df["Fecha"].max()
df["Antiguedad_dias"] = (max_fecha - df["Fecha"]).dt.days

pivot = df.pivot_table(
    values="Vol. Stock",
    index="Grupo",
    columns="Antiguedad_dias",
    aggfunc="sum",
    fill_value=0
)

fig, ax = plt.subplots(figsize=(10, 5))
sns.heatmap(pivot, cmap="YlOrRd", annot=False, cbar_kws={'label': 'Volumen Stock (m³)'}, ax=ax)
st.pyplot(fig)

# -----------------------------
# Tabla detallada
# -----------------------------
st.subheader("📋 Tabla Detallada de Datos")
st.dataframe(df_filtrado)
