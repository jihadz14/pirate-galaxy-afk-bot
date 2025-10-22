#!/usr/bin/env python3
"""
Script de prueba rápida para verificar imports
Sin ejecutar el bot completo
"""

import sys
import os

# Agregar el directorio raíz del proyecto al path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

print("╔═══════════════════════════════════════╗")
print("║   PRUEBA RÁPIDA DE IMPORTS           ║")
print("╚═══════════════════════════════════════╝")
print()

errors = []
warnings = []

# Test 1: Import básicos de Python
print("[1/7] Verificando módulos estándar de Python...")
try:
    import json
    import time
    from pathlib import Path
    print("✓ Módulos estándar OK")
except Exception as e:
    errors.append(f"Módulos estándar: {e}")
    print(f"✗ Error: {e}")

# Test 2: Import del bot core
print("\n[2/7] Verificando src.bot...")
try:
    from src.bot import PGBot, BotState, Importer
    print("✓ src.bot importado correctamente")
    print(f"  - PGBot: {PGBot.__name__}")
    print(f"  - BotState: INIT={BotState.INIT}, FARMING={BotState.FARMING}")
except Exception as e:
    errors.append(f"src.bot: {e}")
    print(f"✗ Error: {e}")

# Test 3: Import de UI (puede fallar si no hay PyQt5)
print("\n[3/7] Verificando src.ui...")
try:
    from src.ui import BotUIWindow, EnergyOverlay
    print("✓ src.ui importado correctamente")
except ImportError as e:
    warnings.append(f"src.ui: PyQt5 no instalado - versión Enhanced no disponible")
    print(f"⚠ PyQt5 no instalado (solo afecta versión Enhanced)")
except Exception as e:
    errors.append(f"src.ui: {e}")
    print(f"✗ Error: {e}")

# Test 4: Import de detection
print("\n[4/7] Verificando src.detection...")
try:
    from src.detection import EnergyDetector, PositionTracker
    print("✓ src.detection importado correctamente")
except Exception as e:
    errors.append(f"src.detection: {e}")
    print(f"✗ Error: {e}")

# Test 5: Import de navigation
print("\n[5/7] Verificando src.navigation...")
try:
    from src.navigation import MapProcessorFinal
    print("✓ src.navigation importado correctamente")
except Exception as e:
    errors.append(f"src.navigation: {e}")
    print(f"✗ Error: {e}")

# Test 6: Import de utils
print("\n[6/7] Verificando src.utils...")
try:
    from src.utils import BotLogger
    print("✓ src.utils importado correctamente")
except ImportError:
    warnings.append("src.utils: BotLogger opcional no disponible")
    print("⚠ BotLogger opcional no disponible")
except Exception as e:
    errors.append(f"src.utils: {e}")
    print(f"✗ Error: {e}")

# Test 7: Verificar archivos de configuración
print("\n[7/7] Verificando archivos de configuración...")
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json')
if os.path.exists(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✓ config/settings.json válido")
        print(f"  - Skillset: {config.get('skillset', 'N/A')}")
        print(f"  - healOnHp: {config.get('healOnHp', 'N/A')}")
    except Exception as e:
        errors.append(f"config/settings.json: {e}")
        print(f"✗ Error parseando JSON: {e}")
else:
    errors.append("config/settings.json no encontrado")
    print("✗ config/settings.json NO existe")

# Resumen
print("\n" + "="*50)
print("RESUMEN DE PRUEBAS")
print("="*50)

if len(errors) == 0 and len(warnings) == 0:
    print("\n✅ TODAS LAS PRUEBAS PASARON")
    print("\nTu bot está listo para ejecutar!")
    print("\nEjecuta:")
    print("  - python main.py (versión original)")
    print("  - python main_enhanced.py (versión mejorada)")
    sys.exit(0)
elif len(errors) == 0:
    print(f"\n✅ PRUEBAS PASADAS con {len(warnings)} advertencia(s)")
    print("\nAdvertencias:")
    for w in warnings:
        print(f"  ⚠ {w}")
    print("\nEl bot funcionará, pero algunas features pueden no estar disponibles.")
    sys.exit(0)
else:
    print(f"\n❌ {len(errors)} ERROR(ES) ENCONTRADO(S)")
    print("\nErrores:")
    for e in errors:
        print(f"  ✗ {e}")

    if len(warnings) > 0:
        print(f"\nAdvertencias adicionales:")
        for w in warnings:
            print(f"  ⚠ {w}")

    print("\nPor favor, instala las dependencias faltantes:")
    print("  pip install pyautogui keyboard colorama opencv-python pytesseract pywin32")
    print("  pip install PyQt5 PyQtChart  # Para versión Enhanced")
    sys.exit(1)
