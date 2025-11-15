"""
Dashboard Interactivo - NO₂ y T21 (Incendios) en la Península de Yucatán
Datos satelitales 2024 - Google Earth Engine
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
from PIL import Image
import numpy as np
import os

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================
st.set_page_config(
    page_title="NO₂ y T21 - Península de Yucatán",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CONFIGURACIÓN DE RUTAS DE DATOS
# ============================================
# Usar la carpeta actual del proyecto
DATA_DIR = "."

# ============================================
# CONFIGURACIÓN DE MODO OSCURO/CLARO
# ============================================
# Inicializar estado del tema si no existe
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Función para alternar modo oscuro
def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

# ============================================
# ESTILOS CSS PERSONALIZADOS
# ============================================
def get_styles(dark_mode=False):
    if dark_mode:
        return """
        <style>
        .stApp {
            background-color: #1e1e1e !important;
            color: #ffffff !important;
        }
        .stApp > div {
            background-color: #1e1e1e !important;
            color: #ffffff !important;
        }
        .main .block-container {
            background-color: #1e1e1e !important;
            color: #ffffff !important;
        }
        /* Forzar texto blanco en modo oscuro */
        .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            color: #ffffff !important;
        }
        /* Títulos y subtítulos específicos */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
        }
        .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
            color: #ffffff !important;
        }
        /* Controles y labels */
        .stSelectbox label, .stSelectbox div, .stSelectbox span {
            color: #ffffff !important;
        }
        .stSlider label, .stSlider span {
            color: #ffffff !important;
        }
        .stRadio label, .stRadio span {
            color: #ffffff !important;
        }
        .stRadio div label {
            color: #ffffff !important;
        }
        [role="radiogroup"] label {
            color: #ffffff !important;
        }
        .stCheckbox label, .stCheckbox span {
            color: #ffffff !important;
        }
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] button {
            color: #ffffff !important;
        }
        .stTabs [data-baseweb="tab"] span {
            color: #ffffff !important;
        }
        .stTabs button span {
            color: #ffffff !important;
        }
        /* Alertas e info */
        .element-container, .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
            color: #ffffff !important;
        }
        .stAlert > div, .stInfo > div, .stSuccess > div, .stWarning > div, .stError > div {
            color: #ffffff !important;
        }
        /* Textos en general */
        p, span, div {
            color: #ffffff !important;
        }
        /* Métricas y números */
        .metric-value, .metric-label {
            color: #ffffff !important;
        }
        [data-testid="metric-container"] {
            color: #ffffff !important;
        }
        .main-title {
            font-size: 3.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #bb86fc 0%, #6200ea 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            margin-bottom: 0.8rem;
            letter-spacing: -0.02em;
        }
        .subtitle {
            font-size: 1.4rem;
            color: #b3b3b3 !important;
            margin-bottom: 2.5rem;
            font-weight: 400;
        }
        .metric-container {
            background: linear-gradient(135deg, #6200ea 0%, #bb86fc 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 32px rgba(98, 0, 234, 0.3);
            backdrop-filter: blur(8px);
        }
        .info-box {
            background: linear-gradient(135deg, #2a2a2a 0%, #3a3a3a 100%);
            padding: 2rem;
            border-radius: 16px;
            border-left: 4px solid #bb86fc;
            box-shadow: 0 4px 16px rgba(98, 0, 234, 0.2);
            color: #ffffff;
        }
        .stSidebar {
            background: linear-gradient(180deg, #2a2a2a 0%, #1e1e1e 100%) !important;
        }
        .stSidebar .stMarkdown, .stSidebar .stSelectbox label, .stSidebar h1, .stSidebar h2, .stSidebar h3 {
            color: #ffffff !important;
        }
        .stSidebar p, .stSidebar span, .stSidebar div {
            color: #ffffff !important;
        }
        .stSidebar .stMarkdown h1, .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3, .stSidebar .stMarkdown h4 {
            color: #ffffff !important;
        }
        .stSidebar [data-testid="stSidebarNav"] {
            background-color: #2a2a2a !important;
        }
        .metric-card {
            background: #2a2a2a;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            border: 1px solid rgba(187, 134, 252, 0.2);
            color: #ffffff;
        }
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(187, 134, 252, 0.3);
        }
        .dark-mode-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            background: #bb86fc;
            border: none;
            border-radius: 50px;
            padding: 12px 20px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(187, 134, 252, 0.3);
        }
        /* Forzar colores en tablas y dataframes */
        .stDataFrame, .stDataFrame table, .stDataFrame th, .stDataFrame td {
            background-color: #2a2a2a !important;
            color: #ffffff !important;
        }
        /* Tabs en modo oscuro */
        .stTabs [data-baseweb="tab-list"] {
            background: linear-gradient(135deg, #2a2a2a 0%, #3a3a3a 100%) !important;
        }
        .stTabs [data-baseweb="tab"] {
            background: #3a3a3a !important;
            color: #ffffff !important;
        }
        .stTabs [data-baseweb="tab"] span {
            color: #ffffff !important;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #bb86fc 0%, #6200ea 100%) !important;
            color: white !important;
        }
        .stTabs [data-baseweb="tab"]:hover span {
            color: white !important;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #bb86fc 0%, #6200ea 100%) !important;
            color: white !important;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] span {
            color: white !important;
        }
        /* Subheaders y headers específicos de Streamlit */
        [data-testid="stHeader"], .stHeader {
            color: #ffffff !important;
        }
        .stSubheader, [data-testid="stSubheader"] {
            color: #ffffff !important;
        }
        /* Expanders */
        .streamlit-expanderHeader {
            color: #ffffff !important;
        }
        [data-testid="stExpander"] summary {
            color: #ffffff !important;
        }
        /* Botones */
        .stButton button {
            background-color: #bb86fc !important;
            color: #ffffff !important;
            border: none !important;
        }
        .stButton button:hover {
            background-color: #6200ea !important;
        }
        /* Selectores más amplios para capturar todos los textos */
        * {
            color: #ffffff !important;
        }
        /* Excepciones para elementos que deben mantener su color */
        .main-title * {
            color: transparent !important;
        }
        .metric-container * {
            color: white !important;
        }
        /* Radio buttons específicos */
        [data-baseweb="radio"] label {
            color: #ffffff !important;
        }
        [data-baseweb="radio"] span {
            color: #ffffff !important;
        }
        /* Todos los inputs y labels */
        input, label, select, textarea {
            color: #ffffff !important;
        }
        </style>
        """
    else:
        return """
        <style>
        .main-title {
            font-size: 3.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.8rem;
            letter-spacing: -0.02em;
        }
        .subtitle {
            font-size: 1.4rem;
            color: #5a6c7d;
            margin-bottom: 2.5rem;
            font-weight: 400;
        }
        .metric-container {
            background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 32px rgba(108, 92, 231, 0.2);
            backdrop-filter: blur(8px);
        }
        .info-box {
            background: linear-gradient(135deg, #f8f9ff 0%, #f1f3ff 100%);
            padding: 2rem;
            border-radius: 16px;
            border-left: 4px solid #6c5ce7;
            box-shadow: 0 4px 16px rgba(108, 92, 231, 0.1);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background: linear-gradient(135deg, #f8f9ff 0%, #f1f3ff 100%);
            border-radius: 16px;
            padding: 8px;
            margin-bottom: 1rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 14px 24px;
            background: white;
            border-radius: 12px;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
        }
        .stSidebar {
            background: linear-gradient(180deg, #f8f9ff 0%, #f1f3ff 100%);
        }
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            border: 1px solid rgba(108, 92, 231, 0.1);
        }
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(108, 92, 231, 0.15);
        }
        .dark-mode-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            background: #667eea;
            border: none;
            border-radius: 50px;
            padding: 12px 20px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        </style>
        """

# Aplicar estilos según el modo seleccionado
st.markdown(get_styles(st.session_state.dark_mode), unsafe_allow_html=True)

# ============================================
# FUNCIÓN PARA CARGAR DATOS
# ============================================
@st.cache_data
def load_data():
    """Cargar datos del CSV y metadata"""
    try:
        csv_path = os.path.join(DATA_DIR, 'datos_no2_t21.csv')
        metadata_path = os.path.join(DATA_DIR, 'metadata.json')
        
        df = pd.read_csv(csv_path)
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        return df, metadata, None
    except FileNotFoundError as e:
        error_msg = f"""
        **Archivos no encontrados en: {os.path.abspath(DATA_DIR)}**
        
        Debes ejecutar primero el script de descarga:
        
        ```bash
        python 01_download_data.py
        ```
        
        Asegúrate de que DATA_DIR en app.py coincida con OUTPUT_DIR en 01_download_data.py
        
        Archivos esperados:
        - {csv_path}
        - {metadata_path}
        - {os.path.join(DATA_DIR, 'monthly_images')}/
        """
        return None, None, error_msg

# ============================================
# CARGAR DATOS
# ============================================
df, metadata, error = load_data()

if error:
    st.error(error)
    st.info("Asegúrate de haber autenticado Earth Engine antes de ejecutar el script")
    st.code("import ee\nee.Authenticate()\nee.Initialize(project='tu-proyecto')")
    st.stop()

# ============================================
# ENCABEZADO
# ============================================
st.markdown('<p class="main-title">NO₂ y T21 (Incendios) en la Península de Yucatán</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análisis interactivo de datos satelitales mensuales - 2024</p>', unsafe_allow_html=True)

# ============================================
# SIDEBAR - CONTROLES
# ============================================
st.sidebar.header("Panel de Control")

# Botón para alternar modo oscuro
col1, col2 = st.sidebar.columns([3, 1])
with col1:
    st.markdown("### Tema")
with col2:
    if st.button("🌙" if not st.session_state.dark_mode else "☀️",
                 key="dark_mode_toggle",
                 help="Alternar modo oscuro/claro"):
        toggle_dark_mode()
        st.rerun()

st.sidebar.markdown("---")

# Selector de mes
available_months = sorted(df['Fecha'].dt.strftime('%Y-%m').unique().tolist())
selected_month = st.sidebar.selectbox(
    "Selecciona el mes:",
    options=available_months,
    index=len(available_months)-1
)

st.sidebar.markdown("---")

# Métricas del mes seleccionado con diseño mejorado
selected_data = df[df['Fecha'].dt.strftime('%Y-%m') == selected_month].iloc[0]

st.sidebar.markdown("### Datos del Mes")

# Contenedor con estilo mejorado para métricas
st.sidebar.markdown("""
<div style="
    background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
    padding: 1.5rem;
    border-radius: 16px;
    margin: 1rem 0;
    color: white;
">
    <h4 style="margin: 0 0 0.8rem 0; font-size: 1rem;">NO₂ (Dióxido de Nitrógeno)</h4>
    <p style="margin: 0; font-size: 1.2rem; font-weight: 600;">{:.2e} mol/m²</p>
</div>

<div style="
    background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%);
    padding: 1.5rem;
    border-radius: 16px;
    margin: 1rem 0;
    color: white;
">
    <h4 style="margin: 0 0 0.8rem 0; font-size: 1rem;">T21 (Temperatura de Brillo)</h4>
    <p style="margin: 0; font-size: 1.2rem; font-weight: 600;">{:.1f} K</p>
</div>
""".format(selected_data['NO2'], selected_data['T21']), unsafe_allow_html=True)

# Calcular cambio respecto al mes anterior
if len(df) > 1:
    current_idx = df[df['Fecha'].dt.strftime('%Y-%m') == selected_month].index[0]
    if current_idx > 0:
        prev_no2 = df.iloc[current_idx - 1]['NO2']
        prev_t21 = df.iloc[current_idx - 1]['T21']
        delta_no2 = ((selected_data['NO2'] - prev_no2) / prev_no2) * 100
        delta_t21 = selected_data['T21'] - prev_t21
        
        st.sidebar.markdown("### Cambio vs Mes Anterior")

        # Diseño mejorado para cambios mensuales
        delta_color_no2 = "#00b894" if delta_no2 >= 0 else "#e17055"
        delta_color_t21 = "#00b894" if delta_t21 >= 0 else "#e17055"

        st.sidebar.markdown("""
        <div style="
            background: white;
            padding: 1rem;
            border-radius: 12px;
            margin: 0.5rem 0;
            border-left: 4px solid {};
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        ">
            <h5 style="margin: 0 0 0.3rem 0; color: #2d3436;">Δ NO₂</h5>
            <p style="margin: 0; font-size: 1.1rem; font-weight: 600; color: {};">{:+.1f}%</p>
        </div>

        <div style="
            background: white;
            padding: 1rem;
            border-radius: 12px;
            margin: 0.5rem 0;
            border-left: 4px solid {};
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        ">
            <h5 style="margin: 0 0 0.3rem 0; color: #2d3436;">Δ T21</h5>
            <p style="margin: 0; font-size: 1.1rem; font-weight: 600; color: {};">{:+.1f} K</p>
        </div>
        """.format(delta_color_no2, delta_color_no2, delta_no2, delta_color_t21, delta_color_t21, delta_t21), unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.info("**Tip**: Usa las pestañas superiores para explorar diferentes visualizaciones")

# ============================================
# TABS PRINCIPALES
# ============================================
tab1, tab2, tab3, tab4 = st.tabs(["Mapa Interactivo", "Series Temporales", "Análisis de Correlación", "Información"])

# ============================================
# TAB 1: MAPA INTERACTIVO
# ============================================
with tab1:
    st.subheader(f"Visualización Espacial - {selected_month}")
    
    image_dir = Path(DATA_DIR) / 'monthly_images'
    
    if not image_dir.exists():
        st.warning("Carpeta 'monthly_images' no encontrada. Ejecuta el script de descarga primero.")
    else:
        # Selector de modo de visualización
        view_mode = st.radio(
            "Modo de visualización:",
            ["Comparación lado a lado", "Superposición con control", "Vista individual"],
            horizontal=True
        )
        
        st.markdown("---")
        
        # MODO 1: Comparación lado a lado (default)
        if view_mode == "Comparación lado a lado":
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### NO₂ - Dióxido de Nitrógeno")
                img_path = image_dir / f"no2_{selected_month}.png"
                if img_path.exists():
                    img = Image.open(img_path)
                    st.image(img, use_container_width=True)
                else:
                    st.error(f"Imagen no disponible: {img_path.name}")
            
            with col2:
                st.markdown("#### T21 - Temperatura de Brillo (Incendios)")
                img_path = image_dir / f"t21_{selected_month}.png"
                if img_path.exists():
                    img = Image.open(img_path)
                    st.image(img, use_container_width=True)
                else:
                    st.error(f"Imagen no disponible: {img_path.name}")
        
        # MODO 2: Superposición con control de opacidad
        elif view_mode == "Superposición con control":
            st.markdown("#### Mapa Superpuesto con Control de Capas")
            
            # Controles
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                opacity_no2 = st.slider("Opacidad NO₂", 0.0, 1.0, 1.0, 0.1)
            
            with col2:
                opacity_t21 = st.slider("Opacidad T21", 0.0, 1.0, 0.5, 0.1)
            
            with col3:
                blend_mode = st.selectbox("Mezcla", ["Normal", "Multiplicar", "Pantalla"])
            
            # Cargar imágenes
            img_no2_path = image_dir / f"no2_{selected_month}.png"
            img_t21_path = image_dir / f"t21_{selected_month}.png"
            
            if img_no2_path.exists() and img_t21_path.exists():
                from PIL import ImageDraw
                
                # Cargar imágenes
                img_no2 = Image.open(img_no2_path).convert('RGBA')
                img_t21 = Image.open(img_t21_path).convert('RGBA')
                
                # Asegurar mismo tamaño
                if img_no2.size != img_t21.size:
                    img_t21 = img_t21.resize(img_no2.size, Image.Resampling.LANCZOS)
                
                # Crear capa base
                base = Image.new('RGBA', img_no2.size, (255, 255, 255, 255))
                
                # Aplicar opacidad a NO2
                img_no2_alpha = img_no2.copy()
                img_no2_alpha.putalpha(int(255 * opacity_no2))
                
                # Aplicar opacidad a T21
                img_t21_alpha = img_t21.copy()
                img_t21_alpha.putalpha(int(255 * opacity_t21))
                
                # Superponer capas
                result = Image.alpha_composite(base, img_no2_alpha)
                result = Image.alpha_composite(result, img_t21_alpha)
                
                # Mostrar resultado
                st.image(result, use_container_width=True)
                
                # Leyenda
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**NO₂** (Opacidad: {opacity_no2:.0%})")
                with col2:
                    st.markdown(f"**T21** (Opacidad: {opacity_t21:.0%})")
            else:
                st.error("Una o ambas imágenes no están disponibles")
        
        # MODO 3: Vista individual con selector
        else:
            layer_choice = st.radio(
                "Selecciona la capa a visualizar:",
                ["NO₂ - Dióxido de Nitrógeno", "T21 - Temperatura de Brillo (Incendios)"],
                horizontal=True
            )
            
            st.markdown("---")
            
            if "NO₂" in layer_choice:
                st.markdown("#### NO₂ - Dióxido de Nitrógeno")
                img_path = image_dir / f"no2_{selected_month}.png"
                if img_path.exists():
                    img = Image.open(img_path)
                    st.image(img, use_container_width=True)
                else:
                    st.error(f"Imagen no disponible")
            else:
                st.markdown("#### T21 - Temperatura de Brillo (Incendios)")
                img_path = image_dir / f"t21_{selected_month}.png"
                if img_path.exists():
                    img = Image.open(img_path)
                    st.image(img, use_container_width=True)
                else:
                    st.error(f"Imagen no disponible")
        
        # Leyendas en expander (común para todos los modos)
        with st.expander("Ver Leyendas de Colores", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **NO₂ (Dióxido de Nitrógeno)**
                - 🟣 Negro/Morado oscuro: Concentraciones muy bajas
                - 🔵 Azul/Morado: Concentraciones bajas
                - 🔴 Rojo: Concentraciones medias
                - 🟠 Naranja: Concentraciones altas
                - 🟡 Amarillo/Blanco: Concentraciones muy altas
                
                **Fuente**: Contaminación atmosférica, tráfico vehicular, industria
                """)
            with col2:
                st.markdown("""
                **T21 (Temperatura de Brillo)**
                - 🟨 Amarillo claro: 300-320K (temperatura normal)
                - 🟧 Naranja: 320-350K (calor moderado)
                - 🔴 Rojo: 350-380K (incendios activos)
                - 🟥 Rojo oscuro: >380K (incendios intensos)
                
                **Fuente**: Detección de incendios forestales y quemas agrícolas
                """)
        
        # Tips de uso
        st.info("""
        **Tips de uso**:
        - **Comparación lado a lado**: Ideal para ver ambos datasets simultáneamente
        - **Superposición con control**: Permite ajustar la transparencia y ver relaciones espaciales
        - **Vista individual**: Enfócate en una sola variable a la vez
        """)

# ============================================
# TAB 2: SERIES TEMPORALES
# ============================================
with tab2:
    st.subheader("Evolución Temporal - Año 2024")
    
    # Gráfico combinado en dos subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('NO₂ - Dióxido de Nitrógeno', 'T21 - Temperatura de Brillo (Incendios)'),
        vertical_spacing=0.15,
        row_heights=[0.5, 0.5]
    )
    
    # Plot NO2 con nuevos colores
    fig.add_trace(
        go.Scatter(
            x=df['Fecha'],
            y=df['NO2'],
            mode='lines+markers',
            name='NO₂',
            line=dict(color='#6c5ce7', width=4),
            marker=dict(size=12, symbol='circle', line=dict(width=2, color='white')),
            hovertemplate='<b>%{x|%B %Y}</b><br>NO₂: %{y:.2e} mol/m²<extra></extra>'
        ),
        row=1, col=1
    )

    # Línea de tendencia NO2
    z_no2 = np.polyfit(range(len(df)), df['NO2'], 1)
    p_no2 = np.poly1d(z_no2)
    fig.add_trace(
        go.Scatter(
            x=df['Fecha'],
            y=p_no2(range(len(df))),
            mode='lines',
            name='Tendencia NO₂',
            line=dict(color='rgba(108, 92, 231, 0.3)', width=3, dash='dash'),
            showlegend=True
        ),
        row=1, col=1
    )
    
    # Plot T21 con nuevos colores
    fig.add_trace(
        go.Scatter(
            x=df['Fecha'],
            y=df['T21'],
            mode='lines+markers',
            name='T21',
            line=dict(color='#fd79a8', width=4),
            marker=dict(size=12, symbol='diamond', line=dict(width=2, color='white')),
            hovertemplate='<b>%{x|%B %Y}</b><br>T21: %{y:.1f} K<extra></extra>'
        ),
        row=2, col=1
    )

    # Línea de tendencia T21
    z_t21 = np.polyfit(range(len(df)), df['T21'], 1)
    p_t21 = np.poly1d(z_t21)
    fig.add_trace(
        go.Scatter(
            x=df['Fecha'],
            y=p_t21(range(len(df))),
            mode='lines',
            name='Tendencia T21',
            line=dict(color='rgba(253, 121, 168, 0.3)', width=3, dash='dash'),
            showlegend=True
        ),
        row=2, col=1
    )
    
    # Actualizar layout
    fig.update_xaxes(title_text="Mes", row=2, col=1, showgrid=True)
    fig.update_yaxes(title_text="Densidad (mol/m²)", row=1, col=1, showgrid=True)
    fig.update_yaxes(title_text="Temperatura (K)", row=2, col=1, showgrid=True)
    
    # Configurar template según el modo
    template = 'plotly_dark' if st.session_state.dark_mode else 'plotly_white'
    bg_color = 'rgba(30, 30, 30, 0.8)' if st.session_state.dark_mode else 'rgba(248, 249, 255, 0.8)'
    paper_color = '#1e1e1e' if st.session_state.dark_mode else 'white'

    fig.update_layout(
        height=800,
        hovermode='x unified',
        showlegend=True,
        template=template,
        font=dict(size=12),
        plot_bgcolor=bg_color,
        paper_bgcolor=paper_color
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Estadísticas resumidas con diseño moderno
    st.markdown("### Estadísticas del Año 2024")

    col1, col2, col3, col4 = st.columns(4, gap="medium")

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4 style="margin: 0 0 0.5rem 0; color: #6c5ce7; font-size: 0.9rem;">NO₂ PROMEDIO</h4>
            <p style="margin: 0; font-size: 1.4rem; font-weight: 600; color: #2d3436;">{:.2e}</p>
            <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #636e72;">mol/m²</p>
        </div>
        """.format(df['NO2'].mean()), unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4 style="margin: 0 0 0.5rem 0; color: #fd79a8; font-size: 0.9rem;">NO₂ MÁXIMO</h4>
            <p style="margin: 0; font-size: 1.4rem; font-weight: 600; color: #2d3436;">{:.2e}</p>
            <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #636e72;">{}</p>
        </div>
        """.format(df['NO2'].max(), df['Fecha'][df['NO2'].idxmax()].strftime('%B')), unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4 style="margin: 0 0 0.5rem 0; color: #fdcb6e; font-size: 0.9rem;">T21 PROMEDIO</h4>
            <p style="margin: 0; font-size: 1.4rem; font-weight: 600; color: #2d3436;">{:.1f}</p>
            <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #636e72;">K</p>
        </div>
        """.format(df['T21'].mean()), unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <h4 style="margin: 0 0 0.5rem 0; color: #e84393; font-size: 0.9rem;">T21 MÁXIMO</h4>
            <p style="margin: 0; font-size: 1.4rem; font-weight: 600; color: #2d3436;">{:.1f}</p>
            <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #636e72;">{}</p>
        </div>
        """.format(df['T21'].max(), df['Fecha'][df['T21'].idxmax()].strftime('%B')), unsafe_allow_html=True)
    
    # Tabla de datos
    with st.expander("Ver Tabla de Datos Completa"):
        df_display = df.copy()
        df_display['Fecha'] = df_display['Fecha'].dt.strftime('%Y-%m')
        df_display['NO2'] = df_display['NO2'].apply(lambda x: f"{x:.2e}")
        df_display['T21'] = df_display['T21'].apply(lambda x: f"{x:.2f}")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

