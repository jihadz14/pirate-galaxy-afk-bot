"""
Analizador de mapa - Encuentra los valores correctos de threshold
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

class MapAnalyzer:
    def __init__(self, map_path):
        self.map_path = map_path
        self.img = cv2.imread(map_path)
        if self.img is None:
            raise FileNotFoundError(f"No se pudo cargar: {map_path}")
        
        print(f"✓ Mapa cargado: {self.img.shape}")
    
    def analyze_colors(self):
        """Analizar distribución de colores"""
        print("\n" + "="*60)
        print("  ANÁLISIS DE COLORES")
        print("="*60 + "\n")
        
        # Convertir a diferentes espacios de color
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        
        # Calcular histogramas
        hist_gray = cv2.calcHist([gray], [0], None, [256], [0, 256])
        
        # Encontrar picos
        peaks = []
        for i in range(1, 255):
            if hist_gray[i] > hist_gray[i-1] and hist_gray[i] > hist_gray[i+1]:
                if hist_gray[i] > 100:  # Threshold mínimo
                    peaks.append((i, hist_gray[i][0]))
        
        peaks.sort(key=lambda x: x[1], reverse=True)
        
        print("📊 Picos en escala de grises (brightness):")
        for i, (value, count) in enumerate(peaks[:5], 1):
            print(f"   {i}. Valor {value} → {int(count)} píxeles")
        
        # Calcular percentiles
        flat_gray = gray.flatten()
        p25 = np.percentile(flat_gray, 25)
        p50 = np.percentile(flat_gray, 50)
        p75 = np.percentile(flat_gray, 75)
        
        print(f"\n📐 Percentiles:")
        print(f"   25% → {p25:.0f}")
        print(f"   50% (mediana) → {p50:.0f}")
        print(f"   75% → {p75:.0f}")
        
        # Sugerir threshold
        # Los caminos son oscuros, las paredes claras
        # El threshold ideal está entre los dos picos principales
        if len(peaks) >= 2:
            suggested_threshold = int((peaks[0][0] + peaks[1][0]) / 2)
        else:
            suggested_threshold = int(p50)
        
        print(f"\n💡 Threshold sugerido: {suggested_threshold}")
        
        return suggested_threshold
    
    def visualize_thresholds(self):
        """Probar múltiples thresholds y visualizar"""
        print("\n" + "="*60)
        print("  PROBANDO DIFERENTES THRESHOLDS")
        print("="*60 + "\n")
        
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        
        # Probar diferentes valores
        thresholds = [50, 70, 90, 110, 130, 150]
        
        output_dir = Path('output/threshold_tests')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        for thresh_val in thresholds:
            # Aplicar threshold
            _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
            
            # Limpiar
            kernel = np.ones((3, 3), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=2)
            
            # Contar píxeles blancos (caminos)
            white_pixels = np.sum(cleaned > 0)
            total_pixels = cleaned.size
            coverage = (white_pixels / total_pixels) * 100
            
            # Guardar
            output_path = output_dir / f'threshold_{thresh_val}.png'
            cv2.imwrite(str(output_path), cleaned)
            
            results.append({
                'threshold': thresh_val,
                'coverage': coverage,
                'path': output_path
            })
            
            print(f"✓ Threshold {thresh_val}: {coverage:.1f}% de cobertura")
        
        # Encontrar el mejor (buscar ~30-50% de cobertura)
        best = min(results, key=lambda x: abs(x['coverage'] - 40))
        
        print(f"\n🎯 Mejor threshold: {best['threshold']} ({best['coverage']:.1f}% cobertura)")
        print(f"   Archivo: {best['path']}")
        
        return best['threshold']
    
    def test_color_ranges(self):
        """Probar detección por rangos de color HSV"""
        print("\n" + "="*60)
        print("  ANÁLISIS POR RANGO DE COLOR (HSV)")
        print("="*60 + "\n")
        
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        
        # Definir rangos de color para caminos (tonos marrones/rojizos oscuros)
        color_ranges = {
            'brown_dark': {
                'lower': np.array([0, 20, 20]),
                'upper': np.array([30, 255, 100])
            },
            'brown_mid': {
                'lower': np.array([0, 30, 30]),
                'upper': np.array([25, 200, 120])
            },
            'all_dark': {
                'lower': np.array([0, 0, 0]),
                'upper': np.array([180, 255, 100])
            }
        }
        
        output_dir = Path('output/color_tests')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        best_result = None
        best_coverage = 0
        
        for name, ranges in color_ranges.items():
            # Crear máscara
            mask = cv2.inRange(hsv, ranges['lower'], ranges['upper'])
            
            # Limpiar
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
            
            # Dilatar para conectar
            kernel_dilate = np.ones((3, 3), np.uint8)
            mask = cv2.dilate(mask, kernel_dilate, iterations=2)
            
            # Calcular cobertura
            coverage = (np.sum(mask > 0) / mask.size) * 100
            
            # Guardar
            output_path = output_dir / f'color_{name}.png'
            cv2.imwrite(str(output_path), mask)
            
            print(f"✓ Rango '{name}': {coverage:.1f}% cobertura")
            
            # Buscar cobertura ~40-60%
            if 35 <= coverage <= 65:
                if abs(coverage - 50) < abs(best_coverage - 50):
                    best_coverage = coverage
                    best_result = (name, mask, ranges)
        
        if best_result:
            print(f"\n🎯 Mejor rango de color: '{best_result[0]}' ({best_coverage:.1f}% cobertura)")
            return best_result[0], best_result[2]
        
        return None, None


# EJECUTAR ANÁLISIS
if __name__ == '__main__':
    print("="*60)
    print("  ANALIZADOR DE MAPA - MANTIS HIVE")
    print("="*60)
    
    analyzer = MapAnalyzer('data/maps/mantis_hive_map.png')
    
    # Análisis 1: Colores
    suggested_threshold = analyzer.analyze_colors()
    
    # Análisis 2: Probar thresholds
    best_threshold = analyzer.visualize_thresholds()
    
    # Análisis 3: Por rango de color
    best_color_name, best_color_range = analyzer.test_color_ranges()
    
    print("\n" + "="*60)
    print("  RESUMEN DE RECOMENDACIONES")
    print("="*60)
    print(f"\n1️⃣ Threshold sugerido (análisis): {suggested_threshold}")
    print(f"2️⃣ Mejor threshold (pruebas): {best_threshold}")
    if best_color_name:
        print(f"3️⃣ Mejor rango de color: {best_color_name}")
        print(f"   Lower: {best_color_range['lower']}")
        print(f"   Upper: {best_color_range['upper']}")
    
    print(f"\n📁 Revisa las imágenes en:")
    print(f"   • output/threshold_tests/")
    print(f"   • output/color_tests/")
    print(f"\n💡 Busca la imagen que mejor separa caminos de paredes\n")