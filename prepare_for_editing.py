"""
Preparar imagen para edicion manual
"""

import cv2
import numpy as np
from pathlib import Path

# Cargar mapa
img = cv2.imread('data/maps/mantis_hive_map.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Threshold
_, binary = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY_INV)

# Invertir colores para Paint (negro = caminos, blanco = paredes)
binary_inverted = cv2.bitwise_not(binary)

# Guardar para edicion
cv2.imwrite('output/map_for_editing.png', binary)
cv2.imwrite('output/map_for_editing_inverted.png', binary_inverted)

print("Archivos creados:")
print("  • output/map_for_editing.png (blanco=caminos)")
print("  • output/map_for_editing_inverted.png (negro=caminos)")
print("\nElige cual prefieres editar en Paint")