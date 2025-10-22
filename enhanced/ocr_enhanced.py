###################
# Enhanced OCR    #
###################

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

class EnhancedOCR:
    
    @staticmethod
    def preprocess_image(image, method='standard'):
        """Pre-procesar imagen para mejor OCR"""
        
        # Convertir PIL a numpy si es necesario
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
        
        # Convertir a escala de grises
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        if method == 'standard':
            # Threshold simple
            _, processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
        elif method == 'adaptive':
            # Threshold adaptativo
            processed = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
        elif method == 'contrast':
            # Aumentar contraste
            pil_img = Image.fromarray(gray)
            enhancer = ImageEnhance.Contrast(pil_img)
            enhanced = enhancer.enhance(2.0)
            processed = np.array(enhanced)
            _, processed = cv2.threshold(processed, 127, 255, cv2.THRESH_BINARY)
            
        elif method == 'denoise':
            # Reducir ruido
            processed = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            _, processed = cv2.threshold(processed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return Image.fromarray(processed)
    
    @staticmethod
    def read_number_advanced(image, max_attempts=3):
        """
        Leer número con múltiples intentos y validación
        """
        methods = ['standard', 'adaptive', 'contrast', 'denoise']
        results = []
        
        for i, method in enumerate(methods[:max_attempts]):
            try:
                # Pre-procesar
                processed = EnhancedOCR.preprocess_image(image, method)
                
                # Intentar leer
                text = pytesseract.image_to_string(
                    processed,
                    config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
                )
                
                # Limpiar resultado
                text = ''.join(filter(str.isdigit, text))
                
                if text:
                    num = int(text)
                    results.append((num, method))
                    
            except:
                continue
        
        if not results:
            return None
        
        # Si hay consenso entre métodos, usar ese valor
        if len(results) >= 2:
            nums = [r[0] for r in results]
            # Verificar si hay valores similares
            for num in nums:
                count = sum(1 for n in nums if abs(n - num) < num * 0.1)  # 10% tolerance
                if count >= 2:
                    return num
        
        # Retornar el más común o el primero
        return results[0][0]
    
    @staticmethod
    def read_hp(screenshot_region):
        """Leer HP con validación mejorada"""
        try:
            # Duplicar imagen horizontalmente (como en bot original)
            width, height = screenshot_region.size
            newImg = Image.new('RGB', (2*width, height), (250,250,250))
            newImg.paste(screenshot_region, (0,0))
            newImg.paste(screenshot_region, (width,0))
            
            # Leer con método avanzado
            hp = EnhancedOCR.read_number_advanced(newImg)
            
            if hp is None:
                return None
            
            # Tomar primera mitad (por duplicación)
            hp_str = str(hp)
            hp = int(hp_str[0:len(hp_str)//2])
            
            # Validar rango (1-100)
            if 1 <= hp <= 100 and hp not in [1, 2]:  # Ignorar 1 y 2 (falsos positivos)
                return hp
            
            return None
            
        except:
            return None
    
    @staticmethod
    def read_energy(screenshot_region):
        """Leer energía con validación mejorada"""
        try:
            # Leer con método avanzado
            energy = EnhancedOCR.read_number_advanced(screenshot_region)
            
            if energy is None:
                return None
            
            # Validar rango razonable (100-99999)
            if 100 <= energy <= 99999:
                return energy
            
            return None
            
        except:
            return None