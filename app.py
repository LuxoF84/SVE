import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

#####################

def add_custom_logo():
    st.markdown(
        """
        <style>
        [data-testid="stHeader"] {
            background-image: url("https://www.svti.cl/img/logo-svti.png");
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


#####################



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
    df_resumen = pd.read_excel("estadias.xlsx")
    
    df_stock_completo = pd.read_excel("STOCK.xlsx")
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
        title={'text': f"Grupo {grupo_name}",
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
            ]
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
            color_continuous_scale='Picnic',
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










