###################
# Enhanced PGBot  #
# UI Compatible   #
###################

import sys
import os
import traceback

# Agregar carpetas al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'enhanced'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

sys.dont_write_bytecode = True

print("╔═══════════════════════════════════════╗")
print("║   PIRATE GALAXY BOT - ENHANCED       ║")
print("║   UI Gráfica + OCR Mejorado          ║")
print("╚═══════════════════════════════════════╝")
print("[INFO] Iniciando bot versión mejorada...")
print("[INFO] Se abrirá una ventana gráfica")
print("════════════════════════════════════════")

# Verificar PyQt5 ANTES de llamar al importer
print("\n[1/5] Verificando PyQt5...")
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtChart import QChart
    from PyQt5.QtCore import QTimer
    print("✓ PyQt5 encontrado")
except ImportError as e:
    print(f"✗ Error: PyQt5 no está instalado")
    print(f"Detalle: {e}")
    print(f"\nInstala con: pip install PyQt5 PyQtChart")
    input("\nPresiona Enter para salir...")
    sys.exit(1)

# Verificar las demás dependencias
print("\n[2/5] Verificando dependencias...")
try:
    from importer import Importer
    Importer.verifyLibs({'pyautogui', 'keyboard', 'colorama', 'requests', 'pytesseract', 'opencv-python', 'pywin32'})
    print("✓ Todas las dependencias verificadas")
except Exception as e:
    print(f"✗ Error verificando dependencias: {e}")
    traceback.print_exc()
    input("\nPresiona Enter para salir...")
    sys.exit(1)

# Importar módulos del bot
print("\n[3/5] Importando módulos del bot...")
try:
    from bot_ui import BotUIWindow
    print("✓ bot_ui importado")
except Exception as e:
    print(f"✗ Error importando bot_ui: {e}")
    traceback.print_exc()
    input("\nPresiona Enter para salir...")
    sys.exit(1)

try:
    from ocr_enhanced import EnhancedOCR
    ocr_available = True
    print("✓ ocr_enhanced importado")
except ImportError:
    print("⚠ OCR Enhanced no disponible, usando OCR básico")
    ocr_available = False

try:
    from logger import BotLogger
    logger_available = True
    print("✓ logger importado")
except ImportError:
    print("⚠ Logger no disponible")
    logger_available = False

try:
    from bot import PGBot, BotState
    print("✓ bot importado")
except Exception as e:
    print(f"✗ Error importando bot: {e}")
    traceback.print_exc()
    input("\nPresiona Enter para salir...")
    sys.exit(1)

print("\n[4/5] Importando librerías adicionales...")
try:
    from time import sleep, time
    import json
    import pyautogui
    from PIL import Image
    import cv2 as cv
    import numpy as np
    import keyboard
    print("✓ Librerías adicionales importadas")
except Exception as e:
    print(f"✗ Error importando librerías: {e}")
    traceback.print_exc()
    input("\nPresiona Enter para salir...")
    sys.exit(1)

# Load Settings
print("\n[5/5] Cargando configuración...")
try:
    settings_path = os.path.join(os.path.dirname(__file__), 'core', 'settings.json')
    
    if not os.path.exists(settings_path):
        print(f"✗ Error: No se encontró settings.json en: {settings_path}")
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    
    with open(settings_path, encoding='utf-8') as f:
        settings = json.load(f)
    print(f"✓ Configuración cargada desde: {settings_path}")
except Exception as e:
    print(f"✗ Error cargando settings.json: {e}")
    traceback.print_exc()
    input("\nPresiona Enter para salir...")
    sys.exit(1)

# Crear logger si está disponible
if logger_available:
    try:
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        logger = BotLogger(log_dir=log_dir)
        print("✓ Logger inicializado")
    except Exception as e:
        print(f"⚠ Error inicializando logger: {e}")
        logger = None
else:
    logger = None

print("\n════════════════════════════════════════")
print("✓ TODAS LAS VERIFICACIONES COMPLETADAS")
print("════════════════════════════════════════\n")

