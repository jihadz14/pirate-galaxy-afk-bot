# 🏴‍☠️ Pirate Galaxy AFK Bot

Bot automatizado para Pirate Galaxy con dos versiones: **Original** (Eclip5e) y **Enhanced** (UI gráfica mejorada).

---

## 🚀 Inicio Rápido

### Windows (Recomendado):

1. **Ejecutar versión mejorada (con UI):**
   ```
   Doble click en: scripts\run_enhanced.bat
   ```

2. **Ejecutar versión original (CLI):**
   ```
   Doble click en: scripts\run_original.bat
   ```

### Manual (Python):

```bash
# Versión mejorada (UI gráfica):
python main_enhanced.py

# Versión original (CLI):
python main.py
```

---

## 📦 Instalación

### 1. Instalar Python 3.8+
Descarga desde: https://www.python.org/downloads/

### 2. Instalar Tesseract OCR
Descarga desde: https://github.com/UB-Mannheim/tesseract/wiki

### 3. Instalar dependencias

**Básicas (ambas versiones):**
```bash
pip install pyautogui keyboard colorama requests pytesseract opencv-python pywin32
```

**Extra para versión Enhanced:**
```bash
pip install PyQt5 PyQtChart
```

**O ejecutar:**
```
scripts\install_dependencies.bat
```

---

## ⚙️ Configuración

Edita el archivo: **`config/settings.json`**

```json
{
    "tesseract": "C:/Program Files/Tesseract-OCR/tesseract.exe",
    "healOnHp": 30,
    "defendOnHp": 45,
    "runOnHp": 10,
    "lowEnergy": 1000,
    "skillset": "custom",
    "presets": {
        "storm": ["blaster", "collector", "rocket", "repair", "afterburner", "aimcomp", "perforator", "thermo"],
        "tank": ["blaster", "collector", "repair", "afterburner", "shield", "taunt", "scramble", "aggrobomb"],
        "sniper": ["blaster", "collector", "repair", "afterburner", "sniper", "attackdroid", "orbitalstrike", "dmgbuff"],
        "custom": ["blaster", "collector", "rocket", "repair", "shield", "speedactuator", "sniper", "orbitalstrike"]
    }
}
```

**Habilidades disponibles:**
```
blaster, collector, repair, afterburner, rocket, orbitalstrike, aggrobomb,
mine, stundome, stickybomb, magnettrap, shield, protector, scramble,
aggrobeacon, stun, thermoblast, taunt, sniper, attackdroid, speedactuator,
aimcomp, perforator, dmgbuff, lightningchain
```

---

## 🎮 Uso

### Versión Original (main.py)
```
✅ Bot CLI simple
✅ Detección de enemigos y loot
✅ Sistema de curación automático
✅ Hotkeys: Q (salir), P (pausar)
```

### Versión Enhanced (main_enhanced.py)
```
✨ Todo lo de la versión original +
✅ Interfaz gráfica (PyQt5)
✅ Estadísticas en tiempo real
✅ Gráficas de HP/Energy
✅ Sistema de logging avanzado
✅ OCR mejorado
✅ Energy Loading Mode
✅ Hotkeys: Q (salir), P (pausar), E (energy mode)
```

---

## 🔑 Hotkeys

| Tecla | Acción |
|-------|--------|
| **Q** | Cerrar el bot |
| **P** | Pausar/Reanudar |
| **E** | Energy Loading (solo Enhanced) |

---

## 📁 Estructura del Proyecto

```
pirate-galaxy-afk-bot/
├── main.py                 ⭐ Versión ORIGINAL
├── main_enhanced.py        ⭐ Versión MEJORADA
├── src/                    📂 Código fuente
│   ├── bot/               🤖 Lógica del bot
│   ├── ui/                🎨 Interfaz gráfica
│   ├── detection/         🔍 OCR y detección
│   ├── navigation/        🗺️ Mapas y pathfinding
│   └── utils/             🛠️ Utilidades
├── config/                ⚙️ Configuraciones
├── scripts/               ▶️ Scripts de ejecución
├── tools/                 🔧 Herramientas de debug
├── data/                  📊 Imágenes y mapas
└── logs/                  📝 Logs de sesión
```

📖 **Ver documentación completa:** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## 🛠️ Herramientas Incluidas

### Debug de Energía
```bash
python tools/energy_debug_tool.py
```
Calibra detección de orbes de energía.

### Analizador de Mapas
```bash
python tools/map_analyzer.py
```
Analiza mapas para pathfinding.

### Configurador de Crionita
```bash
python tools/crionita_config_tool.py
```
Configura lectura de crionita para tu resolución.

---

## 📊 Características Avanzadas (Enhanced)

### Tracking automático de:
- ⚔️ Enemigos eliminados
- 📦 Loot recolectado
- 💎 Crionita ganada
- ❤️ Eventos de vida baja
- ⚡ Nivel de energía

### Soporte multi-resolución:
- ✅ 1920x1080 (Full HD)
- ✅ 1366x768 (HD)
- ✅ 1280x720
- ✅ Personalizable

---

## 🐛 Solución de Problemas

### "Python no está instalado"
Instala Python desde: https://www.python.org/downloads/
✅ Marca "Add Python to PATH" durante instalación

### "PyQt5 not found" (solo Enhanced)
```bash
pip install PyQt5 PyQtChart
```

### "Tesseract not found"
1. Instala Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Actualiza ruta en `config/settings.json`:
```json
{
    "tesseract": "C:/Program Files/Tesseract-OCR/tesseract.exe"
}
```

### "No module named 'src'"
Asegúrate de ejecutar desde la raíz del proyecto:
```bash
cd pirate-galaxy-afk-bot
python main_enhanced.py
```

---

## 📜 Créditos

- **Bot Original:** [Eclip5e](https://github.com/Eclip5eLP)
- **Versión Enhanced:** jihadz14
- **Versión:** 0.4.0

---

## ⚠️ Disclaimer

Este bot es solo para fines educativos. Úsalo bajo tu propio riesgo. Los autores no se hacen responsables por cualquier consecuencia derivada de su uso.

---

## 📄 Licencia

Este proyecto mantiene el crédito original de Eclip5e y las mejoras de jihadz14.

---

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:
1. Mantén `main.py` sin modificaciones (versión original)
2. Todas las mejoras van en `main_enhanced.py`
3. Documenta tus cambios
4. Prueba antes de hacer commit

---

## 📞 Soporte

¿Problemas o preguntas?
- 📖 Lee primero: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- 🐛 Reporta bugs en Issues
- 💡 Sugerencias en Discussions

---

**¡Disfruta el bot! 🏴‍☠️⚡**
