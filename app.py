import streamlit as st
import pandas as pd
import polars as pl
import plotly.express as px
from datetime import datetime

# --- Configuración base ---
st.set_page_config(page_title="Dashboard Maderas", layout="wide")

# --- Carga de datos ---
@st.cache_data
def load_data():
    GITHUB_BASE = "https://raw.githubusercontent.com/LuxoF84/SVE/main/"
    df_resumen = pd.read_excel(GITHUB_BASE + "estadias.xlsx")
    df_stock_completo = pd.read_excel(GITHUB_BASE + "STOCK.xlsx")
    return df_resumen, df_stock_completo

df_resumen, df_stock_completo = load_data()

# --- Encabezado ---
st.markdown("<h1 style='text-align:center;'>Dashboard Maderas - SVE</h1>", unsafe_allow_html=True)

# --- 4. Gráficos en el centro (Pie y Bar) ---
#################################################################################
# 🔴 SECCIÓN DESACTIVADA
# A solicitud del usuario, se eliminan los gráficos:
#   - % de Utilización por Grupo (Pie Chart)
#   - Volumen por Tipo de Programa (Bar Chart)
#
# Esta sección se mantiene comentada para evitar errores en el flujo del script.
#################################################################################

# (Antes aquí se mostraban los gráficos de resumen general)
# Se omiten completamente para mantener la app más limpia visualmente.

# Si en el futuro se desean reactivar, basta con restaurar la sección original.
#################################################################################

# --- 5. Gráficos Adicionales (de la tabla de STOCK completa) --- 
st.markdown("<h2 style='text-align: center;'>Análisis de Volumen de Stock Completo</h2>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

def categorizar_antiguedad(fecha):
    if pd.isna(fecha):
        return "Sin Fecha"
    dias = (datetime.now() - fecha).days
    if dias <= 15:
        return "0-15 dias"
    elif dias <= 30:
        return "16-30 dias"
    elif dias <= 60:
        return "31-60 dias"
    elif dias <= 90:
        return "61-90 dias"
    else:
        return "90 dias o mas"

if 'Fecha_Recepcion' in df_stock_completo.columns:
    df_stock_completo['Fecha_Recepcion'] = pd.to_datetime(df_stock_completo['Fecha_Recepcion'], errors='coerce')
    df_stock_completo['Rango_Antiguedad'] = df_stock_completo['Fecha_Recepcion'].apply(categorizar_antiguedad)

    # --- GRÁFICO 1: PIE CHART POR GRUPO (PLOTLY) ---
    with col1:
        df_stock_volumen = df_stock_completo.dropna(subset=['Volumen']).groupby('Grupo')['Volumen'].sum().reset_index()
        fig1 = px.pie(df_stock_volumen, values='Volumen', names='Grupo', title='Distribución de Volumen por Grupo')
        fig1.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
        fig1.update_layout(title_x=0.2)
        st.plotly_chart(fig1, use_container_width=True)

    # --- GRÁFICO 2: PIE CHART POR ANTIGÜEDAD (PLOTLY) ---
    with col2:
        df_agrupado_pie = df_stock_completo.groupby('Rango_Antiguedad')['Volumen'].sum().reset_index()
        fig2 = px.pie(df_agrupado_pie, values='Volumen', names='Rango_Antiguedad', title='Distribución de Volumen por Rango de Antigüedad')
        fig2.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5))
        fig2.update_layout(title_x=0.1)
        st.plotly_chart(fig2, use_container_width=True)

    # --- GRÁFICO 3: HEATMAP (PLOTLY) ---
    with col3:
        df_agrupado_hm = df_stock_completo.groupby(['Producto', 'Rango_Antiguedad'])['Volumen'].sum().reset_index()
        matriz_volumen = df_agrupado_hm.pivot_table(index='Producto', columns='Rango_Antiguedad', values='Volumen', fill_value=0)
        orden_columnas = ['0-15 dias', '16-30 dias', '31-60 dias', '61-90 dias', '90 dias o mas']
        matriz_volumen = matriz_volumen.reindex(columns=orden_columnas, fill_value=0)
        fig3 = px.imshow(matriz_volumen, x=matriz_volumen.columns, y=matriz_volumen.index, labels={'x':'Rango de Antigüedad', 'y':'Producto', 'color':'Volumen'}, title='Mapa de Calor de Antigüedad', color_continuous_scale='Reds', text_auto=".0f", width=600, height=600)
        fig3.update_layout(title_x=0.3)
        fig3.update_traces(textfont_size=15)
        fig3.update_xaxes(tickangle=45)
        st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("La columna 'Fecha_Recepcion' no se encontró en el archivo 'STOCK.xlsx'. Los gráficos de antigüedad no se mostrarán.")
