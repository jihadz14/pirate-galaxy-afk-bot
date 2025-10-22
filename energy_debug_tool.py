"""
Herramienta de diagnóstico para lectura de Energía
Ayuda a verificar qué está leyendo el OCR
"""

import pyautogui
import pytesseract
import cv2 as cv
import numpy as np
from PIL import Image, ImageEnhance
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk

class EnergyDebugTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔍 Energy Debug Tool")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        
        # Cargar configuración
        self.load_config()
        
        self.setup_ui()
        
    def load_config(self):
        """Cargar configuración desde settings.json"""
        try:
            possible_paths = [
                Path(__file__).parent / 'core' / 'settings.json',
                Path(__file__).parent.parent / 'core' / 'settings.json',
            ]
            
            settings_path = None
            for path in possible_paths:
                if path.exists():
                    settings_path = path
                    break
            
            if settings_path:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                screen_width, screen_height = pyautogui.size()
                resolution_key = f"{screen_width}x{screen_height}"
                
                # Cargar región de energía
                if 'stats_config' in settings and 'energy_region' in settings['stats_config']:
                    energy_regions = settings['stats_config']['energy_region']
                    if resolution_key in energy_regions:
                        self.energy_region = tuple(energy_regions[resolution_key])
                    else:
                        self.energy_region = tuple(energy_regions.get('default', [100, 100, 120, 25]))
                else:
                    self.energy_region = (100, 100, 120, 25)
                
                self.tesseract_path = settings.get('tesseract', 'C:/Program Files/Tesseract-OCR/tesseract.exe')
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
            else:
                self.energy_region = (100, 100, 120, 25)
                self.tesseract_path = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
                
        except Exception as e:
            print(f"Error cargando config: {e}")
            self.energy_region = (100, 100, 120, 25)
            self.tesseract_path = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
    
    def setup_ui(self):
        """Configurar interfaz"""
        # Header
        header = tk.Frame(self.root, bg='#1e1e2e', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="🔍 Energy OCR Diagnostic Tool",
            font=("Arial", 16, "bold"),
            bg='#1e1e2e',
            fg='#89dceb'
        )
        title.pack(pady=15)
        
        # Info Frame
        info_frame = tk.LabelFrame(
            self.root,
            text="📍 Current Configuration",
            font=("Arial", 10, "bold"),
            bg='#313244',
            fg='#89b4fa',
            padx=15,
            pady=10
        )
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        region_text = f"Energy Region: {self.energy_region}\n"
        region_text += f"Format: [x={self.energy_region[0]}, y={self.energy_region[1]}, "
        region_text += f"width={self.energy_region[2]}, height={self.energy_region[3]}]"
        
        region_label = tk.Label(
            info_frame,
            text=region_text,
            bg='#313244',
            fg='#cdd6f4',
            font=("Courier", 9),
            justify=tk.LEFT
        )
        region_label.pack()
        
        # Capture Button
        capture_btn = tk.Button(
            self.root,
            text="📸 Capture & Analyze Energy",
            command=self.capture_and_analyze,
            font=("Arial", 12, "bold"),
            bg='#89dceb',
            fg='#1e1e2e',
            padx=30,
            pady=15,
            relief=tk.FLAT,
            cursor="hand2"
        )
        capture_btn.pack(pady=10)
        
        # Results Frame
        results_frame = tk.LabelFrame(
            self.root,
            text="🔬 Analysis Results",
            font=("Arial", 10, "bold"),
            bg='#313244',
            fg='#a6e3a1',
            padx=15,
            pady=10
        )
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Imagen original
        original_label = tk.Label(results_frame, text="Original Capture:", bg='#313244', fg='#cdd6f4')
        original_label.pack(pady=(5, 0))
        
        self.original_image_label = tk.Label(results_frame, bg='#1e1e2e')
        self.original_image_label.pack(pady=5)
        
        # Imagen procesada
        processed_label = tk.Label(results_frame, text="Processed (Binary):", bg='#313244', fg='#cdd6f4')
        processed_label.pack(pady=(10, 0))
        
        self.processed_image_label = tk.Label(results_frame, bg='#1e1e2e')
        self.processed_image_label.pack(pady=5)
        
        # Resultados de OCR
        ocr_label = tk.Label(results_frame, text="OCR Results:", bg='#313244', fg='#cdd6f4', font=("Arial", 10, "bold"))
        ocr_label.pack(pady=(10, 0))
        
        self.ocr_results_text = tk.Text(
            results_frame,
            height=8,
            bg='#1e1e2e',
            fg='#cdd6f4',
            font=("Courier", 10),
            padx=10,
            pady=10
        )
        self.ocr_results_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Botón de reconfiguración
        reconfig_btn = tk.Button(
            self.root,
            text="⚙️ Reconfigure Energy Region",
            command=self.open_region_config,
            font=("Arial", 10, "bold"),
            bg='#f9e2af',
            fg='#1e1e2e',
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        reconfig_btn.pack(pady=10)
    
    def capture_and_analyze(self):
        """Capturar y analizar región de energía"""
        try:
            # Capturar screenshot
            screenshot = pyautogui.screenshot(region=self.energy_region)
            
            # Mostrar imagen original (escalada)
            display_img = screenshot.copy()
            display_img = display_img.resize((300, 100), Image.LANCZOS)
            photo = ImageTk.PhotoImage(display_img)
            self.original_image_label.config(image=photo)
            self.original_image_label.image = photo
            
            # Procesar imagen
            img_array = np.array(screenshot)
            gray = cv.cvtColor(img_array, cv.COLOR_RGB2GRAY)
            
            # Aplicar threshold
            _, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
            
            # Invertir si es necesario
            if np.mean(binary) < 127:
                binary = cv.bitwise_not(binary)
            
            # Mostrar imagen procesada
            binary_pil = Image.fromarray(binary)
            binary_display = binary_pil.resize((300, 100), Image.LANCZOS)
            binary_photo = ImageTk.PhotoImage(binary_display)
            self.processed_image_label.config(image=binary_photo)
            self.processed_image_label.image = binary_photo
            
            # Limpiar resultados anteriores
            self.ocr_results_text.delete(1.0, tk.END)
            
            # Intentar múltiples configuraciones de OCR
            self.ocr_results_text.insert(tk.END, "🔍 Testing OCR configurations...\n\n", "header")
            
            configs = [
                ('Config 1 (PSM 7, digits only)', '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'),
                ('Config 2 (PSM 8, digits only)', '--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789'),
                ('Config 3 (PSM 6, digits only)', '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789'),
                ('Config 4 (PSM 7, digits+comma)', '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789,'),
                ('Config 5 (Default)', '-c tessedit_char_whitelist=0123456789,'),
            ]
            
            best_result = None
            best_config = None
            
            for config_name, config_str in configs:
                try:
                    result = pytesseract.image_to_string(binary_pil, config=config_str)
                    result_clean = result.replace('\n', '').replace('\x0c', '').replace(',', '').replace('.', '').replace(' ', '').strip()
                    
                    self.ocr_results_text.insert(tk.END, f"• {config_name}:\n", "config")
                    self.ocr_results_text.insert(tk.END, f"  Raw: '{result}'\n", "raw")
                    self.ocr_results_text.insert(tk.END, f"  Clean: '{result_clean}'\n", "clean")
                    
                    if result_clean and result_clean.isdigit():
                        value = int(result_clean)
                        self.ocr_results_text.insert(tk.END, f"  ✅ Integer: {value:,}\n\n", "success")
                        if best_result is None or (100 <= value <= 50000):
                            best_result = value
                            best_config = config_name
                    else:
                        self.ocr_results_text.insert(tk.END, f"  ❌ Not a valid number\n\n", "error")
                        
                except Exception as e:
                    self.ocr_results_text.insert(tk.END, f"  ❌ Error: {e}\n\n", "error")
            
            # Mostrar mejor resultado
            self.ocr_results_text.insert(tk.END, "\n" + "="*50 + "\n", "separator")
            if best_result:
                self.ocr_results_text.insert(tk.END, f"✨ BEST RESULT: {best_result:,}\n", "best")
                self.ocr_results_text.insert(tk.END, f"   Using: {best_config}\n", "best")
            else:
                self.ocr_results_text.insert(tk.END, "⚠️  NO VALID RESULTS\n", "warning")
                self.ocr_results_text.insert(tk.END, "   Try reconfiguring the region\n", "warning")
            
            # Aplicar colores
            self.ocr_results_text.tag_config("header", foreground="#89dceb", font=("Courier", 10, "bold"))
            self.ocr_results_text.tag_config("config", foreground="#f9e2af")
            self.ocr_results_text.tag_config("raw", foreground="#9399b2")
            self.ocr_results_text.tag_config("clean", foreground="#cdd6f4")
            self.ocr_results_text.tag_config("success", foreground="#a6e3a1", font=("Courier", 10, "bold"))
            self.ocr_results_text.tag_config("error", foreground="#f38ba8")
            self.ocr_results_text.tag_config("warning", foreground="#f9e2af", font=("Courier", 10, "bold"))
            self.ocr_results_text.tag_config("best", foreground="#a6e3a1", font=("Courier", 11, "bold"))
            self.ocr_results_text.tag_config("separator", foreground="#585b70")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error capturing/analyzing: {e}")
    
    def open_region_config(self):
        """Abrir herramienta de configuración"""
        try:
            import subprocess
            import sys
            
            config_tool_path = Path(__file__).parent / 'crionita_config_tool.py'
            
            if config_tool_path.exists():
                if sys.platform == 'win32':
                    subprocess.Popen([sys.executable, str(config_tool_path)], 
                                   creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    subprocess.Popen([sys.executable, str(config_tool_path)])
                
                messagebox.showinfo(
                    "Config Tool Opened",
                    "The region configuration tool has been opened.\n\n"
                    "Configure the Energy region and save.\n"
                    "Then restart this debug tool to test the new region."
                )
            else:
                messagebox.showerror(
                    "Tool Not Found",
                    f"Configuration tool not found at:\n{config_tool_path}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Error opening config tool: {e}")
    
    def run(self):
        """Ejecutar aplicación"""
        self.root.mainloop()


if __name__ == '__main__':
    print("=" * 60)
    print("  Energy OCR Diagnostic Tool")
    print("=" * 60)
    print("\nThis tool will help you diagnose energy reading issues.")
    print("It will show you what the OCR is seeing and reading.\n")
    print("=" * 60 + "\n")
    
    try:
        app = EnergyDebugTool()
        app.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