# Crear bot con OCR mejorado
class EnhancedPGBot(PGBot):
    """Bot mejorado con OCR avanzado y sistema de curación inteligente"""
    
    def __init__(self, settings, appName, version):
        super().__init__(settings, appName, version)
        
        # Logger
        if logger_available:
            self.logger = logger
        else:
            self.logger = None
        
        # OCR mejorado
        if ocr_available:
            self.ocr = EnhancedOCR()
        else:
            self.ocr = None
        
        # Asegurar que stopped existe
        if not hasattr(self, 'stopped'):
            self.stopped = False
        
        # Cargar configuración de estadísticas
        self.stats_config = settings.get('stats_config', {
            'enable_kill_tracking': True,
            'enable_collection_tracking': True,
            'enable_crionita_tracking': True,
            'enable_lowlife_tracking': True,
            'crionita_region': {
                'default': [1700, 50, 150, 30]
            }
        })
        
        # Sistema de estadísticas de sesión
        self.session_stats = {
            'kills': 0,
            'heals': 0,
            'collections': 0,
            'crionita': 0,
            'lowlife': 0
        }
        
        # Variables de tracking
        self.current_target_id = None
        self.last_target_type = None
        self.last_crionita = 0
        self.lowlife_triggered = False
        self.stats_check_time = time()
    
    def increment_stat(self, stat_name):
        """Incrementar una estadística de sesión"""
        if stat_name in self.session_stats:
            self.lock.acquire()
            self.session_stats[stat_name] += 1
            self.lock.release()
    
    def check_kill(self):
        """Verificar si se eliminó un enemigo - MÉTODO MEJORADO"""
        if not self.stats_config.get('enable_kill_tracking', True):
            return
        
        try:
            # Buscar en área del minimapa
            find_minimap = self.search('minimap', 0.7)
            
            if find_minimap != False:
                # Buscar píxel rojo (enemigo seleccionado) alrededor del minimapa
                minimap_region = (
                    int(find_minimap.left + 25), 
                    int(find_minimap.top - 100), 
                    115, 
                    115
                )
                
                screenshot = pyautogui.screenshot(region=minimap_region)
                img_array = np.array(screenshot)
                
                # Buscar píxeles rojos (enemigos)
                enemy_color = self.objectPixel.get('enemy', [135, 27, 11])
                
                # Crear máscara para detectar color rojo de enemigo
                lower_bound = np.array([max(0, enemy_color[0]-15), max(0, enemy_color[1]-15), max(0, enemy_color[2]-15)])
                upper_bound = np.array([min(255, enemy_color[0]+15), min(255, enemy_color[1]+15), min(255, enemy_color[2]+15)])
                
                mask = cv.inRange(img_array, lower_bound, upper_bound)
                enemy_pixels = cv.countNonZero(mask)
                
                has_target = enemy_pixels > 3
                
                if has_target:
                    target_id = enemy_pixels
                    
                    if self.current_target_id is None:
                        self.current_target_id = target_id
                        self.last_target_type = 'enemy'
                    elif abs(self.current_target_id - target_id) > 50:
                        if self.last_target_type == 'enemy':
                            self.increment_stat('kills')
                            self._log_stat('kill')
                        self.current_target_id = target_id
                        self.last_target_type = 'enemy'
                else:
                    if self.current_target_id is not None and self.last_target_type == 'enemy':
                        if hasattr(self, 'targets') and self.targets and self.targets[2] in ['enemy', 'enemyIdle']:
                            self.increment_stat('kills')
                            self._log_stat('kill')
                    self.current_target_id = None
                    self.last_target_type = None
        except Exception as e:
            pass
    
    def check_collection(self):
        """Verificar si se recolectó un objeto - MÉTODO MEJORADO"""
        if not self.stats_config.get('enable_collection_tracking', True):
            return
        
        try:
            find_minimap = self.search('minimap', 0.7)
            
            if find_minimap != False:
                minimap_region = (
                    int(find_minimap.left + 25), 
                    int(find_minimap.top - 100), 
                    115, 
                    115
                )
                
                screenshot = pyautogui.screenshot(region=minimap_region)
                img_array = np.array(screenshot)
                
                loot_color = self.objectPixel.get('loot', [19, 193, 217])
                
                lower_bound = np.array([max(0, loot_color[0]-15), max(0, loot_color[1]-15), max(0, loot_color[2]-15)])
                upper_bound = np.array([min(255, loot_color[0]+15), min(255, loot_color[1]+15), min(255, loot_color[2]+15)])
                
                mask = cv.inRange(img_array, lower_bound, upper_bound)
                loot_pixels = cv.countNonZero(mask)
                
                has_loot = loot_pixels > 3
                
                if has_loot:
                    loot_id = loot_pixels
                    
                    if self.current_target_id is None:
                        self.current_target_id = loot_id
                        self.last_target_type = 'loot'
                    elif abs(self.current_target_id - loot_id) > 50:
                        if self.last_target_type == 'loot':
                            self.increment_stat('collections')
                            self._log_stat('collection')
                        self.current_target_id = loot_id
                        self.last_target_type = 'loot'
                else:
                    if self.current_target_id is not None and self.last_target_type == 'loot':
                        if hasattr(self, 'targets') and self.targets and self.targets[2] == 'loot':
                            self.increment_stat('collections')
                            self._log_stat('collection')
                    
                    if self.last_target_type == 'loot':
                        self.current_target_id = None
                        self.last_target_type = None
        except Exception as e:
            pass
    
    def check_crionita(self):
        """Verificar cantidad de crionita"""
        if not self.stats_config.get('enable_crionita_tracking', True):
            return
        
        try:
            crionita_regions = self.stats_config.get('crionita_region', {})
            screen_width, screen_height = pyautogui.size()
            resolution_key = f"{screen_width}x{screen_height}"
            
            if resolution_key in crionita_regions:
                crionita_region = tuple(crionita_regions[resolution_key])
            else:
                crionita_region = tuple(crionita_regions.get('default', [1700, 50, 150, 30]))
            
            screenshot = pyautogui.screenshot(region=crionita_region)
            
            if self.ocr and hasattr(self.ocr, 'read_number'):
                crionita_text = self.ocr.read_number(screenshot)
            else:
                crionita_text = self.getNum(screenshot)
            
            if crionita_text and crionita_text.strip():
                crionita = int(crionita_text.replace(',', '').replace('.', '').strip())
                
                if crionita > self.last_crionita:
                    diff = crionita - self.last_crionita
                    self.lock.acquire()
                    self.session_stats['crionita'] = crionita
                    self.lock.release()
                    
                    if self.logger:
                        self.logger.info(f"Crionita: {crionita:,} (+{diff:,})")
                
                self.last_crionita = crionita
        except:
            pass
    
    def check_lowlife(self):
        """Verificar si la vida está por debajo del 30%"""
        if not self.stats_config.get('enable_lowlife_tracking', True):
            return
        
        if self.plr_hp <= 30 and not self.lowlife_triggered:
            self.increment_stat('lowlife')
            self.lowlife_triggered = True
            self._log_stat('lowlife')
        elif self.plr_hp > 30:
            self.lowlife_triggered = False
    
    def _log_stat(self, stat_type):
        """Log de estadística"""
        messages = {
            'kill': f"Kill #{self.session_stats['kills']}",
            'collection': f"Collection #{self.session_stats['collections']}",
            'lowlife': f"Low life event #{self.session_stats['lowlife']}"
        }
        
        if self.logger and stat_type in messages:
            self.logger.info(messages[stat_type])
    
    def checkHP(self):
        """Override con OCR mejorado + sistema de curación mejorado + estadísticas"""
        if not self.checkTimePassed(1, 2):
            if (self.plr_hp <= self.healOnHp):
                current_time = time()
                if current_time - self.last_heal_time >= self.healCooldown:
                    self.skill(self.checkSkill("repair"))
                    self.last_heal_time = current_time
                    self.increment_stat('heals')
                    if self.logger:
                        self.logger.log_heal()
                    return True
            return False

        find = self.search('minimap')
        if find != False:
            screenshot = pyautogui.screenshot(region=(int(find.left - 25), int(find.top + 5), 20, 15))
            
            if self.ocr and hasattr(self.ocr, 'read_hp'):
                hp = self.ocr.read_hp(screenshot)
            else:
                chp = pyautogui.screenshot('./data/search/hp.png', region=(int(find.left - 25), int(find.top + 5), 20, 15))
                newImg = Image.new('RGB', (2*chp.size[0], chp.size[1]), (250,250,250))
                newImg.paste(chp,(0,0))
                newImg.paste(chp,(chp.size[0],0))
                newImg.save("./data/search/hp.png", "PNG")
                
                chp_text = self.getNum(Image.open('./data/search/hp.png')).replace('\n', '').replace('\x0c', '').replace('|', '')
                chp_text = chp_text[0:int(len(chp_text)/2)] if chp_text else ''
                
                if chp_text != '' and chp_text != ' ':
                    hp = int(chp_text)
                    if hp == 1 or hp == 2:
                        hp = None
                else:
                    hp = None
            
            if hp is not None:
                self.lock.acquire()
                old_hp = self.last_hp
                self.plr_hp = hp
                self.lock.release()
                
                self.check_lowlife()

                current_time = time()
                time_since_last_heal = current_time - self.last_heal_time
                hp_is_dropping = hp < old_hp or old_hp == 100
                
                should_heal = False
                
                if hp < 80 and hp_is_dropping and time_since_last_heal >= self.healCooldown:
                    should_heal = True
                    if self.logger:
                        self.logger.info(f"Healing at {hp}% (< 80%)")
                elif hp <= self.healOnHp:
                    should_heal = True
                    if self.logger:
                        self.logger.warning(f"CRITICAL HEAL at {hp}%")
                
                if should_heal:
                    self.skill(self.checkSkill("repair"))
                    self.last_heal_time = current_time
                    self.last_hp = hp
                    self.increment_stat('heals')
                    if self.logger:
                        self.logger.log_heal()
                    return True
                
                self.last_hp = hp
            else:
                self.lock.acquire()
                self.plr_hp = 100
                self.last_hp = 100
                self.lock.release()
            return False
        else:
            return False
    
    # ELIMINADO: método checkEnergy() - ahora usa el método mejorado de la clase base (bot.py)
    # La clase PGBot ya tiene un método checkEnergy() con:
    # - Región configurada desde settings.json
    # - Múltiples intentos de OCR
    # - Validación de rangos (100-50000)
    # Por eso NO necesitamos override aquí