# ============================================
# TAB 3: ANÁLISIS DE CORRELACIÓN
# ============================================
with tab3:
    st.subheader("Análisis de Correlación NO₂ vs T21")
    
    # Calcular correlación
    correlation = df['NO2'].corr(df['T21'])
    
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        # Gráfico de dispersión con línea de tendencia
        fig = go.Figure()
        
        # Puntos de dispersión con colores modernos
        fig.add_trace(go.Scatter(
            x=df['NO2'],
            y=df['T21'],
            mode='markers',
            marker=dict(
                size=18,
                color=df['T21'],
                colorscale=[[0, '#6c5ce7'], [0.5, '#a29bfe'], [1.0, '#fd79a8']],
                showscale=True,
                colorbar=dict(
                    title="T21 (K)",
                    thickness=18,
                    len=0.7,
                    bgcolor='rgba(255,255,255,0.8)'
                ),
                line=dict(width=2, color='white')
            ),
            text=df['Fecha'].dt.strftime('%B %Y'),
            hovertemplate='<b>%{text}</b><br>NO₂: %{x:.2e}<br>T21: %{y:.1f}K<extra></extra>',
            name='Datos mensuales'
        ))
        
        # Línea de tendencia con colores modernos
        z = np.polyfit(df['NO2'], df['T21'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(df['NO2'].min(), df['NO2'].max(), 100)

        fig.add_trace(go.Scatter(
            x=x_trend,
            y=p(x_trend),
            mode='lines',
            name='Línea de tendencia',
            line=dict(color='#e84393', width=4, dash='dash')
        ))
        
        # Configurar template según el modo para gráfico de correlación
        template = 'plotly_dark' if st.session_state.dark_mode else 'plotly_white'
        bg_color = 'rgba(30, 30, 30, 0.8)' if st.session_state.dark_mode else 'rgba(248, 249, 255, 0.8)'
        paper_color = '#1e1e1e' if st.session_state.dark_mode else 'white'
        title_color = '#ffffff' if st.session_state.dark_mode else '#2d3436'

        fig.update_layout(
            title=dict(
                text='Relación entre NO₂ y Temperatura de Brillo',
                font=dict(size=18, color=title_color)
            ),
            xaxis_title='NO₂ - Densidad de columna (mol/m²)',
            yaxis_title='T21 - Temperatura de Brillo (K)',
            height=550,
            template=template,
            hovermode='closest',
            plot_bgcolor=bg_color,
            paper_bgcolor=paper_color
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Coeficiente de correlación
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="margin: 0; font-size: 1.2rem;">Coeficiente de Correlación</h3>
            <h1 style="margin: 1rem 0; font-size: 4rem;">{correlation:.3f}</h1>
            <p style="margin: 0; font-size: 1rem;">Correlación de Pearson</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Interpretación
        if abs(correlation) < 0.3:
            interpretation = "Correlación Débil"
            color = "linear-gradient(135deg, #fdcb6e 0%, #e17055 100%)"
            desc = "La relación entre las variables es mínima o inexistente."
        elif abs(correlation) < 0.7:
            interpretation = "Correlación Moderada"
            color = "linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%)"
            desc = "Existe una relación parcial entre las variables."
        else:
            interpretation = "Correlación Fuerte"
            color = "linear-gradient(135deg, #fd79a8 0%, #e84393 100%)"
            desc = "Las variables están fuertemente relacionadas."
        
        st.markdown(f"""
        <div style="background: {color}; padding: 1.5rem; border-radius: 10px; color: white;">
            <h3 style="margin: 0;">{interpretation}</h3>
            <p style="margin-top: 0.5rem; font-size: 0.95rem;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Explicación
        st.markdown("""
        ### Interpretación

        Una **correlación positiva** indica que cuando aumenta la temperatura
        de brillo (incendios), también tiende a aumentar el NO₂ en la atmósfera.

        Esto sugiere que los **incendios forestales y quemas agrícolas**
        contribuyen significativamente a las emisiones de dióxido de nitrógeno
        en la Península de Yucatán.
        """)

# ============================================
# TAB 4: INFORMACIÓN
# ============================================
with tab4:
    st.markdown("""
    ## Acerca de este Dashboard

    ### Fuentes de Datos
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### NO₂ (Dióxido de Nitrógeno)
        
        - **Satélite**: Copernicus Sentinel-5P
        - **Sensor**: TROPOMI
        - **Resolución**: ~7×3.5 km
        - **Variable**: Densidad de columna troposférica
        - **Unidades**: mol/m²
        - **Actualización**: Diaria
        
        El NO₂ es un contaminante atmosférico producido principalmente por:
        - Combustión de vehículos
        - Procesos industriales
        - Incendios y quemas
        - Generación de energía
        """)
    
    with col2:
        st.markdown("""
        #### T21 (Temperatura de Brillo)
        
        - **Sistema**: FIRMS (NASA)
        - **Sensores**: MODIS/VIIRS
        - **Banda**: 4 μm (infrarrojo medio)
        - **Variable**: Temperatura de brillo
        - **Unidades**: Kelvin (K)
        - **Actualización**: Diaria
        
        T21 detecta incendios activos mediante:
        - Anomalías térmicas
        - Puntos de calor
        - Quemas agrícolas
        - Incendios forestales
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Región de Estudio
    
    **Península de Yucatán, México**
    - **Estados**: Yucatán, Quintana Roo, Campeche
    - **Coordenadas**: 19.4°N - 21.7°N, 86.7°W - 90.6°W
    - **Superficie**: ~145,000 km²
    - **Ecosistema**: Selva tropical, manglares, zona costera
    - **Periodo analizado**: Enero - Diciembre 2024
    
    ### Metodología
    
    1. **Adquisición de datos**: Google Earth Engine API
    2. **Procesamiento temporal**: Promedios mensuales por región
    3. **Análisis estadístico**: Correlación de Pearson
    4. **Visualización**: Dashboard interactivo con Streamlit + Plotly
    
    ### Hallazgos Clave
    
    - La **temporada de incendios** en la Península de Yucatán ocurre típicamente entre **marzo y mayo** (temporada seca)
    - Los **incendios forestales y quemas agrícolas** contribuyen significativamente a las emisiones de NO₂
    - Existe una **correlación positiva** entre temperatura de brillo (T21) y concentraciones de NO₂
    - Las **áreas urbanas** muestran concentraciones de NO₂ más elevadas de forma constante
    
    ### Tecnologías Utilizadas
    
    - **Google Earth Engine**: Procesamiento de datos satelitales
    - **Python**: Análisis de datos (pandas, numpy)
    - **Streamlit**: Framework de visualización web
    - **Plotly**: Gráficos interactivos
    - **PIL**: Procesamiento de imágenes
    
    ### Referencias
    
    - [Sentinel-5P TROPOMI](https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-5p)
    - [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/)
    - [Google Earth Engine](https://earthengine.google.com/)
    
    ### Desarrollo
    
    Este dashboard fue desarrollado para facilitar el análisis de datos satelitales 
    de calidad del aire e incendios en la Península de Yucatán.
    
    ---
    
    **Sugerencia**: Usa este dashboard para identificar patrones estacionales, 
    correlacionar eventos de incendios con calidad del aire, y analizar tendencias 
    temporales de contaminación atmosférica.
    """)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style="
    text-align: center;
    background: linear-gradient(135deg, #f8f9ff 0%, #f1f3ff 100%);
    padding: 2rem;
    border-radius: 16px;
    margin-top: 3rem;
    border: 1px solid rgba(108, 92, 231, 0.1);
">
    <p style="margin: 0; color: #6c5ce7; font-weight: 600;">Desarrollado con Streamlit | Datos: Google Earth Engine</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #636e72;">Península de Yucatán - Análisis Satelital 2024</p>
</div>
""", unsafe_allow_html=True)
