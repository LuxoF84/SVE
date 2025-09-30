import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Cargar histórico
# -----------------------------
url = "https://raw.githubusercontent.com/LuxoF84/SVE/main/status%20maderas.xlsx"
df_hist = pd.read_excel(url, sheet_name="Hoja1", parse_dates=["Fecha"])

st.set_page_config(page_title="Dashboard Histórico", layout="wide")
st.title("📊 Dashboard Histórico de Inventarios y Estadías")

# -----------------------------
# Filtros
# -----------------------------
st.sidebar.header("🔎 Filtros")

grupos = ["Todos"] + list(df_hist["Grupo"].unique())
grupo_sel = st.sidebar.selectbox("Seleccionar Grupo", grupos)

df_filtrado = df_hist.copy()
if grupo_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Grupo"] == grupo_sel]

# -----------------------------
# 1. Evolución % Utilización
# -----------------------------
st.subheader("📈 Evolución % Utilización")
fig_util = px.line(
    df_filtrado,
    x="Fecha",
    y="% Utilizacion",
    color="Grupo",
    markers=True,
    title="Evolución de la Utilización (%)"
)
st.plotly_chart(fig_util, use_container_width=True)

# -----------------------------
# 2. Evolución Stock
# -----------------------------
st.subheader("📦 Evolución del Stock (m³)")
fig_stock = px.line(
    df_filtrado,
    x="Fecha",
    y="Vol. Stock",
    color="Grupo",
    markers=True,
    title="Evolución del Volumen de Stock"
)
st.plotly_chart(fig_stock, use_container_width=True)

# -----------------------------
# 3. Holgura
# -----------------------------
st.subheader("📉 Evolución de Holgura (m³)")
fig_holgura = px.line(
    df_filtrado,
    x="Fecha",
    y="Holgura m3",
    color="Grupo",
    markers=True,
    title="Evolución de la Holgura"
)
st.plotly_chart(fig_holgura, use_container_width=True)

# -----------------------------
# 4. Stock acumulado (stacked area)
# -----------------------------
st.subheader("🌊 Evolución Acumulada de Stock por Grupo")
fig_area = px.area(
    df_hist,
    x="Fecha",
    y="Vol. Stock",
    color="Grupo",
    title="Stock acumulado en el tiempo por grupo"
)
st.plotly_chart(fig_area, use_container_width=True)

# -----------------------------
# 5. Tabla detallada
# -----------------------------
st.subheader("📋 Datos Históricos")
st.dataframe(df_filtrado)
