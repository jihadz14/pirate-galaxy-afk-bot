"""
Position Tracker - Detecta la posición del jugador
Busca la flecha blanca en minimapa y mapa grande
"""

import cv2
import numpy as np
import pyautogui
from pathlib import Path

class PositionTracker:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        
        # Color de la flecha del jugador (blanco)
        self.arrow_color_lower = np.array([200, 200, 200])  # RGB
        self.arrow_color_upper = np.array([255, 255, 255])
        
        # Regiones
        self.minimap_region = None
        self.big_map_region = None
        
    def find_minimap(self):
        """Encontrar región del minimapa"""
        find = self.bot.search('minimap', 0.7)
        
        if find:
            # El minimapa es circular, aproximadamente
            self.minimap_region = {
                'x': int(find.left + 25),
                'y': int(find.top - 100),
                'width': 115,
                'height': 115,
                'center_x': int(find.left + 25 + 57),
                'center_y': int(find.top - 100 + 57)
            }
            return self.minimap_region
        return None
    
    def find_big_map(self):
        """
        Encontrar región del mapa grande en pantalla
        Basado en tu screenshot, está en la esquina superior derecha
        """
        # Buscar esquina del panel (ajustar según tu resolución)
        screen_width, screen_height = pyautogui.size()
        
        # Aproximación: mapa grande está en la esquina superior derecha
        # Ajustar estos valores según tu resolución exacta
        self.big_map_region = {
            'x': screen_width - 400,  # 400px desde la derecha
            'y': 80,  # 80px desde arriba
            'width': 380,
            'height': 380
        }
        
        return self.big_map_region
    
    def detect_arrow_in_minimap(self):
        """
        Detectar flecha blanca en el minimapa
        Retorna coordenadas relativas al centro del minimapa
        """
        if not self.minimap_region:
            self.find_minimap()
        
        # Capturar minimapa
        screenshot = pyautogui.screenshot(region=(
            self.minimap_region['x'],
            self.minimap_region['y'],
            self.minimap_region['width'],
            self.minimap_region['height']
        ))
        
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # Detectar píxeles blancos (flecha)
        mask = cv2.inRange(img, self.arrow_color_lower, self.arrow_color_upper)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Tomar el contorno más grande (probablemente la flecha)
            largest = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest)
            
            if M['m00'] > 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                
                # Coordenadas relativas al centro del minimapa
                rel_x = cx - 57  # 57 es el radio
                rel_y = cy - 57
                
                return {
                    'absolute': (cx, cy),
                    'relative': (rel_x, rel_y),
                    'screen': (
                        self.minimap_region['x'] + cx,
                        self.minimap_region['y'] + cy
                    )
                }
        
        # Si no se detecta, asumir centro
        return {
            'absolute': (57, 57),
            'relative': (0, 0),
            'screen': (
                self.minimap_region['center_x'],
                self.minimap_region['center_y']
            )
        }
    
    def detect_arrow_in_big_map(self):
        """
        Detectar flecha blanca en el mapa grande
        Retorna coordenadas absolutas del mapa
        """
        if not self.big_map_region:
            self.find_big_map()
        
        # Capturar mapa grande
        screenshot = pyautogui.screenshot(region=(
            self.big_map_region['x'],
            self.big_map_region['y'],
            self.big_map_region['width'],
            self.big_map_region['height']
        ))
        
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # Detectar flecha blanca
        mask = cv2.inRange(img, self.arrow_color_lower, self.arrow_color_upper)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest)
            
            if M['m00'] > 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                
                return {
                    'map_coords': (cx, cy),
                    'screen_coords': (
                        self.big_map_region['x'] + cx,
                        self.big_map_region['y'] + cy
                    )
                }
        
        return None


# TEST
if __name__ == '__main__':
    class MockBot:
        def search(self, img, conf=0.7):
            # Mock para testing
            class Box:
                left = 100
                top = 100
            return Box()
    
    bot = MockBot()
    tracker = PositionTracker(bot)
    
    print("Buscando minimapa...")
    minimap = tracker.find_minimap()
    print(f"Minimapa: {minimap}")
    
    print("\nDetectando posición en minimapa...")
    pos = tracker.detect_arrow_in_minimap()
    print(f"Posición: {pos}")