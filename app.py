import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
#from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode


def add_custom_logo():
    st.markdown(
        """
        <style>
        [data-testid="stHeader"] {
            background-image: url("https://www.svti.cl/img/logo-svti-footer.png");
            background-repeat: no-repeat;
            background-position: 02% 50%; /* Adjust for top-right placement */
            background-size: 70px; /* Adjust logo size */
            padding-top: 10px; /* Adjust as needed for spacing */
            padding-left: 10px; /* Adjust for spacing */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
add_custom_logo()


# --- Configuración de la página ---
st.set_page_config(
    page_title="Dashboard de Gestión de Stock",
    layout="wide",
    initial_sidebar_state="expanded"
)

#st.image(image_url, caption="My Image", width=400) 
#image_url = "https://www.svti.cl/img/logo-svti.png" 
pd.set_option('display.max_colwidth', None) # Muestra el contenido completo de la columna
pd.set_option('display.width', None)       # Ajusta el ancho de la consola para permitir el salto
# Display the image using st.image()
#st.image(image_url, caption="My Image from URL", use_column_width=True) 

#st.header("📊 Dashboard de Gestión de Stock por Grupo")

#st.markdown("---")

# --- Carga y preparación de datos ---
try:
GITHUB_BASE = "https://github.com/LuxoF84/SVE/blob/main/"

try:
    df_resumen = pd.read_excel(GITHUB_BASE + "estadias.xlsx")
except Exception as e:
    st.error(f"No se pudo cargar el archivo desde GitHub: {e}")
    st.stop()
    
    df_stock_completo = pd.read_excel(GITHUB_BASE + "STOCK.xlsx")
except FileNotFoundError:
    st.error("Error: No se encontraron los archivos 'estadias.xlsx' o 'STOCK.xlsx'. Por favor, verifica la ruta.")
    st.stop()

df_stock_completo = df_stock_completo[
    (df_stock_completo['Cliente'].str.strip() == 'ARAUCO') &
    (df_stock_completo['Grupo'].str.strip() != 'CELULOSA')
]

columnas_numericas_resumen = ['Vol. Stock', 'Capacidad m3', 'vol_prgvig', 'vol_sinprg', 'stk_dead', '% Utilizacion', 'vol_sinprginc']
for col in columnas_numericas_resumen:
    if col in df_resumen.columns:
        df_resumen[col] = pd.to_numeric(df_resumen[col], errors='coerce').fillna(0)

# --- 1. Tarjetas de Métricas (en la parte superior) ---
#st.header("Volumen Total en Stock por Grupo")
#st.write("Mostrando datos de la tabla de resumen 'estadias'")

#cols_metric = st.columns(4)
#grupos = df_resumen['Grupo'].unique()

#for idx, grupo in enumerate(grupos):
#    with cols_metric[idx]:
#        vol_stock = df_resumen[df_resumen['Grupo'] == grupo]['Vol. Stock'].iloc[0] if grupo in df_resumen['Grupo'].values else 0
#        st.metric(label=f"Grupo {grupo}", value=f"{vol_stock:.2f} m³")

#st.markdown("---")

# --- 2. Gráficos de Velocímetro (Gauges) ---
#st.header("Utilización de Capacidad por Grupo")

#st.header("Utilización de Capacidad por Grupo")

# Configura la página (opcional, pero se recomienda al inicio)
st.set_page_config(page_title="Mi Aplicación con Logo", layout="wide")

# Agrega el logo a la barra lateral (esquina superior izquierda)
st.logo("https://www.svti.cl/img/logo-svti.png", icon_image="https://www.svti.cl/img/logo-svti.png", size="large")

st.markdown("<h2 style='text-align: center;'>Utilización de Capacidad por Grupo</h2>", unsafe_allow_html=True)


df_resumen = df_resumen.drop(df_resumen.index[-1])

grupos = df_resumen['Grupo'].unique()

num_grupos = len(grupos)

# Crear columnas con espacios entre ellas
if num_grupos == 2:
    cols_gauges = st.columns([2, 2, 2])  # 2 gauges con espacio
    gauge_positions = [0, 2]
elif num_grupos == 3:
    cols_gauges = st.columns([1, 0.3, 1, 0.3, 1])  # 3 gauges con espacios
    gauge_positions = [0, 2, 4]
elif num_grupos == 4:
    cols_gauges = st.columns([1, 1, 1, 1, 1, 1, 1])  # 4 gauges con espacios
    gauge_positions = [0, 2, 4, 6]
else:
    # Para más de 4 grupos, usar el método original
    cols_gauges = st.columns(num_grupos)
    gauge_positions = list(range(num_grupos))

gauge_idx = 0
for idx, row in df_resumen.iterrows():
    vol_stock = row['Vol. Stock']
    capacidad_max = row['Capacidad m3']
    grupo_name = row['Grupo']
    
    # Excluir 'nan'
    if pd.isna(grupo_name):
        continue
    
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=vol_stock,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{grupo_name}",
               'font': {'size': 20}},
        number={
            'valueformat': ".0f",
            'font': {'size': 28},
            'suffix': ' m³'
        },
        gauge={
            'axis': {
                'range': [0, capacidad_max],
                'tickfont': {'size': 14}
            },
            'bar': {'color': "blue"},
            'steps': [
                #{'range': [0, capacidad_max * 0.5], 'color': "white"},
                {'range': [capacidad_max * 0.8, capacidad_max * 1], 'color': "red"}
            ],
            #'threshold': {
            #    'line': {'color': "red", 'width': 4},
            #    'thickness': 0.75,
            #    'value': capacidad_max * 0.9
            }
        
    ))

    fig_gauge.update_layout(height=300, width=300)

    # Muestra los valores 0 y Máximo debajo del gauge
    gauge_vals_cols = st.columns(2)
   # with gauge_vals_cols[0]:
   #     st.markdown('<p style="text-align: left;">0</p>', unsafe_allow_html=True)
   # with gauge_vals_cols[1]:
   #     st.markdown(f'<p style="text-align: right;">{capacidad_max}</p>', unsafe_allow_html=True)

    # Usar las posiciones calculadas para colocar los gauges con espaciado
    with cols_gauges[gauge_positions[gauge_idx]]:
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    gauge_idx += 1


#st.markdown("---")

# --- 3. Matriz (Tabla) ---
#st.header("Detalle Completo del Stock")
pd.set_option('display.max_colwidth', None) # Muestra el contenido completo de la columna
pd.set_option('display.width', None)       # Ajusta el ancho de la consola para permitir el salto

if 'Fecha' in df_resumen.columns:
    df_resumen['Fecha'] = pd.to_datetime(df_resumen['Fecha'], errors='coerce').dt.date

df_resumen = df_resumen.reset_index(drop=True)

formatos = {
    'Vol. Stock': '{:.3f}',
    'Holgura m3': '{:.3f}',
    'vol_prgvig': '{:.3f}',
    'vol_sinprg': '{:.3f}',
    'Stock Piedra': '{:.3f}',
    'Volumen Consolidable Con Programa': '{:.3f}',
    'Volumen Consolidable Sin Programa': '{:.2f}',
    'Volumen E. Incompletas Sin Programa': '{:.3f}',
    'Vol. Cons. s/Prog.': '{:.2f}',
    'Vol.Ent.Inc.s/Prog.': '{:.3f}',
    '% Utilizacion': '{:.1f}',
    '% Vol. Stock Piedra': '{:.1f}',
    '%V.StkPiedra': '{:.0f}'
}

formatos_existentes = {col: fmt for col, fmt in formatos.items() if col in df_resumen.columns}

estilo_tabla = df_resumen.style.format(formatos_existentes).set_properties(
    **{
        'font-size': '16px',
        'text-align': 'center'  # <--- Esta línea centra el contenido de la tabla
    }
)

st.dataframe(estilo_tabla, use_container_width=False,
             column_config={
         "Capacidad m3": st.column_config.Column(
            label="Cap.m3",
            width=60, # <-- ANCHO FIJO en píxeles
            help="Capacidad por producto en m3"
        ),
         "% Utilizacion": st.column_config.Column(
            label="% Uso",
            width=50, # <-- ANCHO FIJO en píxeles
            help="% de utilizacion de la capacidad"
        ),
       
         "Holgura Camiones": st.column_config.Column(
            label="Holg.Cam",
            width=70, # <-- ANCHO FIJO en píxeles
            help="Holgura de cantidad de camiones."
        ),
        
        "Holgura m3": st.column_config.Column(
            label="Holg.m3",
            width=70, # <-- ANCHO FIJO en píxeles
            help="Holgura del stock en metros cúbicos."
        ),
        "Volumen Consolidable Con Programa": st.column_config.Column(
            label="Vol.Cble. c/Prog.",
            width=100, # <-- ANCHO FIJO para esta columna
            help="Volumen total de stock consolidable con un programa de producción vigente."
        ),
        "Volumen Consolidable Sin Programa": st.column_config.Column(
            label="Vol. Cons. s/Prog.",
            width=100, # <-- ANCHO FIJO para esta columna
            help="Volumen total de stock consolidable sin un programa de producción vigente."
        ),
         "Volumen E. Incompletas Sin Programa": st.column_config.Column(
            label="Vol.Ent.Inc.s/Prog.",
            width=100, # <-- ANCHO FIJO para esta columna
            help="Volumen de entregas Incompletas y Sin Programa."
        ),
         "% Vol. Stock Piedra": st.column_config.Column(
            label="%V.StkPiedra",
            width=100, # <-- ANCHO FIJO para esta columna
            help="Porcentaje Volumen de stock piedra, sin rotacion."
         ),
         "CT Consolidables": st.column_config.Column(
            label="CT.Cble",
            width=50, # <-- ANCHO FIJO para esta columna
            help="Contenedores Consolidables"
        ),
         "CT Consolidables Sin Programa": st.column_config.Column(
            label="CT.Cble/SP",
            width=75, # <-- ANCHO FIJO para esta columna
            help="Contenedores Consolidables Sin Programa vigente"
        ),
         "CT sin programa, incompletas": st.column_config.Column(
            label="CT,S/P,Inc.",
            width=75, # <-- ANCHO FIJO para esta columna
            help="Cantidad de contenedores sin programa con carga incompleta"
        ),
         "Equivalente a CT con stock Piedra": st.column_config.Column(
            label="CT/Stk Piedra",
            width=75, # <-- ANCHO FIJO para esta columna
            help="Equivalencia a CT del stock piedra"
        )
    }
)

st.markdown("---")

# --- 4. Gráficos en el centro (Pie y Bar) ---
col_pie, col_bar = st.columns(2)

with col_pie:
    #st.subheader("% de Utilización por Grupo")
    st.markdown("<h3 style='text-align: center;'>% de Utilización por Grupo'</h1>", unsafe_allow_html=True)
    fig_pie = px.pie(
        df_resumen,
        values='% Utilizacion',
        names='Grupo',
        #title='Porcentaje de Utilización por Grupo'
    )
    
    fig_pie.update_layout(
            legend=dict(
            orientation="h",  # Horizontal
            yanchor="top",    # Ancla superior de la leyenda
            y=-0.1,          # Posición vertical (negativa para colocar debajo)
            xanchor="center", # Centrar horizontalmente
            x=0.5            # Posición horizontal centrada
        ))


    st.plotly_chart(fig_pie, use_container_width=True)

with col_bar:
    #st.subheader("Volumen por Tipo de Programa")
    st.markdown("<h3 style='text-align: center;'>Volumen por Tipo de Programa</h1>", unsafe_allow_html=True)
    
    df_bar = df_resumen.melt(id_vars='Grupo', value_vars=['Volumen Consolidable Con Programa', 'Volumen Consolidable Sin Programa', 'Volumen E. Incompletas Sin Programa', 'Stock Piedra'],
                             var_name='Tipo de Volumen', value_name='Volumen')
    
    fig_bar = px.bar(
        df_bar,
        x='Grupo',
        y='Volumen',
        color='Tipo de Volumen',
        barmode='group',
        #title='Volumen por Grupo y Tipo'
    )
    fig_bar.update_layout(
            legend=dict(
            orientation="h",  # Horizontal
            yanchor="top",    # Ancla superior de la leyenda
            y=-0.1,          # Posición vertical (negativa para colocar debajo)
            xanchor="center", # Centrar horizontalmente
            x=0.5            # Posición horizontal centrada
        ))

    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# --- 5. Gráficos Adicionales (de la tabla de STOCK completa) ---
#st.header("Análisis de Volumen de Stock Completo")
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
        #st.subheader("Volumen por Grupo")
        df_stock_volumen = df_stock_completo.dropna(subset=['Volumen']).groupby('Grupo')['Volumen'].sum().reset_index()
        
        fig1 = px.pie(
            df_stock_volumen,
            values='Volumen',
            names='Grupo',
            title='Distribución de Volumen por Grupo',
            
        )
        
        fig1.update_layout(
            legend=dict(
            orientation="h",  # Horizontal
            yanchor="top",    # Ancla superior de la leyenda
            y=-0.1,          # Posición vertical (negativa para colocar debajo)
            xanchor="center", # Centrar horizontalmente
            x=0.5,            # Posición horizontal centrada
                                
        ))
        
        # Centra el título usando update_layout()
        fig1.update_layout(
        title_x=0.2
)

        st.plotly_chart(fig1, use_container_width=True)

    # --- GRÁFICO 2: PIE CHART POR ANTIGÜEDAD (PLOTLY) ---
    with col2:
        #st.subheader("Volumen por Antigüedad")
        df_agrupado_pie = df_stock_completo.groupby('Rango_Antiguedad')['Volumen'].sum().reset_index()
        
        fig2 = px.pie(
            df_agrupado_pie,
            values='Volumen',
            names='Rango_Antiguedad',
            title='Distribución de Volumen por Rango de Antigüedad'
        )
        
        # Configurar la leyenda en la parte inferior
        fig2.update_layout(
            legend=dict(
            orientation="h",  # Horizontal
            yanchor="top",    # Ancla superior de la leyenda
            y=-0.1,          # Posición vertical (negativa para colocar debajo)
            xanchor="center", # Centrar horizontalmente
            x=0.5            # Posición horizontal centrada
        )
    )
        fig2.update_layout(
        title_x=0.1
)

        st.plotly_chart(fig2, use_container_width=True)

    # --- GRÁFICO 3: HEATMAP (PLOTLY) ---
    with col3:
        #st.subheader("Mapa de Calor de Antigüedad")
        df_agrupado_hm = df_stock_completo.groupby(['Producto', 'Rango_Antiguedad'])['Volumen'].sum().reset_index()
        matriz_volumen = df_agrupado_hm.pivot_table(index='Producto', columns='Rango_Antiguedad', values='Volumen', fill_value=0)
        orden_columnas = ['0-15 dias', '16-30 dias', '31-60 dias', '61-90 dias', '90 dias o mas']
        matriz_volumen = matriz_volumen.reindex(columns=orden_columnas, fill_value=0)

        fig3 = px.imshow(
            matriz_volumen,
            x=matriz_volumen.columns,
            y=matriz_volumen.index,
            labels={'x':'Rango de Antigüedad', 'y':'Producto', 'color':'Volumen'},
            title='Mapa de Calor de Antigüedad',
            color_continuous_scale='Reds',
            text_auto=".0f",                  # <-- NUEVO: Muestra el valor en la celda
            width=600,                       # <-- NUEVO: Ancho para celdas más grandes
            height=600                       # <-- NUEVO: Altura para celdas más grandes
        )
        fig3.update_layout(
        title_x=0.3
)
        fig3.update_traces(textfont_size=15)
        fig3.update_xaxes(tickangle=45)
        st.plotly_chart(fig3, use_container_width=True)
   
else:
    st.warning("La columna 'Fecha_Recepcion' no se encontró en el archivo 'STOCK.xlsx'. Los gráficos de antigüedad no se mostrarán.")

############################################################################### TABLA DINAMICA #####################

import streamlit as st
import polars as pl
import time

# -------------------------------------------------------------------------
# GLOBAL: Definición del mapa de renombre de columnas
# -------------------------------------------------------------------------
COLUMN_RENAMES = {
    'Sobrepeso': 'SP',
    'volprg': 'VP',
    'vollote_sum': 'VR',
    'diff_vol': 'SV',
    # 'diff_lote' se renombra a 'SL' (Saldo Lote) para evitar colisión con 'SP'
    'diff_lote': 'SL', 
    'pqtsprg': 'PP',
    'loteof_count': 'PR',
    'Box Prog.': 'CT',
    'Box Consol.': 'CC',
    'Box Saldo': 'Sld CT'
}

# Configuración de Streamlit para usar la versión moderna de caché
@st.cache_data(show_spinner=False)
def load_data():
    """Carga los datos del archivo 'merged.xlsx' y aplica renombre defensivo."""
    start_time = time.time()
    if 'loading_data' not in st.session_state:
        st.session_state.loading_data = False
        
    st.session_state.loading_data = True
    
    with st.spinner(f"⏳ Cargando datos desde merged.xlsx..."):
       
        try:
            df = pl.read_excel(GITHUB_BASE + "merged.xlsx")
        except Exception:
            df = pl.from_pandas(pd.read_excel("merged.xlsx", engine="openpyxl"))
            
    # -------------------------------------------------------------------------
    # INICIO: Manejo de Conflicto de Columna Duplicada ('CT') - Eliminación
    # -------------------------------------------------------------------------
    target_name = 'CT'
    source_name = 'Box Prog.'
    
    # Si la columna que deseamos usar ('CT') ya existe en el original, la eliminamos.
    if target_name in df.columns and source_name in df.columns and COLUMN_RENAMES.get(source_name) == target_name:
        df = df.drop(target_name)
        st.sidebar.info(
            f"✅ **Columna Eliminada:** La columna original **'{target_name}'** que generaba conflicto fue eliminada "
            f"para permitir que **'{source_name}'** se renombre a **'{target_name}'**."
        )

    # Aplicar el renombre solicitado por el usuario.
    df = df.rename(COLUMN_RENAMES)
    
    end_time = time.time()
    st.session_state.loading_data = False
    st.sidebar.success(f"✅ Datos cargados en {end_time - start_time:.2f} segundos.")
    return df

# === Función de Estilo para Subtotales ===
def highlight_subtotals(row):
    """Aplica estilo de negrita y fondo verde claro a las filas de 'Subtotal'."""
    # Nota: No se cambia la alineación aquí para que respete el estilo global centrado.
    style = 'background-color: rgba(144, 238, 144, 0.2); font-weight: bold; text-align: center;'
    
    if 'feta' in row and row['feta'] == 'Subtotal':
        return [style] * len(row)
    else:
        return [''] * len(row)

# === Función de Estilo para Negativos (Fuente Roja) ===
def highlight_negatives(val, columns_to_check):
    """Aplica fuente roja si el valor es negativo en las columnas especificadas."""
    
    styles = [''] * len(val)
    
    for col_name in columns_to_check:
        try:
            col_index = val.index.get_loc(col_name) 
            cell_value = val.iloc[col_index]
            
            if isinstance(cell_value, (int, float)) and cell_value < 0:
                # Se añade text-align: center para evitar que el estilo de color rompa la alineación global
                styles[col_index] = 'color: red; text-align: center;' 
        except KeyError:
            continue
            
    return styles

# === Función de Estilo para SP > 0 (Fuente Roja y Negrita) ===
def highlight_sp_positive(s):
    """Aplica fuente roja y negrita si el valor en SP es positivo y > 0."""
    
    styles = []
    style_positive = 'color: red; font-weight: bold; text-align: center;'
    style_default = 'text-align: center;' # Mantiene el centrado global

    for val in s:
        try:
            # Aseguramos que solo aplicamos estilo si es un número y es mayor a cero
            v = float(val)
            if v > 0:
                styles.append(style_positive)
            else:
                styles.append(style_default)
        except (ValueError, TypeError):
             # Para valores no numéricos (cadenas, NaN, None)
             styles.append(style_default) 
            
    return styles


# === Función de Estilo para NAVIERA (Fondo, Color y Centrado) ===
def highlight_naviera(s):
    """Aplica color de fondo, color de fuente, negrita y centrado a la columna NAVIERA."""
    
    styles_map = {
        'MSC': ('#EED484', 'black'),
        'MAERSK': ('#42B0D5', 'white'),
        'ONE': ('#BD1874', 'white'),
        'HAPAG LLOYD': ('#FE6B00', 'black')
    }
    
    css_list = []
    
    for val in s:
        bg_color, text_color = styles_map.get(val, ('', ''))
        # Se mantiene 'text-align: center;' para asegurar que sobrescriba el estilo global si fuera necesario.
        css = 'text-align: center;'
        
        if bg_color:
            css += f'; background-color: {bg_color}; color: {text_color}; font-weight: bold;'
            
        css_list.append(css)
        
    return css_list

# === Función: Estilo condicional para 'MN-par' ===
def highlight_mn_par(s):
    """Aplica fondo amarillo con texto rojo y negrita si el valor no es 'Ok'."""
    style_fail = 'background-color: yellow; color: red; font-weight: bold; text-align: center;'
    style_ok = 'text-align: center;'
    
    css_list = []
    
    for val in s:
        val_str = str(val).strip().upper()
        if val_str != 'OK' and val_str != '':
            css_list.append(style_fail)
        else:
            css_list.append(style_ok)
            
    return css_list
    
# === Función: Escala de color para '%' ===
def color_scale_percentage_manual(s):
    """Aplica una escala de colores de fondo para la columna '%'."""
    styles = []
    
    for val in s:
        if val == '' or pd.isna(val):
            styles.append('text-align: center;')
            continue
            
        try:
            v = float(val)
        except (ValueError, TypeError):
             styles.append('text-align: center;')
             continue

        v_clamped = max(0.0, min(v, 1.0))
        factor = v_clamped 
        
        if v <= 0:
            color_str = f'background-color: rgba(255, 0, 0, 0.2);'
        elif v >= 1:
            color_str = f'background-color: white;'
        else:
            # Interpolación lineal de 0% (R,0,0,0.2) a 100% (R,G,B,1.0)
            R = 255
            G = int(0 + factor * 255)
            B = int(0 + factor * 255)
            A = 0.2 + factor * 0.8
            
            color_str = f'background-color: rgba({R}, {G}, {B}, {A:.3f});'
            
        # Aseguramos el centrado
        styles.append(color_str + 'text-align: center;')
        
    return styles


st.title("📊 Tabla Dinámica Interactiva con Subtotales por MN")

# === Cargar datos y manejar el estado ===
df = load_data()

# === Filtros ===
grupos = sorted(df["Grupo"].drop_nulls().unique().to_list()) if "Grupo" in df.columns else []
clientes = sorted(df["Cliente"].drop_nulls().unique().to_list()) if "Cliente" in df.columns else []
programas = sorted(df["Programa"].drop_nulls().unique().to_list()) if "Programa" in df.columns else []
estados = sorted(df["Estado"].drop_nulls().unique().to_list()) if "Estado" in df.columns else []
mns = sorted(df["MN"].drop_nulls().unique().to_list()) if "MN" in df.columns else []

with st.sidebar:
    st.header("Opciones y Filtros")

    st.markdown("---")
    st.subheader("Control de Datos")
    if st.button("🔄 Forzar Recarga de 'merged.xlsx'"):
        st.cache_data.clear()
        st.rerun() 
    st.markdown("---")
    
    filtro_grupo = st.multiselect("Grupo", grupos, default=[g for g in grupos if g != "OTROS"])
    filtro_cliente = st.multiselect("Cliente", clientes, default=["ARAUCO"] if "ARAUCO" in clientes else [])
    filtro_programa = st.multiselect("Programa", programas, default=["Vigente"] if "Vigente" in programas else [])
    filtro_estado = st.multiselect("Estado", estados, default=["Saldo"] if "Saldo" in estados else [])
    filtro_mn = st.multiselect("MN", mns)

filtros = []
if filtro_grupo:
    filtros.append(pl.col("Grupo").is_in(filtro_grupo))
if filtro_cliente: filtros.append(pl.col("Cliente").is_in(filtro_cliente))
if filtro_programa: filtros.append(pl.col("Programa").is_in(filtro_programa))
if filtro_estado: filtros.append(pl.col("Estado").is_in(filtro_estado))
if filtro_mn: filtros.append(pl.col("MN").is_in(filtro_mn))

df_filtrado = df.filter(pl.all_horizontal(filtros)) if filtros else df.clone()
st.write(f"🔹 **Registros filtrados:** {df_filtrado.height:,}")

# --- INICIO: Creación de la clave de fecha para ordenamiento cronológico ---
if "feta" in df_filtrado.columns:
    # Asume formato DD/MM/YYYY. strict=False permite NULLs si la conversión falla.
    df_filtrado = df_filtrado.with_columns(
        pl.col("feta").str.to_date("%d/%m/%Y", strict=False).alias("_feta_date_key")
    )
# --- FIN: Creación de la clave de fecha ---


# === Columnas ===
# Listas de columnas actualizadas con los nuevos nombres
columnas_filas_default = [
    "feta", "MN", "Stacking", "Puerto Final", "Producto_norm",
    "GrupoEntr", "entrega", "MN-par", "NAVIERA", "%",
    "obs", "factor", "SP", "Δ ETA UltRecp (dias)", "Δ Recep (dias)"
]

columnas_valores_default = [
    "VP", "VR", "SV", "SL", 
    "PP", "PR", "diff_pqt", 
    "CT", "CC", "Sld CT"
]

# -------------------------------------------------------------------------
# Se eliminan las referencias a 'CT_Existente_Duplicado' ya que se eliminó en load_data
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# Asegurar que no haya solapamiento entre columnas de filas y valores
# -------------------------------------------------------------------------

cols_exist = set(df_filtrado.columns)
cols_exist_valores = [c for c in columnas_valores_default if c in cols_exist and c not in columnas_filas_default]
cols_exist_filas = [c for c in columnas_filas_default if c in cols_exist and c not in columnas_valores_default] 

# === Tabla dinámica (Group By) ===
if not cols_exist_filas or not cols_exist_valores:
    st.warning("No hay suficientes columnas de agrupación o de valor para crear la tabla dinámica con los filtros actuales.")
    pivot = pl.DataFrame()
else:
    # Lógica de agrupación y subtotales
    pivot = (
        df_filtrado
        .group_by(cols_exist_filas)
        .agg([
            # Incluir la clave de fecha para la ordenación
            pl.col("_feta_date_key").first().alias("_feta_date_key") if "_feta_date_key" in df_filtrado.columns else pl.lit(None),
            *[pl.col(c).sum().alias(c) for c in cols_exist_valores]
        ])
        .with_columns(pl.lit(0).alias("_is_subtotal_order"))
    )

    if "MN" in pivot.columns:
        subtotales = (
            pivot
            .group_by("MN")
            .agg([pl.col(c).sum().alias(c) for c in cols_exist_valores])
            .with_columns([
                pl.lit("Subtotal").alias("feta"), 
                pl.lit(1).alias("_is_subtotal_order"), 
                # Establecer la clave de fecha a NULL para que se ordene al final del grupo MN
                pl.lit(None).cast(pl.Date).alias("_feta_date_key") if "_feta_date_key" in pivot.columns else pl.lit(None),
            ])
        )

        cols_to_fill_with_none = [c for c in cols_exist_filas if c not in subtotales.columns]
        for c in cols_to_fill_with_none:
            subtotales = subtotales.with_columns(pl.lit(None).cast(pivot[c].dtype).alias(c))

        pivot = pl.concat([
            pivot, 
            subtotales.select(pivot.columns) 
        ], how="diagonal")

# === Ordenar ===
if not pivot.is_empty() and "_is_subtotal_order" in pivot.columns and "_feta_date_key" in pivot.columns:
    # Ordenar por MN, luego por el orden Subtotal (detalle primero), y finalmente por la clave de fecha
    sort_keys = ["MN", "_is_subtotal_order", "_feta_date_key"]
    sort_order = [c for c in sort_keys if c in pivot.columns] 
    
    # Agregar las demás columnas de agrupación para un orden secundario
    for c in cols_exist_filas:
        # Usar las columnas de fila originales, excepto 'feta' que ya se ordena con la clave de fecha
        if c not in sort_order and c != 'feta': 
            sort_order.append(c)

    try:
        pivot = pivot.sort(by=sort_order)
    except Exception as e:
        st.warning(f"Error al ordenar para subtotales intercalados: {e}. Se omitirá el orden.")
        
    pivot = pivot.drop("_is_subtotal_order")
elif not pivot.is_empty() and "_feta_date_key" in pivot.columns:
    # Ordenar solo por la clave de fecha, y luego por el resto de columnas de fila
    orden_cols = ["_feta_date_key", "MN", "Stacking", "Puerto Final", "Producto_norm", "GrupoEntr", "entrega"]
    orden_existentes = [c for c in orden_cols if c in pivot.columns]
    try:
        pivot = pivot.sort(by=orden_existentes)
    except Exception as e:
        st.warning(f"Error al ordenar sin subtotales: {e}")
elif not pivot.is_empty():
    orden_cols = ["feta", "MN", "Stacking", "Puerto Final", "Producto_norm", "GrupoEntr", "entrega"]
    orden_existentes = [c for c in orden_cols if c in pivot.columns]
    try:
        pivot = pivot.sort(by=orden_existentes)
    except Exception as e:
        st.warning(f"Error al ordenar sin clave de fecha: {e}")


# === Mostrar con Estilo y Formato ===
if not pivot.is_empty():
    
    # Eliminar la clave de fecha temporal antes de convertir a Pandas
    if "_feta_date_key" in pivot.columns:
        pivot = pivot.drop("_feta_date_key")
        
    df_to_display = pivot.to_pandas()
    
    # -------------------------------------------------------------------------
    # Aplicar orden final de columnas (CT, CC, Sld CT deben ir después de SP)
    # -------------------------------------------------------------------------
    all_cols = list(df_to_display.columns)
    cols_to_move = ['CT', 'CC', 'Sld CT']
    
    # Se eliminaron las referencias a 'CT_Existente_Duplicado'
    fixed_cols = [col for col in all_cols if col not in cols_to_move]
    
    final_display_order = all_cols # Fallback
    try:
        sp_index = fixed_cols.index('SP')
        final_display_order = fixed_cols[:sp_index + 1] + [c for c in cols_to_move if c in all_cols] + fixed_cols[sp_index + 1:]
    except ValueError:
        final_display_order = all_cols
        
    df_to_display = df_to_display.reindex(columns=final_display_order)

    
    # Limpieza de NaN/None en columnas de fila
    cols_to_blank = [c for c in cols_exist_filas if c not in ["MN", "feta"] and c in df_to_display.columns]
    
    if cols_to_blank:
        for col in cols_to_blank:
            df_to_display[col] = df_to_display[col].astype('object').fillna('')

    # --- Custom Formatters ---
    def format_zero_decimal(val):
        if val == '': return ''
        try: return '{:.0f}'.format(float(val))
        except (ValueError, TypeError): return str(val)
            
    def format_comma_zero_decimal(val):
        if val == '': return ''
        try: return '{:,.0f}'.format(float(val))
        except (ValueError, TypeError): return str(val)
            
    def format_comma_three_decimal(val):
        if val == '': return ''
        try: return '{:,.3f}'.format(float(val))
        except (ValueError, TypeError): return str(val)
            
    def format_percentage(val):
        if val == '': return ''
        try: return '{:.0%}'.format(float(val))
        except (ValueError, TypeError): return str(val)
    
    # REFUERZO: Columnas de formato
    key_cols_no_separator = ['GrupoEntr', 'entrega']
    integer_value_cols = [
        'factor', 'SP', 'Δ ETA UltRecp (dias)', 'Δ Recep (dias)', 
        'PR', 'diff_pqt', 'CT', 'CC', 'Sld CT', 'SL', 'PP'
    ]
    decimal_cols = ["VP", "VR", "SV"]
    # REFUERZO: Columnas que deben tener fuente roja si son negativas
    negative_red_cols = ['diff_pqt', 'SV', 'Sld CT', 'SL', 'PP']

    # Se eliminó la referencia a 'CT_Existente_Duplicado'
    format_dict = {}
    
    # A. Columnas de IDENTIFICADOR 
    for col in key_cols_no_separator:
        if col in df_to_display.columns: format_dict[col] = format_zero_decimal 

    # B. Columna de PORCENTAJE
    if '%' in df_to_display.columns: format_dict['%'] = format_percentage
        
    # C. Columnas de VALOR ENTERO (Fila)
    numeric_row_cols_int = [c for c in integer_value_cols if c in cols_exist_filas and c not in format_dict and c in df_to_display.columns]
    for col in numeric_row_cols_int: format_dict[col] = format_comma_zero_decimal

    # D. Columnas de VALOR DECIMAL (Fila)
    numeric_row_cols_dec = [c for c in decimal_cols if c in cols_exist_filas and c not in format_dict and c in df_to_display.columns]
    for col in numeric_row_cols_dec: format_dict[col] = format_comma_three_decimal

    # E. Columnas de VALOR AGREGADO (Entero/Decimal)
    value_cols_int = [c for c in integer_value_cols if c in df_to_display.columns and c not in cols_exist_filas]
    for col in value_cols_int: format_dict[col] = '{:,.0f}'

    value_cols_decimal = [c for c in decimal_cols if c in df_to_display.columns and c not in cols_exist_filas]
    for col in value_cols_decimal: format_dict[col] = '{:,.3f}'
            
    # F. Columnas de STRING/OBJETO
    for col in cols_exist_filas:
        if col not in format_dict and col in df_to_display.columns: format_dict[col] = '{}'
    
    styled_df = df_to_display.style
    
    # 5. Aplicar alineación centrada a todas las celdas (la aplicación más robusta)
    styled_df = styled_df.set_properties(
        subset=df_to_display.columns,
        **{'text-align': 'center'}
    )

    # 6. Aplicar los formatos
    styled_df = styled_df.format(format_dict, na_rep='')
    
    # 7. Aplicar el estilo condicional para SP > 0 (Fuente roja y negrita)
    if 'SP' in df_to_display.columns: 
        styled_df = styled_df.apply(highlight_sp_positive, axis=0, subset=['SP'])

    # 8. Aplicar el estilo condicional para subtotales 
    if 'feta' in df_to_display.columns: styled_df = styled_df.apply(highlight_subtotals, axis=1)
        
    # 9. Aplicar el estilo condicional para 'MN-par'
    if 'MN-par' in df_to_display.columns: styled_df = styled_df.apply(highlight_mn_par, axis=0, subset=['MN-par'])
        
    # 10. Aplicar la escala de color para '%'
    if '%' in df_to_display.columns: styled_df = styled_df.apply(color_scale_percentage_manual, axis=0, subset=['%'])
    
    # 11. Aplicar el estilo condicional para negativos
    styled_df = styled_df.apply(
        lambda x: highlight_negatives(x, negative_red_cols), 
        axis=1, 
        subset=[col for col in negative_red_cols if col in df_to_display.columns]
    )
    
    # 12. Aplicar el estilo condicional para NAVIERA
    if 'NAVIERA' in df_to_display.columns: styled_df = styled_df.apply(highlight_naviera, axis=0, subset=['NAVIERA'])
        
    st.dataframe(styled_df, use_container_width=True)
else:
    st.dataframe(pivot.to_pandas(), use_container_width=True)


# === Exportar ===
if not pivot.is_empty():
    # Se eliminó la lógica para eliminar la columna temporal antes de exportar
    output_path = "pivot_polars_subtotales.xlsx"
    # Antes de exportar, hay que asegurarse de que la columna temporal _feta_date_key no esté presente
    if "_feta_date_key" in pivot.columns:
        pivot = pivot.drop("_feta_date_key")
        
    pivot.write_excel(output_path, autofit=True)

    with open(output_path, "rb") as file:
        st.download_button(
            "💾 Descargar tabla dinámica con subtotales (Excel)",
            file,
            file_name="pivot_polars_subtotales.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

###################################################------------------------------ANALISIS ESTADIAS---------------#################################


# ===========================================
# CONFIGURACIÓN INICIAL
# ===========================================
st.markdown("Dashboard de análisis de capacidad, stock y consolidación por **fecha** y **grupo**.")

# ===========================================
# CARGA DE DATOS DESDE LA MISMA CARPETA
# ===========================================
dfestadias = pl.read_excel(GITHUB_BASE + "status maderas.xlsx")



# Leer Excel con Polars
dfestadias = pl.read_excel(file_name)

# Limpieza de nombres de columnas
dfestadias = dfestadias.rename({c: c.strip() for c in dfestadias.columns})


# ===========================================
# CONVERSIÓN SEGURA DE FECHAS
# ===========================================
if "Fecha" in dfestadias.columns:
    dtype_fecha = dfestadias["Fecha"].dtype

    # Solo convertir si no es ya Date o Datetime
    if dtype_fecha not in [pl.Date, pl.Datetime]:
        try:
            dfestadias = dfestadias.with_columns(
                pl.col("Fecha").str.strptime(pl.Date, strict=False).alias("Fecha")
            )
        except Exception:
            # fallback si los valores no son texto
            dfestadias = dfestadias.with_columns(
                pl.col("Fecha").cast(pl.Date, strict=False)
            )


# ===========================================
# FILTROS
# ===========================================
if "Grupo" in dfestadias.columns and "Fecha" in dfestadias.columns:
    # --- Filtro por grupo ---
    grupos = dfestadias["Grupo"].drop_nans().unique().to_list()
    grupo_sel = st.multiselect("Seleccionar Grupo(s):", grupos, default=grupos)
    dfestadias = dfestadias.filter(pl.col("Grupo").is_in(grupo_sel))

    # --- Filtro por fecha (slider) ---
    fechas = dfestadias["Fecha"].to_pandas()

    # Asegurar que la columna sea datetime y convertir a date
    fechas = pd.to_datetime(fechas).dt.date
    fecha_min, fecha_max = fechas.min(), fechas.max()

    # Slider para elegir rango de fechas
    rango_fechas = st.slider(
        "Seleccionar rango de fechas:",
        min_value=fecha_min,
        max_value=fecha_max,
        value=(fecha_min, fecha_max),
        format="DD-MM-YYYY"
    )

    # Convertir nuevamente el rango a datetime64 para usarlo en Polars
    dfestadias = dfestadias.filter(
        (pl.col("Fecha") >= pd.to_datetime(rango_fechas[0])) &
        (pl.col("Fecha") <= pd.to_datetime(rango_fechas[1]))
    )

else:
    st.error("No se encontraron las columnas necesarias ('Grupo' o 'Fecha').")
    st.stop()

st.divider()



# ===========================================
# 1️⃣ Composición del Vol. Stock y Holgura m³ con línea de referencia de Capacidad m³
# ===========================================
st.subheader("1️⃣ Composición del Vol. Stock y Holgura (m³) con línea de referencia de Capacidad (m³)")

required_cols = {
    "Capacidad m3",
    "Holgura m3",
    "Volumen Consolidable Con Programa",
    "Volumen Consolidable Sin Programa",
    "Volumen E. Incompletas Sin Programa",
    "Stock Piedra",
}

if required_cols.issubset(dfestadias.columns):
    grupos_unicos = dfestadias["Grupo"].unique().to_list()

    for grupo in grupos_unicos:
        st.markdown(f"### 🔹 Grupo: {grupo}")

        # Filtrar datos por grupo y ordenar por fecha
        df_grupo = (
            dfestadias.filter(pl.col("Grupo") == grupo)
            .select([
                "Fecha",
                "Capacidad m3",
                "Holgura m3",
                "Volumen Consolidable Con Programa",
                "Volumen Consolidable Sin Programa",
                "Volumen E. Incompletas Sin Programa",
                "Stock Piedra",
            ])
            .sort("Fecha")
            .to_pandas()
        )

        # Crear figura
        fig = px.bar()

        # Barras apiladas: componentes del Vol. Stock
        fig.add_bar(
            x=df_grupo["Fecha"],
            y=df_grupo["Volumen Consolidable Con Programa"],
            name="Vol. Consolidable Con Programa",
            marker_color="rgb(31,119,180)",
        )
        fig.add_bar(
            x=df_grupo["Fecha"],
            y=df_grupo["Volumen Consolidable Sin Programa"],
            name="Vol. Consolidable Sin Programa",
            marker_color="rgb(100,149,237)",
        )
        fig.add_bar(
            x=df_grupo["Fecha"],
            y=df_grupo["Volumen E. Incompletas Sin Programa"],
            name="Vol. E. Incompletas Sin Programa",
            marker_color="rgb(135,206,250)",
        )
        fig.add_bar(
            x=df_grupo["Fecha"],
            y=df_grupo["Stock Piedra"],
            name="Stock Piedra",
            marker_color="rgb(255,105,97,0.2)",
        )

        # Holgura m³ (naranjo semitransparente)
        fig.add_bar(
            x=df_grupo["Fecha"],
            y=df_grupo["Holgura m3"],
            name="Holgura m³",
            marker_color="rgba(255,127,14,0.1)",
        )

        # Línea de Capacidad m³
        fig.add_scatter(
            x=df_grupo["Fecha"],
            y=df_grupo["Capacidad m3"],
            mode="lines",
            name="Capacidad m³",
            line=dict(color="red", width=2, dash="dash"),
        )

        # Configuración general
        fig.update_layout(
            title=f"Capacidad vs Composición del Vol. Stock y Holgura — {grupo}",
            xaxis_title="Fecha",
            yaxis_title="Volumen (m³)",
            barmode="stack",
            legend_title="Variable",
            height=500,
            yaxis=dict(
                tickfont=dict(size=12, family="Arial Black", color="gray"), # <-- Fuente y tamaño Eje Y
                title_font=dict(size=12, family="Arial", color="gray")  # <-- Fuente y tamaño Título Eje Y  
            ),
            xaxis=dict(
                tickangle=-45,
                tickmode="array",
                tickvals=df_grupo["Fecha"],
                ticktext=df_grupo["Fecha"].dt.strftime("%b-%d").str.lower(),
            ),
                legend=dict(
                font=dict(
                family="Arial", # <-- Cambia el tipo de fuente de la leyenda
                size=13,        # <-- Cambia el tamaño de la fuente de la leyenda
            ),
        ) 
        )

        st.plotly_chart(fig, use_container_width=True)

    # Resumen general
    resumen = (
        dfestadias.group_by("Grupo")
        .agg([
            pl.col("Capacidad m3").mean().round(1).alias("Capacidad Promedio"),
            (
                pl.col("Volumen Consolidable Con Programa")
                + pl.col("Volumen Consolidable Sin Programa")
                + pl.col("Volumen E. Incompletas Sin Programa")
                + pl.col("Stock Piedra")
            )
            .mean()
            .round(1)
            .alias("Vol. Stock Promedio"),
            pl.col("Holgura m3").mean().round(1).alias("Holgura Promedio"),
        ])
        .to_pandas()
    )

    st.subheader("📊 Resumen Promedios por Grupo")
    st.markdown(
        """
        <style>
            [data-testid="stDataFrame"] table {
                text-align: center !important;
                font-size: 18px !important;
            }
            [data-testid="stDataFrame"] th {
                text-align: center !important;
                font-size: 19px !important;
                font-weight: bold !important;
            }
            [data-testid="stDataFrame"] td {
                text-align: center !important;
                vertical-align: middle !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(resumen, hide_index=True, use_container_width=False)

else:
    st.warning("Faltan columnas necesarias para este gráfico.")




# ===========================================
# 2️⃣ Histórico de % Utilización
# ===========================================
st.subheader("2️⃣ Histórico de % Utilización")

if "% Utilizacion" in dfestadias.columns:
    # Ordenamos por fecha para asegurar el eje X correcto
    df_plot = dfestadias.select(["Fecha", "Grupo", "% Utilizacion"]).sort("Fecha").to_pandas()

    fig2 = px.line(
        df_plot,
        x="Fecha",
        y="% Utilizacion",
        color="Grupo",
        markers=True,
        title="Histórico del % de Utilización",
        line_shape='spline' # <-- ESTO SUAVIZA LAS LÍNEAS
    )

# Mostrar todas las fechas, inclinarlas y eje Y en porcentaje
    fig2.update_layout(
        yaxis=dict(
            title="% Utilización",
            tickformat=".0%",
            tickfont=dict(size=14, family="Arial Black", color="gray"), # <-- Fuente y tamaño Eje Y
            title_font=dict(size=14, family="Arial", color="gray")  # <-- Fuente y tamaño Título Eje Y  
                # Muestra como porcentaje (0.85 → 85%)
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=df_plot["Fecha"],
            ticktext=df_plot["Fecha"].dt.strftime("%b-%d").str.lower(),
            tickangle=-45,
            tickfont=dict(size=12, family="Arial", color="gray"), # <-- Fuente y tamaño Eje X
            title_font=dict(size=14, family="Arial Black", color="gray")  # <-- Fuente y tamaño Título Eje X
        ),
         legend=dict(
            font=dict(
                family="Arial", # <-- Cambia el tipo de fuente de la leyenda
                size=13,        # <-- Cambia el tamaño de la fuente de la leyenda
            )
        ) 
    )
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.warning("No se encontró la columna '% Utilización'.")

st.divider()

# ===========================================
# 3️⃣ Volumen Consolidable Con Programa y CT Consolidables
# ===========================================
st.subheader("3️⃣ Volumen Consolidable Con Programa m³ y CT Consolidables")

# Nota: El chequeo de columnas es más sencillo en Polars, pero tu sintaxis actual funciona si son columnas de Polars
if {"Volumen Consolidable Con Programa", "CT Consolidables"}.issubset(dfestadias.columns):
    
    # --- Gráfico 1: Volumen Consolidable Con Programa (barras)
    # Usando sintaxis POLARS para seleccionar y ordenar, SIN .to_pandas()
    df_plot = (
        dfestadias
        .select(["Fecha", "Grupo", "Volumen Consolidable Con Programa"])
        .sort("Fecha")
    )
    # Plotly Express puede manejar este DataFrame de Polars directamente

    fig3 = px.bar(
        df_plot, # Pasa el DataFrame de Polars directamente
        x="Fecha",
        y="Volumen Consolidable Con Programa",
        color="Grupo",
        barmode="group",
        title="Volumen Consolidable Con Programa (m³)"
    )

    fig3.update_layout(
        xaxis=dict(
            tickmode="array",
            # Accede a los valores de Fecha usando sintaxis Polars si es necesario:
            tickvals=df_plot["Fecha"].to_list(), 
            # Formatea las fechas usando sintaxis Pandas para la visualización del texto:
            ticktext=df_plot["Fecha"].to_pandas().dt.strftime("%b-%d").str.lower(),
            tickangle=-45,
            tickfont=dict(size=12, family="Arial", color="gray"), # <-- Fuente y tamaño Eje X
            title_font=dict(size=14, family="Arial Black", color="gray")  # <-- Fuente y tamaño Título Eje X
        ),
        yaxis=dict(
            title="Volumen (m³)",
            tickfont=dict(size=14, family="Arial Black", color="gray"), # <-- Fuente y tamaño Eje Y
            title_font=dict(size=14, family="Arial", color="gray")  # <-- Fuente y tamaño Título Eje Y
        ),
        title_font=dict(size=18, family="Arial", color="gray"),
          legend=dict(
            font=dict(
                family="Arial", # <-- Cambia el tipo de fuente de la leyenda
                size=13,        # <-- Cambia el tamaño de la fuente de la leyenda
            )
        )  # <-- Fuente y tamaño Título principal
    )

    st.plotly_chart(fig3, use_container_width=True)

    # --- Gráfico 2: CT Consolidables (línea)
    # Usando sintaxis POLARS para seleccionar y ordenar, SIN .to_pandas()
    df_plot2 = (
        dfestadias
        .select(["Fecha", "Grupo", "CT Consolidables"])
        .sort("Fecha")
    )

    fig4 = px.line(
        df_plot2, # Pasa el DataFrame de Polars directamente
        x="Fecha",
        y="CT Consolidables",
        color="Grupo",
        markers=True,
        title="CT Consolidables por Fecha",
        line_shape='spline'
    )

    fig4.update_layout(
        xaxis=dict(
            tickmode="array",
            # Accede a los valores de Fecha usando sintaxis Polars si es necesario:
            tickvals=df_plot2["Fecha"].to_list(), 
            # Formatea las fechas usando sintaxis Pandas para la visualización del texto:
            ticktext=df_plot2["Fecha"].to_pandas().dt.strftime("%b-%d").str.lower(),
            tickangle=-45,
            tickfont=dict(size=12, family="Arial", color="gray"), # <-- Fuente y tamaño Eje X
            title_font=dict(size=14, family="Arial Black", color="gray")  # <-- Fuente y tamaño Título Eje X
        ),
        yaxis=dict(
            title="CT Consolidables",
            tickfont=dict(size=14, family="Arial Black", color="gray"), # <-- Fuente y tamaño Eje Y
            title_font=dict(size=12, family="Arial Black", color="gray")  # <-- Fuente y tamaño Título Eje Y
        ),
        title_font=dict(size=18, family="Arial", color="gray"),
         legend=dict(
            font=dict(
                family="Arial", # <-- Cambia el tipo de fuente de la leyenda
                size=13,        # <-- Cambia el tamaño de la fuente de la leyenda
            )
        ) # <-- Fuente y tamaño Título principal
    )

    st.plotly_chart(fig4, use_container_width=True)

else:
    st.warning("No se encontraron las columnas necesarias para este análisis.")

st.divider()

# ===========================================
# 4️⃣ Comportamiento del % Vol. Stock Piedra
# ===========================================

st.subheader("4️⃣ Comportamiento del % Vol. Stock Piedra")




if "% Vol. Stock Piedra" in dfestadias.columns:
    # Ordenar por fecha y convertir a pandas
    df_plot = dfestadias.select(["Fecha", "Grupo", "% Vol. Stock Piedra"]).sort("Fecha").to_pandas()

    # Crear gráfico con líneas suavizadas
    fig5 = px.line(
        df_plot,
        x="Fecha",
        y="% Vol. Stock Piedra",
        color="Grupo",
        markers=True,
        title="% Vol. Stock Piedra por Fecha",
        line_shape='spline' # <-- ESTO SUAVIZA LAS LÍNEAS
    )

    # Ajustes del eje Y (porcentaje) y X (todas las fechas, -45°)
    fig5.update_layout(
        yaxis=dict(
            title="% Vol. Stock Piedra",
            tickformat=".0%",
            tickfont=dict(size=14, family="Arial Black", color="gray"), # <-- FUENTE EJE Y
            title_font=dict(size=14, family="Arial", color="gray") # <-- FUENTE DEL TITULO DEL EJE Y  # Muestra el eje Y como porcentaje
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=df_plot["Fecha"],
            ticktext=df_plot["Fecha"].dt.strftime("%b-%d").str.lower(),
            tickangle=-45,
            tickfont=dict(size=13, family="Arial", color="black"), # <-- FUENTE EJE X
            title_font=dict(size=14, family="Arial Black", color="gray") # <-- FUENTE DEL TITULO DEL EJE X
        ),
        # Ajustes estéticos de fondo (opcional)
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            font=dict(
                family="Arial", # <-- Cambia el tipo de fuente de la leyenda
                size=13,        # <-- Cambia el tamaño de la fuente de la leyenda
            )
        )
    )
    
    # Ajustes de los marcadores (puntos)
    fig5.update_traces(
        marker=dict(size=8)
    )

    st.plotly_chart(fig5, use_container_width=True)

else:
    st.warning("No se encontró la columna '% Vol. Stock Piedra'.")


