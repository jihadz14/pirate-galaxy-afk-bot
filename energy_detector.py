"""
Energy Detector - Detecta orbes de energía en pantalla
Los orbes son esferas azules brillantes que NO aparecen en minimapa
"""

import cv2
import numpy as np
import pyautogui
from pathlib import Path

class EnergyDetector:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        
        # Región de búsqueda (pantalla principal del juego)
        # Ajustar según tu resolución
        screen_width, screen_height = pyautogui.size()
        
        # Región: toda la pantalla excepto UI (bordes)
        self.search_region = {
            'x': 50,
            'y': 50,
            'width': screen_width - 700,  # Excluir panel derecho
            'height': screen_height - 200  # Excluir barra inferior
        }
        
        # Rangos de color para orbes azules brillantes (HSV)
        self.orb_color_lower = np.array([90, 150, 150])   # Azul brillante
        self.orb_color_upper = np.array([130, 255, 255])
        
        # Parámetros de detección
        self.min_orb_area = 50      # Área mínima del orbe
        self.max_orb_area = 3000    # Área máxima del orbe
        self.min_circularity = 0.4  # Qué tan circular debe ser
        
    def detect_energy_orbs(self, debug=False):
        """
        Detectar orbes de energía en pantalla
        Returns: lista de (x, y, radius) de orbes encontrados
        """
        # Capturar región del juego
        screenshot = pyautogui.screenshot(region=(
            self.search_region['x'],
            self.search_region['y'],
            self.search_region['width'],
            self.search_region['height']
        ))
        
        # Convertir a numpy array y HSV
        img_rgb = np.array(screenshot)
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        
        # Crear máscara para color azul brillante
        mask = cv2.inRange(img_hsv, self.orb_color_lower, self.orb_color_upper)
        
        # Limpiar ruido
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        orbs = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filtrar por área
            if not (self.min_orb_area < area < self.max_orb_area):
                continue
            
            # Calcular circularidad
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            # Filtrar por circularidad (debe ser ~circular)
            if circularity < self.min_circularity:
                continue
            
            # Calcular centro y radio
            M = cv2.moments(contour)
            if M['m00'] == 0:
                continue
            
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            
            # Calcular radio aproximado
            radius = int(np.sqrt(area / np.pi))
            
            # Convertir a coordenadas de pantalla
            screen_x = self.search_region['x'] + cx
            screen_y = self.search_region['y'] + cy
            
            orbs.append({
                'x': screen_x,
                'y': screen_y,
                'radius': radius,
                'area': area,
                'circularity': circularity
            })
        
        # Ordenar por distancia desde el centro de la pantalla (más cerca primero)
        screen_center_x = pyautogui.size()[0] // 2
        screen_center_y = pyautogui.size()[1] // 2
        
        orbs.sort(key=lambda orb: 
            np.sqrt((orb['x'] - screen_center_x)**2 + (orb['y'] - screen_center_y)**2)
        )
        
        if debug:
            self._visualize_detection(img_bgr, mask, orbs)
        
        return orbs
    
    def _visualize_detection(self, img, mask, orbs):
        """Guardar imagen de debug con orbes detectados"""
        debug_img = img.copy()
        
        # Dibujar orbes detectados
        for orb in orbs:
            # Convertir a coordenadas relativas
            rel_x = orb['x'] - self.search_region['x']
            rel_y = orb['y'] - self.search_region['y']
            
            # Círculo verde
            cv2.circle(debug_img, (rel_x, rel_y), orb['radius'], (0, 255, 0), 2)
            
            # Centro rojo
            cv2.circle(debug_img, (rel_x, rel_y), 3, (0, 0, 255), -1)
            
            # Texto con info
            text = f"A:{orb['area']:.0f}"
            cv2.putText(debug_img, text, (rel_x + 10, rel_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        # Guardar
        Path('output/energy_detection').mkdir(parents=True, exist_ok=True)
        cv2.imwrite('output/energy_detection/orbs_detected.png', debug_img)
        cv2.imwrite('output/energy_detection/mask.png', mask)
        
        print(f"  💾 Debug guardado: output/energy_detection/")
    
    def find_nearest_orb(self):
        """Encontrar el orbe más cercano al centro de pantalla"""
        orbs = self.detect_energy_orbs()
        
        if orbs:
            return orbs[0]  # Ya están ordenados por distancia
        
        return None


# TESTING
if __name__ == '__main__':
    class MockBot:
        pass
    
    bot = MockBot()
    detector = EnergyDetector(bot)
    
    print("Detectando orbes de energía...")
    orbs = detector.detect_energy_orbs(debug=True)
    
    print(f"\n✓ Orbes encontrados: {len(orbs)}")
    
    for i, orb in enumerate(orbs[:5], 1):
        print(f"  {i}. Posición: ({orb['x']}, {orb['y']}) - Radio: {orb['radius']}px")