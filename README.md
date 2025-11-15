# Dashboard NO₂ y T21 - Península de Yucatán

Dashboard interactivo para visualizar datos satelitales de dióxido de nitrógeno (NO₂) e incendios (T21) en la Península de Yucatán durante 2024.

## Descripción

Aplicación web desarrollada con Streamlit que permite analizar la relación entre contaminación atmosférica e incendios forestales utilizando datos de Google Earth Engine.

### Características principales:

- Visualización de mapas satelitales mensuales
- Análisis de series temporales
- Correlación entre NO₂ y temperatura de brillo
- Interface interactiva con múltiples modos de visualización

## Datos

### NO₂ (Dióxido de Nitrógeno)
- **Fuente**: Copernicus Sentinel-5P (TROPOMI)
- **Resolución**: ~7×3.5 km
- **Unidades**: mol/m²

### T21 (Temperatura de Brillo)
- **Fuente**: NASA FIRMS (MODIS/VIIRS)
- **Banda**: 4 μm (infrarrojo medio)
- **Unidades**: Kelvin (K)

## Estructura del proyecto

```
TECHWEEK/
├── streamlit_app_optimized.py    # Aplicación principal
├── datos_no2_t21.csv            # Datos mensuales
├── metadata.json                # Metadatos del procesamiento
├── monthly_images/              # Mapas satelitales
│   ├── no2_2024-01.png         # Mapas de NO₂ mensuales
│   └── t21_2024-01.png         # Mapas de T21 mensuales
└── README.md                   # Este archivo
```

## Instalación

```bash
# Instalar dependencias
uv add streamlit pandas plotly pillow numpy

# Ejecutar la aplicación
streamlit run streamlit_app_optimized.py
```

## Uso

1. Ejecuta la aplicación
2. Selecciona el mes deseado desde la barra lateral
3. Explora las diferentes pestañas:
   - **Mapa Interactivo**: Visualización espacial de los datos
   - **Series Temporales**: Evolución temporal durante 2024
   - **Análisis de Correlación**: Relación entre NO₂ y T21
   - **Información**: Detalles técnicos y metodología

## Región de estudio

**Península de Yucatán, México**
- Estados: Yucatán, Quintana Roo, Campeche
- Coordenadas: 19.4°N - 21.7°N, 86.7°W - 90.6°W
- Periodo: Enero - Diciembre 2024

## Tecnologías

- **Google Earth Engine**: Procesamiento de datos satelitales
- **Streamlit**: Framework web
- **Plotly**: Gráficos interactivos
- **Python**: pandas, numpy, PIL

## Autor

**Edgar Yepez**
📧 ypz.edgar@gmail.com

## Licencia

Este proyecto utiliza datos públicos de Copernicus y NASA FIRMS.