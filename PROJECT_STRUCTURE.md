# 📁 Estructura del Proyecto - Pirate Galaxy AFK Bot

## 🎯 Visión General

Este proyecto contiene **DOS versiones** del bot:

1. **`main.py`** - Versión original de Eclip5e (sin modificaciones)
2. **`main_enhanced.py`** - Versión mejorada con UI gráfica y OCR avanzado

---

## 📂 Estructura de Carpetas

```
pirate-galaxy-afk-bot/
│
├── 📄 main.py                    # ⭐ Versión ORIGINAL de Eclip5e
├── 📄 main_enhanced.py           # ⭐ Versión MEJORADA con UI
├── 📄 README.md                  # Guía de instalación y uso
├── 📄 PROJECT_STRUCTURE.md       # Este archivo
├── 📄 .gitignore
│
├── 📂 src/                       # Código fuente organizado
│   ├── 📂 bot/                   # Lógica principal del bot
│   │   ├── __init__.py
│   │   ├── bot_core.py           # Clase PGBot y BotState
│   │   └── importer.py           # Verificador de dependencias
│   │
│   ├── 📂 ui/                    # Interfaz gráfica (PyQt5)
│   │   ├── __init__.py
│   │   ├── bot_window.py         # Ventana principal de UI
│   │   └── energy_overlay.py    # Overlay de energía
│   │
│   ├── 📂 detection/             # Sistemas de detección
│   │   ├── __init__.py
│   │   ├── energy_detector.py   # Detector de orbes de energía
│   │   ├── ocr_enhanced.py      # OCR mejorado con Tesseract
│   │   └── position_tracker.py  # Tracker de posición del jugador
│   │
│   ├── 📂 navigation/            # Sistema de navegación
│   │   ├── __init__.py
│   │   └── map_processor.py     # Procesador de mapas del juego
│   │
│   └── 📂 utils/                 # Utilidades generales
│       ├── __init__.py
│       └── logger.py             # Sistema de logging
│
├── 📂 tools/                     # Herramientas de desarrollo/debug
│   ├── map_analyzer.py           # Analizador de mapas
│   ├── energy_debug_tool.py     # Debug de detección de energía
│   ├── test_energy_debug.py     # Tests de energía
│   ├── crionita_config_tool.py  # Configurador de región de crionita
│   ├── prepare_for_editing.py   # Preparar mapas para edición
│   └── process_edited_map.py    # Procesar mapas editados
│
├── 📂 config/                    # Archivos de configuración
│   ├── settings.json             # ⚙️ Configuración principal del bot
│   └── energy_config.txt         # Configuración de energía
│
├── 📂 scripts/                   # Scripts de ejecución
│   ├── run_enhanced.bat          # ▶️ Ejecutar versión mejorada
│   ├── run_original.bat          # ▶️ Ejecutar versión original
│   └── install_dependencies.bat  # 📦 Instalar dependencias
│
├── 📂 data/                      # Datos del juego
│   ├── images/                   # Imágenes de referencia para OCR
│   │   ├── minimap.png
│   │   ├── energy.png
│   │   ├── target_red.png
│   │   └── ...
│   └── maps/                     # Mapas del juego procesados
│       ├── mantis_hive_map.png
│       └── navigation_graph.pkl
│
├── 📂 logs/                      # Logs de sesión
│   ├── session_*.txt             # Logs de cada sesión
│   └── stats.json                # Estadísticas acumuladas
│
├── 📂 output/                    # Outputs generados
│   └── energy_detection/         # Capturas de detección de energía
│
└── 📂 old_structure/             # ⚠️ Archivos de la estructura anterior
    ├── PGBot.py                  # (Antiguo main)
    ├── PGBot_Enhanced.py         # (Antiguo main enhanced)
    └── ...
```

---

## 🚀 Cómo Ejecutar

### ✅ Opción 1: Versión Original (Eclip5e)

```bash
# Desde la raíz del proyecto:
python main.py

# O usando el script .bat:
scripts\run_original.bat
```

**Características:**
- ✔️ Bot original de Eclip5e sin modificaciones
- ✔️ CLI simple con información de HP/Energía
- ✔️ Hotkeys: Q (salir), P (pausar)

---

### ✅ Opción 2: Versión Mejorada (Enhanced)

```bash
# Desde la raíz del proyecto:
python main_enhanced.py

# O usando el script .bat:
scripts\run_enhanced.bat
```

**Características adicionales:**
- ✨ Interfaz gráfica con PyQt5
- 📊 Estadísticas en tiempo real (kills, loot, crionita)
- 🔍 OCR mejorado para mejor lectura
- 📈 Gráficas de HP/Energy
- ⚡ Energy Loading mode (hotkey E)
- 📝 Sistema de logging avanzado
- 🎨 UI moderna estilo Catppuccin

