import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

import pyautogui
import pytesseract
from PIL import Image, ImageDraw
import cv2
import numpy as np
from time import sleep

pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

print("═══════════════════════════════════════")
print("   DETECTOR DE ENERGÍA - CORREGIDO")
print("═══════════════════════════════════════")
print("\n1. Abre Pirate Galaxy")
print("2. Asegúrate de ver: [Número] [Icono Azul]")
print("3. Espera 5 segundos...\n")
sleep(5)

# Buscar icono
print("Buscando icono energy.png...")
find = None

for confidence in [0.9, 0.8, 0.7, 0.6, 0.5]:
    try:
        find = pyautogui.locateOnScreen('./data/images/energy.png', confidence=confidence)
        if find:
            print(f"✓ Icono encontrado con confidence={confidence}")
            print(f"  Posición: left={find.left}, top={find.top}")
            break
    except:
        pass

if not find:
    print("\n✗ NO SE ENCONTRÓ energy.png")
    print("\nEjecuta primero: python capture_energy_icon.py")
    input("\nPresiona Enter para salir...")
    sys.exit(1)

# Capturar pantalla COMPLETA alrededor para visualización
print("\nCapturando región amplia para análisis...")
wide_screenshot = pyautogui.screenshot(
    region=(
        int(find.left - 250),  # 250px a la izquierda
        int(find.top - 50),    # 50px arriba
        400,                   # Ancho total: 400px
        100                    # Alto: 100px
    )
)

# Dibujar marcadores visuales
draw = ImageDraw.Draw(wide_screenshot)

# Rectángulo ROJO = donde está el icono
icon_x_in_capture = 250  # Offset en la captura
icon_y_in_capture = 50
draw.rectangle(
    [icon_x_in_capture, icon_y_in_capture, 
     icon_x_in_capture + find.width, icon_y_in_capture + find.height],
    outline='red',
    width=3
)

# Línea VERDE = área de captura a la IZQUIERDA (típica)
left_area_x = icon_x_in_capture - 100  # 100px a la izquierda
draw.rectangle(
    [left_area_x, icon_y_in_capture, icon_x_in_capture, icon_y_in_capture + 20],
    outline='green',
    width=2
)

# Línea AZUL = área de captura a la DERECHA (alternativa)
right_area_x = icon_x_in_capture + find.width
draw.rectangle(
    [right_area_x, icon_y_in_capture, right_area_x + 100, icon_y_in_capture + 20],
    outline='blue',
    width=2
)

wide_screenshot.save('energy_layout_analysis.png')
print("✓ Guardado: energy_layout_analysis.png")

print("\n═══════════════════════════════════════")
print("   ANÁLISIS VISUAL")
print("═══════════════════════════════════════")
print("\n📸 Abre: energy_layout_analysis.png")
print("\n   🔴 ROJO = Icono detectado")
print("   🟢 VERDE = Captura a la IZQUIERDA")
print("   🔵 AZUL = Captura a la DERECHA")
print("\n¿El NÚMERO está dentro del rectángulo VERDE o AZUL?")
print("\n   a) Está en el VERDE (izquierda del icono)")
print("   b) Está en el AZUL (derecha del icono)")
print("   c) NO está en ninguno (está más lejos)")
print("\nRespuesta (a/b/c): ", end='')

position = input().lower()

# Configuraciones corregidas
if position == 'a':  # IZQUIERDA
    print("\n✓ Configurando para IZQUIERDA del icono")
    configs = [
        {"name": "80px izq", "offset_x": 80, "offset_y": 0, "width": 80, "height": 20},
        {"name": "100px izq", "offset_x": 100, "offset_y": 0, "width": 100, "height": 20},
        {"name": "120px izq", "offset_x": 120, "offset_y": -2, "width": 120, "height": 24},
        {"name": "150px izq", "offset_x": 150, "offset_y": -5, "width": 150, "height": 30},
    ]
    direction = "IZQUIERDA"
    
elif position == 'b':  # DERECHA
    print("\n✓ Configurando para DERECHA del icono")
    configs = [
        {"name": "80px der", "offset_x": -find.width - 80, "offset_y": 0, "width": 80, "height": 20},
        {"name": "100px der", "offset_x": -find.width - 100, "offset_y": 0, "width": 100, "height": 20},
        {"name": "120px der", "offset_x": -find.width - 120, "offset_y": -2, "width": 120, "height": 24},
    ]
    direction = "DERECHA"
    