# MAIN EXECUTION
try:
    print("Inicializando bot...")
    bot = EnhancedPGBot(settings, 'Pirate Galaxy Bot Enhanced', '2.0.0')
    print("✓ Bot inicializado")

    if logger:
        logger.info('Bot Enhanced v2.0.0 starting...')
        logger.info(f'Heal settings: HP < 80%, Cooldown: {bot.healCooldown}s')

    print("Iniciando bot thread...")
    bot.start()
    print("✓ Bot thread iniciado")

    print("\nCreando interfaz gráfica...")
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    ui = BotUIWindow(bot)
    ui.show()
    print("✓ UI mostrada")

    ui.log("Bot Enhanced v2.0 iniciado")
    ui.log(f"Sistema de curación: HP < 80%, Cooldown: {bot.healCooldown}s")

    # Main Loop con QTimer
    loop_time = time()
    update_timer = QTimer()
    stats_timer = QTimer()

    def update_bot_loop():
        global loop_time
        if not bot.paused and not bot.stopped:
            bot.update_targets()
            loop_time = time()

    def update_stats_loop():
        if not bot.paused and not bot.stopped:
            bot.check_kill()
            bot.check_collection()
            if time() - bot.stats_check_time > 5:
                bot.check_crionita()
                bot.stats_check_time = time()

    update_timer.timeout.connect(update_bot_loop)
    update_timer.start(100)

    stats_timer.timeout.connect(update_stats_loop)
    stats_timer.start(500)

    print("✓ Timers iniciados\n")

    # Hotkeys
    print("Configurando hotkeys...")
    hotkeys_active = True

    def on_quit_hotkey():
        global hotkeys_active
        if not hotkeys_active:
            return
        
        print("\n[HOTKEY] Q presionada - Cerrando bot...")
        ui.log("Hotkey Q detectada - Cerrando bot")
        
        update_timer.stop()
        stats_timer.stop()
        bot.stop()
        cv.destroyAllWindows()
        
        if logger:
            logger.save_stats()
        
        hotkeys_active = False
        keyboard.unhook_all()
        app.quit()

    def on_pause_hotkey():
        if not hotkeys_active:
            return
        
        if bot.paused:
            bot.paused = False
            ui.log("Bot reanudado (Hotkey P)")
            ui.pause_btn.setText("PAUSE")
            ui.status_label.setText("RUNNING")
            ui.status_label.setStyleSheet(f"color: #1e1e2e; background-color: rgba(166, 227, 161, 0.35); padding: 6px 15px; border-radius: 8px;")
            print("[HOTKEY] Bot reanudado")
        else:
            bot.paused = True
            ui.log("Bot pausado (Hotkey P)")
            ui.pause_btn.setText("RESUME")
            ui.status_label.setText("PAUSED")
            ui.status_label.setStyleSheet(f"color: #1e1e2e; background-color: rgba(249, 226, 175, 0.4); padding: 6px 15px; border-radius: 8px;")
            print("[HOTKEY] Bot pausado")

    def on_energy_hotkey():
        """NUEVO: Toggle Energy Loading"""
        if not hotkeys_active:
            return
        
        try:
            is_active = bot.toggle_energy_loading()
            
            if is_active:
                ui.log("⚡ Energy Loading ACTIVADO (Presiona E para desactivar)")
                print("[HOTKEY] Energy Loading ACTIVADO")
                
                # Actualizar botón en UI si existe
                if hasattr(ui, 'energy_btn'):
                    ui.energy_btn.setText("⚡ LOADING...")
                    ui.energy_btn.setStyleSheet("""
                        QPushButton {
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #a6e3a1, stop:1 #94e2d5);
                            color: #1e1e2e;
                            font-size: 13px;
                            border-radius: 8px;
                            font-weight: bold;
                            border: 2px solid #a6e3a1;
                        }
                        QPushButton:hover {
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #b4f0b0, stop:1 #a6f0e8);
                        }
                    """)
            else:
                ui.log("⚡ Energy Loading DESACTIVADO")
                print("[HOTKEY] Energy Loading DESACTIVADO")
                
                # Restaurar botón en UI si existe
                if hasattr(ui, 'energy_btn'):
                    ui.energy_btn.setText("⚡ LOAD ENERGY")
                    ui.energy_btn.setStyleSheet("""
                        QPushButton {
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #89dceb, stop:1 #89b4fa);
                            color: #1e1e2e;
                            font-size: 13px;
                            border-radius: 8px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #a0f0ff, stop:1 #a0c4ff);
                            border: 2px solid #89dceb;
                        }
                    """)
        except Exception as e:
            ui.log(f"Error en Energy Loading: {str(e)}")
            print(f"[ERROR] Energy Loading: {e}")

    try:
        keyboard.add_hotkey('q', on_quit_hotkey, suppress=False)
        keyboard.add_hotkey('p', on_pause_hotkey, suppress=False)
        keyboard.add_hotkey('e', on_energy_hotkey, suppress=False)  # NUEVO
        print("✓ Hotkeys configurados (Q=cerrar, P=pausar, E=energy loading)\n")
    except Exception as e:
        print(f"⚠ No se pudieron registrar hotkeys: {e}\n")

    print("╔════════════════════════════════════════╗")
    print("║  🚀 Bot Enhanced ejecutándose          ║")
    print("║  Presiona Q para cerrar                ║")
    print("║  Presiona P para pausar                ║")
    print("║  Presiona E para Energy Loading ⚡     ║")
    print("╚════════════════════════════════════════╝\n")

    # Ejecutar
    exit_code = app.exec_()
    
except Exception as e:
    print("\n" + "="*60)
    print("❌ ERROR CRÍTICO")
    print("="*60)
    print(f"Tipo de error: {type(e).__name__}")
    print(f"Mensaje: {e}")
    print("\nTraceback completo:")
    traceback.print_exc()
    print("="*60)
    input("\nPresiona Enter para salir...")
    sys.exit(1)

finally:
    print("\n[INFO] Limpiando recursos...")
    
    try:
        if 'hotkeys_active' in locals() and hotkeys_active:
            keyboard.unhook_all()
    except:
        pass
    
    try:
        if 'update_timer' in locals():
            update_timer.stop()
        if 'stats_timer' in locals():
            stats_timer.stop()
    except:
        pass
    
    try:
        if 'bot' in locals():
            bot.stop()
    except:
        pass
    
    try:
        cv.destroyAllWindows()
    except:
        pass
    
    try:
        if 'logger' in locals() and logger:
            logger.save_stats()
    except:
        pass
    
    print("[OK] Bot cerrado correctamente")