**Dependencias extra:**
```bash
pip install PyQt5 PyQtChart
```

---

## ⚙️ Configuración

### Archivo principal: `config/settings.json`

```json
{
    "tesseract": "C:/Program Files/Tesseract-OCR/tesseract.exe",
    "priority": ["enemy", "loot", "enemyIdle"],
    "healOnHp": 30,
    "defendOnHp": 45,
    "runOnHp": 10,
    "lowEnergy": 1000,
    "skillset": "custom",
    "presets": {
        "storm": [...],
        "tank": [...],
        "sniper": [...],
        "custom": [...]
    }
}
```

### Configuraciones multi-resolución

El bot detecta automáticamente tu resolución y ajusta las regiones de OCR:

- ✅ 1920x1080 (Full HD)
- ✅ 1366x768 (HD)
- ✅ 1280x720 (HD Ready)
- ✅ Default (ajustable)

---

## 🛠️ Herramientas de Desarrollo

### 1. Analizador de Mapas
```bash
python tools/map_analyzer.py
```
Analiza mapas del juego para encontrar valores de threshold óptimos.

### 2. Debug de Energía
```bash
python tools/energy_debug_tool.py
```
Herramienta visual para calibrar detección de orbes de energía.

### 3. Configurador de Crionita
```bash
python tools/crionita_config_tool.py
```
Configura la región de lectura de crionita para tu resolución.

---

## 📦 Dependencias

### Básicas (ambas versiones):
```bash
pip install pyautogui keyboard colorama requests pytesseract opencv-python pywin32
```

### Adicionales (solo versión enhanced):
```bash
pip install PyQt5 PyQtChart
```

### Tesseract OCR:
Descarga e instala desde: https://github.com/UB-Mannheim/tesseract/wiki

---

## 🔑 Hotkeys

### Versión Original:
- **Q** - Cerrar bot
- **P** - Pausar/Reanudar

### Versión Enhanced:
- **Q** - Cerrar bot
- **P** - Pausar/Reanudar
- **E** - Activar/Desactivar Energy Loading Mode

---

## 📊 Sistema de Estadísticas (Enhanced)

La versión mejorada rastrea automáticamente:

- ⚔️ **Kills** - Enemigos eliminados
- 📦 **Collections** - Loot recolectado
- 💎 **Crionita** - Dinero ganado
- ❤️ **Low Life Events** - Veces que HP bajó de 30%
- ⚡ **Energy** - Nivel de energía actual

Los logs se guardan en `logs/session_*.txt` y estadísticas en `logs/stats.json`.

---

## 🎮 Presets de Habilidades

Presets incluidos en `config/settings.json`:

1. **Storm** - DPS con cohetes y perforación
2. **Tank** - Defensa con escudo y taunt
3. **Engineer** - Soporte con reparación
4. **Shock** - Control con stuns
5. **Sniper** - Daño a distancia
6. **Custom** - Personalizable

---

## 🔧 Desarrollo

### Agregar nuevos módulos:

1. Crea tu módulo en `src/`
2. Agrega `__init__.py` en la carpeta
3. Importa desde `main_enhanced.py`:
```python
from src.tu_modulo import TuClase
```

### Estructura de imports:
```python
# Correcto ✅
from src.bot import PGBot, BotState
from src.ui.bot_window import BotUIWindow
from src.detection.energy_detector import EnergyDetector

# Incorrecto ❌
from core.bot import PGBot  # Antigua estructura
from bot import PGBot       # Path relativo
```

---

## 📝 Notas Importantes

1. **No modificar `main.py`** - Es la versión original de Eclip5e intacta
2. **Todas las mejoras van en `main_enhanced.py`**
3. Los archivos antiguos están en `old_structure/` por si necesitas referencia
4. La carpeta `src/` contiene código organizado por responsabilidad
5. `tools/` son utilidades de desarrollo, no se ejecutan en producción

---

## 🐛 Troubleshooting

### Error: "No module named 'src'"
```bash
# Asegúrate de ejecutar desde la raíz del proyecto:
cd pirate-galaxy-afk-bot
python main_enhanced.py
```

### Error: "PyQt5 not found"
```bash
pip install PyQt5 PyQtChart
```

### Error: "Tesseract not found"
Edita `config/settings.json` y actualiza la ruta de tesseract:
```json
{
    "tesseract": "C:/Program Files/Tesseract-OCR/tesseract.exe"
}
```

---

## 📜 Créditos

- **Original:** Eclip5e
- **Enhanced:** jihadz14
- **Version:** 0.4.0

---

## 📄 Licencia

Ver archivo LICENSE para más detalles.