else:  # MÁS LEJOS
    print("\n⚠️ El número está MÁS LEJOS")
    print("¿Cuántos píxeles aproximadamente?")
    print("(Mira energy_layout_analysis.png y estima)")
    print("Distancia en píxeles (ej: 150, 200, 250): ", end='')
    
    distance = int(input().strip())
    
    configs = [
        {"name": f"{distance}px izq", "offset_x": distance, "offset_y": 0, "width": distance, "height": 20},
        {"name": f"{distance}px izq alto", "offset_x": distance, "offset_y": -5, "width": distance, "height": 30},
    ]
    direction = "IZQUIERDA (lejos)"

print("\n═══════════════════════════════════════")
print(f"   PROBANDO CAPTURAS A LA {direction}")
print("═══════════════════════════════════════\n")

best_result = None
best_config_idx = None

for i, cfg in enumerate(configs):
    print(f"\n[Config {i+1}] {cfg['name']}")
    print(f"  Region: left-{cfg['offset_x']}, top+{cfg['offset_y']}, {cfg['width']}x{cfg['height']}")
    
    try:
        # CAPTURA CORREGIDA
        capture_left = int(find.left - cfg['offset_x'])
        capture_top = int(find.top + cfg['offset_y'])
        
        print(f"  Coordenadas: ({capture_left}, {capture_top})")
        
        screenshot = pyautogui.screenshot(
            region=(
                capture_left,
                capture_top,
                cfg['width'],
                cfg['height']
            )
        )
        
        # Guardar
        filename = f'energy_capture_{i+1}.png'
        screenshot.save(filename)
        print(f"  💾 Guardado: {filename}")
        
        # Preprocesar
        img_array = np.array(screenshot)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        if np.mean(binary) < 127:
            binary = cv2.bitwise_not(binary)
        
        processed_filename = f'energy_capture_{i+1}_processed.png'
        cv2.imwrite(processed_filename, binary)
        print(f"  💾 Procesado: {processed_filename}")
        
        # OCR con múltiples métodos
        results = []
        
        # Método 1: Solo números
        try:
            r1 = pytesseract.image_to_string(
                Image.fromarray(binary),
                config='--psm 7 -c tessedit_char_whitelist=0123456789,'
            ).replace('\n', '').replace(',', '').replace(' ', '').strip()
            if r1:
                results.append(("M1", r1))
        except:
            pass
        
        # Método 2: Alternativo
        try:
            r2 = pytesseract.image_to_string(
                screenshot,
                config='--psm 6 -c tessedit_char_whitelist=0123456789'
            ).replace('\n', '').replace(',', '').replace(' ', '').strip()
            if r2:
                results.append(("M2", r2))
        except:
            pass
        
        # Método 3: Sin filtro
        try:
            r3 = pytesseract.image_to_string(Image.fromarray(binary))
            r3_clean = ''.join(filter(str.isdigit, r3))
            if r3_clean:
                results.append(("M3", r3_clean))
        except:
            pass
        
        if results:
            print(f"  📊 Resultados OCR:")
            for method, result in results:
                print(f"     {method}: '{result}'")
                
                if result and result.isdigit():
                    num = int(result)
                    if 1000 <= num <= 30000:
                        print(f"     ✅ Válido: {num:,}")
                        if best_result is None or abs(num - 22000) < abs(best_result - 22000):
                            best_result = num
                            best_config_idx = i
                    else:
                        print(f"     ⚠️ Fuera de rango: {num:,}")
        else:
            print(f"  ✗ No se pudo leer")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n═══════════════════════════════════════")
print("   RESULTADO FINAL")
print("═══════════════════════════════════════\n")

if best_result:
    cfg = configs[best_config_idx]
    print(f"✅ CONFIGURACIÓN ÓPTIMA:")
    print(f"   Energía detectada: {best_result:,}")
    print(f"   Config: {cfg['name']}")
    print(f"\n   Verifica: energy_capture_{best_config_idx + 1}.png")
    print(f"\n🔧 COPIA ESTO EN bot.py (línea ~304):")
    print(f"")
    print(f"   offset_x = {cfg['offset_x']}")
    print(f"   offset_y = {cfg['offset_y']}")
    print(f"   width = {cfg['width']}")
    print(f"   height = {cfg['height']}")
    print(f"")
else:
    print("✗ NO SE DETECTÓ ENERGÍA")
    print("\n   Revisa las capturas:")
    for i in range(len(configs)):
        print(f"   - energy_capture_{i+1}.png")
    print("\n   ¿Se ve el número en alguna?")
    print("   Si SÍ → Usa esa config manualmente")
    print("   Si NO → Ajusta la distancia manualmente")

print("\n═══════════════════════════════════════")
input("\nPresiona Enter para salir...")