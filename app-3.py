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

# Filtro de grupos
grupos = ["Todos"] + list(df_hist["Grupo"].unique())
grupo_sel = st.sidebar.selectbox("Seleccionar Grupo", grupos)

# Filtro de fechas
fecha_min = df_hist["Fecha"].min().date()
fecha_max = df_hist["Fecha"].max().date()
rango_fechas = st.sidebar.date_input(
    "Seleccionar Rango de Fechas",
    [fecha_min, fecha_max],
    min_value=fecha_min,
    max_value=fecha_max
)

df_filtrado = df_hist.copy()

# Aplicar filtros
if grupo_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Grupo"] == grupo_sel]

if len(rango_fechas) == 2:
    df_filtrado = df_filtrado[
        (df_filtrado["Fecha"].dt.date >= rango_fechas[0]) &
        (df_filtrado["Fecha"].dt.date <= rango_fechas[1])
    ]

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
    df_filtrado,
    x="Fecha",
    y="Vol. Stock",
    color="Grupo",
    title="Stock acumulado en el tiempo por grupo"
)
st.plotly_chart(fig_area, use_container_width=True)

# -----------------------------
# 5. Stock exclusivo "Piedra"
# -----------------------------
if "Piedra" in df_hist["Grupo"].unique():
    st.subheader("🪨 Evolución del Stock de Piedra")
    df_piedra = df_filtrado[df_filtrado["Grupo"] == "Piedra"]

    if not df_piedra.empty:
        fig_piedra = px.line(
            df_piedra,
            x="Fecha",
            y="Vol. Stock",
            markers=True,
            title="Evolución del Volumen de Stock - Piedra"
        )
        st.plotly_chart(fig_piedra, use_container_width=True)
    else:
        st.info("⚠️ No hay datos de Piedra en el rango de fechas seleccionado.")

# -----------------------------
# 6. Tabla detallada
# -----------------------------
st.subheader("📋 Datos Históricos")
st.dataframe(df_filtrado)
