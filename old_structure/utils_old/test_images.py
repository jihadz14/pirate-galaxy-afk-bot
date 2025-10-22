import pyautogui
import time

print("Esperando 3 segundos... Abre Pirate Galaxy ahora!")
time.sleep(3)

images = ['minimap', 'energy', 'orbit', 'navmenu', 'chatWindow']

for img in images:
    try:
        result = pyautogui.locateOnScreen(f'./data/images/{img}.png', confidence=0.6)
        if result:
            print(f"✅ {img}.png ENCONTRADO en: {result}")
        else:
            print(f"❌ {img}.png NO encontrado")
    except Exception as e:
        print(f"❌ {img}.png ERROR: {e}")