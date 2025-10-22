import sys
import subprocess

class Importer:

    @staticmethod
    def verifyLibs(required):
        """Verificar e instalar librerías faltantes"""
        
        # Mapeo de nombres de paquetes a nombres de importación
        package_map = {
            'opencv-python': 'cv2',
            'pywin32': 'win32api',
            'PyQt5': 'PyQt5.QtWidgets',
            'PyQtChart': 'PyQt5.QtChart',
            'pillow': 'PIL'
        }
        
        missing = []
        
        # Verificar qué librerías faltan
        for package in required:
            import_name = package_map.get(package, package.replace('-', '_'))
            
            try:
                # Intentar importar
                if '.' in import_name:
                    # Importación con submódulo (ej: PyQt5.QtWidgets)
                    parts = import_name.split('.')
                    mod = __import__(parts[0])
                    for part in parts[1:]:
                        mod = getattr(mod, part)
                else:
                    __import__(import_name)
            except (ImportError, AttributeError):
                missing.append(package)
        
        # Si hay librerías faltantes
        if missing:
            print(f"\nFaltan las siguientes librerías: {missing}")
            print("Por favor, instálalas manualmente con:")
            print(f"pip install {' '.join(missing)}")
            sys.exit(1)