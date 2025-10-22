"""
Herramienta para configurar posiciones de lectura en pantalla
Soporta: Crionita, Energía, y otras regiones futuras
"""

import pyautogui
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import ImageGrab, ImageTk
import json
from pathlib import Path

class MultiRegionConfigTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Configurador de Regiones - Pirate Galaxy Bot")
        self.root.geometry("600x650")
        self.root.resizable(False, False)
        
        # Configuraciones disponibles
        self.regions = {
            'crionita': {
                'name': 'Crionita',
                'description': 'Número de Crionita en pantalla',
                'color': '#89dceb',
                'configured': False,
                'coords': None
            },
            'energy': {
                'name': 'Energía',
                'description': 'Valor de energía del jugador',
                'color': '#89b4fa',
                'configured': False,
                'coords': None
            }
        }
        
        self.current_region = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        
        # Cargar configuración existente
        self.load_existing_config()
        
        self.setup_ui()
        
    def load_existing_config(self):
        """Cargar configuración existente desde settings.json"""
        try:
            # Buscar settings.json en varias ubicaciones posibles
            possible_paths = [
                Path(__file__).parent / 'core' / 'settings.json',  # ui/core/settings.json
                Path(__file__).parent.parent / 'core' / 'settings.json',  # ../core/settings.json
                Path(__file__).parent / 'settings.json',  # ui/settings.json
                Path(__file__).parent.parent / 'settings.json',  # ../settings.json
            ]
            
            settings_path = None
            for path in possible_paths:
                if path.exists():
                    settings_path = path
                    break
            
            if not settings_path:
                print("⚠️ Warning: settings.json not found in any expected location")
                return
            
            print(f"✅ Found settings.json at: {settings_path}")
            
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            screen_width, screen_height = pyautogui.size()
            resolution_key = f"{screen_width}x{screen_height}"
            
            # Verificar si hay configuración para esta resolución
            if 'stats_config' in settings:
                config = settings['stats_config']
                
                # Crionita
                if 'crionita_region' in config:
                    if resolution_key in config['crionita_region']:
                        self.regions['crionita']['configured'] = True
                        self.regions['crionita']['coords'] = config['crionita_region'][resolution_key]
                
                # Energía
                if 'energy_region' in config:
                    if resolution_key in config['energy_region']:
                        self.regions['energy']['configured'] = True
                        self.regions['energy']['coords'] = config['energy_region'][resolution_key]
                        
        except Exception as e:
            print(f"Error cargando configuración: {e}")
        
    def setup_ui(self):
        """Configurar interfaz"""
        # Header
        header = tk.Frame(self.root, bg='#1e1e2e', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="⚙️ Configurador de Regiones",
            font=("Arial", 18, "bold"),
            bg='#1e1e2e',
            fg='#cdd6f4'
        )
        title.pack(pady=10)
        
        subtitle = tk.Label(
            header,
            text="Configura las posiciones de lectura para tu resolución",
            font=("Arial", 10),
            bg='#1e1e2e',
            fg='#9399b2'
        )
        subtitle.pack()
        
        # Información de resolución
        screen_width, screen_height = pyautogui.size()
        resolution_frame = tk.Frame(self.root, bg='#313244', height=50)
        resolution_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        resolution_frame.pack_propagate(False)
        
        resolution_label = tk.Label(
            resolution_frame,
            text=f"🖥️  Resolución actual: {screen_width}x{screen_height}",
            font=("Arial", 11, "bold"),
            bg='#313244',
            fg='#f9e2af'
        )
        resolution_label.pack(pady=13)
        
        # Frame principal con scroll
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas con scrollbar
        canvas = tk.Canvas(main_frame, bg='#1e1e2e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1e1e2e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Crear cards para cada región
        self.region_cards = {}
        for region_key, region_data in self.regions.items():
            card = self.create_region_card(scrollable_frame, region_key, region_data)
            self.region_cards[region_key] = card
            card.pack(fill=tk.X, pady=8)
        
        # Instrucciones
        instructions_frame = tk.LabelFrame(
            self.root,
            text="📋 Instrucciones",
            font=("Arial", 10, "bold"),
            bg='#1e1e2e',
            fg='#89b4fa',
            padx=15,
            pady=10
        )
        instructions_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        instructions_text = (
            "1. Abre Pirate Galaxy y asegúrate de que los elementos sean visibles\n"
            "2. Haz clic en 'Configurar' en la región que quieres calibrar\n"
            "3. Dibuja un rectángulo alrededor del número/texto\n"
            "4. Repite para todas las regiones necesarias\n"
            "5. Haz clic en 'Guardar Todo' cuando termines"
        )
        
        instructions_label = tk.Label(
            instructions_frame,
            text=instructions_text,
            justify=tk.LEFT,
            bg='#1e1e2e',
            fg='#cdd6f4',
            font=("Arial", 9)
        )
        instructions_label.pack()
        
        # Botones de acción
        actions_frame = tk.Frame(self.root, bg='#1e1e2e')
        actions_frame.pack(fill=tk.X, padx=20, pady=15)
        
        self.save_all_btn = tk.Button(
            actions_frame,
            text="💾 Guardar Todo",
            command=self.save_all_config,
            font=("Arial", 12, "bold"),
            bg='#a6e3a1',
            fg='#1e1e2e',
            padx=30,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.save_all_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(
            actions_frame,
            text="🔄 Reiniciar Todo",
            command=self.reset_all,
            font=("Arial", 12, "bold"),
            bg='#f38ba8',
            fg='#1e1e2e',
            padx=30,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2"
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(
            actions_frame,
            text="❌ Cerrar",
            command=self.root.quit,
            font=("Arial", 12, "bold"),
            bg='#585b70',
            fg='#cdd6f4',
            padx=30,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
        
    def create_region_card(self, parent, region_key, region_data):
        """Crear card para una región"""
        card = tk.Frame(parent, bg='#313244', relief=tk.RAISED, bd=2)
        
        # Header del card
        header = tk.Frame(card, bg=region_data['color'], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text=f"🎯 {region_data['name']}",
            font=("Arial", 12, "bold"),
            bg=region_data['color'],
            fg='#1e1e2e'
        )
        title.pack(side=tk.LEFT, padx=15, pady=8)
        
        # Status indicator
        status_text = "✅ Configurado" if region_data['configured'] else "⚠️ No configurado"
        status_color = '#a6e3a1' if region_data['configured'] else '#f38ba8'
        
        status_label = tk.Label(
            header,
            text=status_text,
            font=("Arial", 9, "bold"),
            bg=region_data['color'],
            fg='#1e1e2e'
        )
        status_label.pack(side=tk.RIGHT, padx=15)
        
        # Body del card
        body = tk.Frame(card, bg='#313244')
        body.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Descripción
        desc_label = tk.Label(
            body,
            text=region_data['description'],
            font=("Arial", 9),
            bg='#313244',
            fg='#9399b2'
        )
        desc_label.pack(anchor=tk.W)
        
        # Información de región
        if region_data['configured'] and region_data['coords']:
            coords = region_data['coords']
            info_text = f"Región: [{coords[0]}, {coords[1]}, {coords[2]}, {coords[3]}]"
            info_label = tk.Label(
                body,
                text=info_text,
                font=("Courier", 8),
                bg='#313244',
                fg='#89dceb'
            )
            info_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Preview frame
        preview_frame = tk.Frame(body, bg='#1e1e2e', height=80, relief=tk.SUNKEN, bd=1)
        preview_frame.pack(fill=tk.X, pady=(10, 10))
        preview_frame.pack_propagate(False)
        
        preview_label = tk.Label(
            preview_frame,
            text="Sin captura" if not region_data['configured'] else "Vista previa",
            bg='#1e1e2e',
            fg='#9399b2',
            font=("Arial", 9)
        )
        preview_label.pack(expand=True)
        
        # Guardar referencia al preview
        region_data['preview_label'] = preview_label
        region_data['preview_frame'] = preview_frame
        
        # Botón de configurar
        config_btn = tk.Button(
            body,
            text="⚙️ Configurar" if not region_data['configured'] else "🔄 Reconfigurar",
            command=lambda: self.start_capture(region_key),
            font=("Arial", 10, "bold"),
            bg='#89b4fa',
            fg='#1e1e2e',
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        config_btn.pack(pady=(5, 0))
        
        region_data['config_btn'] = config_btn
        region_data['status_label'] = status_label
        
        return card
        
    def start_capture(self, region_key):
        """Iniciar captura para una región específica"""
        self.current_region = region_key
        self.root.withdraw()
        self.root.after(500, self.show_selection_window)
        
    def show_selection_window(self):
        """Mostrar ventana de selección transparente"""
        region_data = self.regions[self.current_region]
        
        # Crear ventana de selección
        self.selection_window = tk.Toplevel()
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-alpha', 0.3)
        self.selection_window.configure(bg='black')
        
        # Canvas para dibujar
        self.canvas = tk.Canvas(
            self.selection_window,
            cursor="cross",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Instrucciones en pantalla
        self.canvas.create_text(
            self.selection_window.winfo_screenwidth() // 2,
            50,
            text=f"Dibuja un rectángulo alrededor de: {region_data['name']}\nPresiona ESC para cancelar",
            font=("Arial", 16, "bold"),
            fill="white"
        )
        
        self.selection_window.bind("<Escape>", lambda e: self.cancel_selection())
        
        self.rect = None
        
    def on_press(self, event):
        """Mouse press"""
        self.start_x = event.x
        self.start_y = event.y
        
        if self.rect:
            self.canvas.delete(self.rect)
        
        region_color = self.regions[self.current_region]['color']
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.start_x, self.start_y,
            outline=region_color,
            width=4
        )
        
    def on_drag(self, event):
        """Mouse drag"""
        if self.rect:
            self.canvas.coords(
                self.rect,
                self.start_x, self.start_y,
                event.x, event.y
            )
            
    def on_release(self, event):
        """Mouse release"""
        self.end_x = event.x
        self.end_y = event.y
        
        # Asegurar que start < end
        x1 = min(self.start_x, self.end_x)
        x2 = max(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        y2 = max(self.start_y, self.end_y)
        
        self.start_x, self.end_x = x1, x2
        self.start_y, self.end_y = y1, y2
        
        # Cerrar ventana de selección
        self.selection_window.destroy()
        
        # Capturar región
        self.capture_region()
        
        # Mostrar ventana principal
        self.root.deiconify()
        
    def cancel_selection(self):
        """Cancelar selección"""
        self.selection_window.destroy()
        self.root.deiconify()
        self.current_region = None
        
    def capture_region(self):
        """Capturar región seleccionada"""
        if not all([self.start_x, self.start_y, self.end_x, self.end_y]):
            return
        
        if not self.current_region:
            return
        
        # Calcular región
        width = self.end_x - self.start_x
        height = self.end_y - self.start_y
        
        if width < 10 or height < 10:
            messagebox.showwarning("Región muy pequeña", "La región seleccionada es muy pequeña")
            self.current_region = None
            return
        
        # Capturar imagen
        try:
            screenshot = ImageGrab.grab(bbox=(
                self.start_x,
                self.start_y,
                self.end_x,
                self.end_y
            ))
            
            region_data = self.regions[self.current_region]
            
            # Guardar coordenadas
            region_data['coords'] = [self.start_x, self.start_y, width, height]
            region_data['configured'] = True
            
            # Mostrar preview
            screenshot_copy = screenshot.copy()
            screenshot_copy.thumbnail((150, 60))
            photo = ImageTk.PhotoImage(screenshot_copy)
            region_data['preview_label'].config(image=photo, text="")
            region_data['preview_label'].image = photo
            
            # Actualizar status
            region_data['status_label'].config(text="✅ Configurado")
            region_data['config_btn'].config(text="🔄 Reconfigurar")
            
            # Mensaje de confirmación
            messagebox.showinfo(
                "Captura Exitosa",
                f"✅ {region_data['name']} configurado correctamente!\n\n"
                f"Región: [{self.start_x}, {self.start_y}, {width}, {height}]"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al capturar región: {e}")
        
        finally:
            self.current_region = None
            
    def save_all_config(self):
        """Guardar todas las configuraciones en settings.json"""
        # Verificar que al menos una región esté configurada
        configured_regions = [k for k, v in self.regions.items() if v['configured']]
        
        if not configured_regions:
            messagebox.showwarning(
                "Sin configuración",
                "No hay regiones configuradas para guardar.\n\n"
                "Por favor, configura al menos una región antes de guardar."
            )
            return
        
        try:
            # Buscar settings.json en varias ubicaciones posibles
            possible_paths = [
                Path(__file__).parent / 'core' / 'settings.json',  # ui/core/settings.json
                Path(__file__).parent.parent / 'core' / 'settings.json',  # ../core/settings.json
                Path(__file__).parent / 'settings.json',  # ui/settings.json
                Path(__file__).parent.parent / 'settings.json',  # ../settings.json
            ]
            
            settings_path = None
            for path in possible_paths:
                if path.exists():
                    settings_path = path
                    break
            
            if not settings_path:
                # Mostrar diálogo para buscar manualmente
                from tkinter import filedialog
                messagebox.showinfo(
                    "Ubicar settings.json",
                    "No se encontró settings.json automáticamente.\n\n"
                    "Por favor, selecciona el archivo settings.json manualmente."
                )
                
                settings_path = filedialog.askopenfilename(
                    title="Seleccionar settings.json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    initialdir=Path(__file__).parent.parent
                )
                
                if not settings_path:
                    return
                
                settings_path = Path(settings_path)
            
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Obtener resolución
            screen_width, screen_height = pyautogui.size()
            resolution_key = f"{screen_width}x{screen_height}"
            
            # Inicializar stats_config si no existe
            if 'stats_config' not in settings:
                settings['stats_config'] = {}
            
            # Guardar cada región configurada
            for region_key, region_data in self.regions.items():
                if region_data['configured'] and region_data['coords']:
                    # Determinar la clave en settings
                    config_key = f"{region_key}_region"
                    
                    if config_key not in settings['stats_config']:
                        settings['stats_config'][config_key] = {}
                    
                    settings['stats_config'][config_key][resolution_key] = region_data['coords']
            
            # Guardar archivo
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            
            # Mensaje de éxito
            configured_names = [self.regions[k]['name'] for k in configured_regions]
            messagebox.showinfo(
                "✅ Configuración Guardada",
                f"Configuración guardada exitosamente!\n\n"
                f"Resolución: {resolution_key}\n"
                f"Regiones configuradas: {', '.join(configured_names)}\n\n"
                f"El bot ahora podrá leer estas regiones correctamente."
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar configuración: {e}")
    
    def reset_all(self):
        """Reiniciar todas las configuraciones"""
        result = messagebox.askyesno(
            "Confirmar Reinicio",
            "¿Estás seguro de que quieres reiniciar todas las configuraciones?\n\n"
            "Esto borrará todas las capturas actuales."
        )
        
        if result:
            for region_key, region_data in self.regions.items():
                region_data['configured'] = False
                region_data['coords'] = None
                region_data['preview_label'].config(image='', text="Sin captura")
                region_data['preview_label'].image = None
                region_data['status_label'].config(text="⚠️ No configurado")
                region_data['config_btn'].config(text="⚙️ Configurar")
            
            messagebox.showinfo("Reiniciado", "Todas las configuraciones han sido reiniciadas.")
    
    def run(self):
        """Ejecutar aplicación"""
        self.root.mainloop()


if __name__ == '__main__':
    print("=" * 60)
    print("  Configurador de Regiones - Pirate Galaxy Bot")
    print("=" * 60)
    print("\nEsta herramienta te ayudará a configurar todas las posiciones")
    print("de lectura necesarias para tu resolución de pantalla.\n")
    print("Regiones disponibles:")
    print("  • Crionita - Contador de recursos")
    print("  • Energía - Valor de energía del jugador")
    print("\n" + "=" * 60)
    print("\n🔍 Buscando settings.json...")
    print(f"📁 Directorio actual: {Path(__file__).parent}\n")
    
    try:
        app = MultiRegionConfigTool()
        app.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")