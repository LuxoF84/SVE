import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Inventarios", layout="wide")

st.title("📊 Dashboard de Inventarios - Situación de Stock")

# === Cargar archivo desde GitHub ===
url = "https://raw.githubusercontent.com/LuxoF84/SVE/main/estadias.xlsx"
df = pd.read_excel(url, parse_dates=["Fecha", "Fecha_Ultimo_Movimiento"])

# === Preparación de datos ===
df["Holgura_m3"] = df["Capacidad_m3"] - df["Vol_Stock"]
df["Antiguedad_dias"] = (pd.Timestamp.today() - df["Fecha_Ultimo_Movimiento"]).dt.days

# Crear buckets de antigüedad
bins = [0,15,30,60,90,9999]
labels = ["0-15","16-30","31-60","61-90","91+"]
df["Bucket_Antiguedad"] = pd.cut(df["Antiguedad_dias"], bins=bins, labels=labels)

# === KPIs globales ===
col1, col2, col3, col4 = st.columns(4)
col1.metric("Utilización (%)", f"{df['Vol_Stock'].sum()/df['Capacidad_m3'].sum():.1%}")
col2.metric("Holgura total (m3)", f"{df['Holgura_m3'].sum():,.0f}")
col3.metric("CT Pendientes", int(df["CT_Consolidables_SinPrograma"].sum() + df["CT_SinPrograma_Incompletas"].sum()))
col4.metric("% Stock Piedra", f"{df['Stock_Piedra'].sum()/df['Vol_Stock'].sum():.1%}")

st.markdown("---")

# === Filtro por grupo ===
grupos = ["Todos"] + df["Grupo"].unique().tolist()
grupo_sel = st.selectbox("Filtrar por Grupo", options=grupos)
if grupo_sel != "Todos":
    df = df[df["Grupo"] == grupo_sel]

# === Gráficos ===
# Ocupación por grupo
fig1 = px.bar(df.groupby("Grupo")[["Vol_Stock","Holgura_m3"]].sum().reset_index(),
              x="Grupo", y=["Vol_Stock","Holgura_m3"], 
              title="Ocupación y Holgura por Grupo", barmode="stack")
st.plotly_chart(fig1, use_container_width=True)

# Distribución de stock
dist = df[["Vol_Consolidable_Programa","Vol_Consolidable_SinPrograma",
           "Vol_Incompleto_SinPrograma","Stock_Piedra"]].sum()
fig2 = px.pie(values=dist.values, names=dist.index, title="Distribución de Stock")
st.plotly_chart(fig2, use_container_width=True)

# Antigüedad
antig = df.groupby("Bucket_Antiguedad")["Vol_Stock"].sum().reset_index()
fig3 = px.bar(antig, x="Bucket_Antiguedad", y="Vol_Stock", 
              title="Volumen por Antigüedad", text_auto=True)
st.plotly_chart(fig3, use_container_width=True)

# === Tabla detallada ===
st.subheader("📋 Detalle de Stock")
st.dataframe(df)
