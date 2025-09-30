import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

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

# Filtro múltiple de grupos
grupos = list(df_hist["Grupo"].unique())
grupos_sel = st.sidebar.multiselect("Seleccionar Grupos", grupos, default=grupos)

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
if grupos_sel:
    df_filtrado = df_filtrado[df_filtrado["Grupo"].isin(grupos_sel)]

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
# 6. Comparación global (último registro)
# -----------------------------
st.subheader("📊 Comparación de Métricas Globales")

# Tomamos el último registro disponible del dataframe filtrado
df_last = df_filtrado.sort_values("Fecha").tail(1)

if not df_last.empty:
    valores = {
        "Capacidad m3": float(df_last["Capacidad m3"].values[0]),
        "Vol. Consol. c/ Programa": float(df_last["Volumen Consolidable Con Programa"].values[0]),
        "Vol. Consol. s/ Programa": float(df_last["Volumen Consolidable Sin Programa"].values[0]),
        "Vol. E. Incompletas s/ Programa": float(df_last["Volumen E. Incompletas Sin Programa"].values[0]),
        "Stock Piedra": float(df_last[df_last["Grupo"] == "Piedra"]["Vol. Stock"].sum())
    }

    # Pie chart
    fig_pie = px.pie(
        names=list(valores.keys()),
        values=list(valores.values()),
        title="Distribución de métricas"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Velocímetros
    st.subheader("⏱️ Velocímetros de Métricas")
    cols = st.columns(5)
    for i, (k, v) in enumerate(valores.items()):
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            title={'text': k, 'font': {'size': 12}}, 
            number={'font': {'size': 18}}, 
            value=v,
            gauge={'axis': {'range': [0, max(valores.values())*1.2]}}
        ))
        cols[i].plotly_chart(gauge, use_container_width=True)

# -----------------------------
# 7. Tabla detallada
# -----------------------------
st.subheader("📋 Datos Históricos")
df_tabla = df_filtrado.copy()
if "Fecha" in df_tabla.columns:
    df_tabla["Fecha"] = df_tabla["Fecha"].dt.strftime("%Y-%m-%d")  # solo día, mes, año

st.dataframe(df_tabla)


# Leer archivo STOCK.xlsx
# -----------------------------
stock_file = "STOCK.xlsx"   # asegúrate de tenerlo en la misma carpeta del script
df_stock = pd.read_excel(stock_file)
df_stock = df_stock[df_stock["Grupo"] != "CELULOSA"]

# -----------------------------
# Heatmap Volumen vs Antigüedad
# -----------------------------
st.subheader("🔥 Heatmap Volumen vs Antigüedad")

# Crear tabla dinámica (agrupación)
heatmap_data = df_stock.pivot_table(
    values="Volumen",
    index="Grupo",
    columns="Rango_Antiguedad",     # 👈 aquí puedes cambiar a 'Cliente' o 'Bodega' si lo prefieres
    aggfunc="sum",
    fill_value=0
)

# Generar heatmap
fig, ax = plt.subplots(figsize=(9,5))
sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="Reds", linewidths=0.5, ax=ax)

plt.title("Relación Volumen vs Rango de Antigüedad", fontsize=14)
st.pyplot(fig)
