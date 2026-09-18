# Estructura del Proyecto Web

## 📁 Organización de Carpetas

```
Web/
├── app.py                 # Archivo principal (orquestador)
├── utils/               # Utilidades y lógica
│   ├── config.py       # Configuración central
│   ├── translations.py # Idiomas y traducciones
│   ├── data_utils.py   # Carga y procesamiento de datos
│   ├── price_utils.py  # Conversión de precios
│   ├── game_utils.py   # Utilidades de juegos
│   └── analytics.py    # Análisis y cálculos
├── components/         # Componentes reutilizables
│   ├── cards.py       # Tarjetas de juegos
│   ├── metrics.py     # Métricas y números (próxima)
│   ├── charts.py      # Gráficos (próxima)
│   └── forms.py       # Formularios (próxima)
├── pages/             # Páginas principales
│   ├── dashboard.py   # Panel principal (próxima)
│   ├── game_detail.py # Detalle de juego (próxima)
│   ├── favorites.py   # Página de favoritos (próxima)
│   └── chat.py        # Asistente IA (próxima)
└── styles/            # Estilos CSS
    └── theme.py      # Temas y estilos globales
```

## 📝 Descripción de Módulos

### **utils/**
- `config.py` - Configuración global (rutas, URLs, constantes)
- `translations.py` - Sistema multiidioma (Español, English, Français, Português)
- `data_utils.py` - Carga de CSVs, inicialización de archivos, utilidades generales
- `price_utils.py` - Conversión y formateo de precios
- `game_utils.py` - Procesamiento de juegos, imágenes, información de Steam
- `analytics.py` - Cálculos de tendencias, ranking, popularidad

### **components/**
- `cards.py` - Tarjetas de juegos (estándar y dashboard)

### **pages/** (En desarrollo)
- Cada página principal será un módulo separado

### **styles/**
- `theme.py` - CSS y estilos globales

## 🚀 Ventajas de la Nueva Estructura

✅ **Modularidad** - Cada módulo tiene una responsabilidad clara  
✅ **Reutilización** - Funciones y componentes reutilizables  
✅ **Mantenibilidad** - Fácil de encontrar y modificar código  
✅ **Escalabilidad** - Fácil agregar nuevas páginas y componentes  
✅ **Legibilidad** - Código organizado y documentado  
✅ **Independencia** - Cambios aislados sin efectos secundarios

## 📖 Cómo Usar

### Importar utilidades:
```python
from utils.config import BASE_DIR, LANGUAGE_NAMES
from utils.translations import get_translations
from utils.data_utils import load_data, fix_nan
from utils.game_utils import get_enhanced_game_image
from utils.price_utils import format_local_price
```

### Usar componentes:
```python
from components.cards import render_game_card, render_dashboard_card

render_game_card(appid, name, translations, key, df_listado, df_info, df_detalles, df_plataformas)
```

## 🔄 Próximos Pasos

1. Crear componentes de UI (`metrics.py`, `charts.py`, `forms.py`)
2. Dividir páginas principales en módulos separados
3. Crear `app.py` limpio que solo orqueste todo
4. Agregar más utilidades según sea necesario
