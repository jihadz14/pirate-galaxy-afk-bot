"""
Extensión del bot con sistema de carga de energía
"""

from bot import PGBot
from energy_detector import EnergyDetector
import time

class EnergyLoadingBot(PGBot):
    def __init__(self, settings, appName, version):
        super().__init__(settings, appName, version)
        
        # Sistema de detección de energía
        self.energy_detector = EnergyDetector(self)
        
        # Estado de carga de energía
        self.energy_loading_mode = False
        self.orbs_collected = 0
        self.last_orb_collection = 0
        
        print("✓ Sistema de carga de energía inicializado")
    
    def toggle_energy_loading(self):
        """Activar/desactivar modo de carga de energía"""
        self.energy_loading_mode = not self.energy_loading_mode
        
        status = "ACTIVADO" if self.energy_loading_mode else "DESACTIVADO"
        print(f"⚡ Modo de carga de energía: {status}")
        
        return self.energy_loading_mode
    
    def collect_energy_orbs(self, max_orbs=10, timeout=30):
        """
        Recolectar orbes de energía
        
        max_orbs: máximo de orbes a recolectar
        timeout: tiempo máximo en segundos
        """
        print(f"\n⚡ Iniciando carga de energía...")
        print(f"  Objetivo: {max_orbs} orbes o {timeout}s")
        
        start_time = time.time()
        collected = 0
        
        while collected < max_orbs and time.time() - start_time < timeout:
            # Detectar orbe más cercano
            orb = self.energy_detector.find_nearest_orb()
            
            if orb is None:
                print(f"  ℹ No se detectaron más orbes")
                break
            
            # Click en el orbe
            print(f"  → Recolectando orbe en ({orb['x']}, {orb['y']})")
            self.click(orb['x'], orb['y'])
            
            # Esperar animación de recolección
            time.sleep(0.8)
            
            # Usar collector skill
            collector_slot = self.checkSkill("collector")
            if collector_slot:
                self.skill(collector_slot)
                time.sleep(0.5)
            
            collected += 1
            self.orbs_collected += 1
            
            print(f"  ✓ Orbe {collected}/{max_orbs} recolectado")
        
        elapsed = time.time() - start_time
        print(f"\n✓ Carga completada: {collected} orbes en {elapsed:.1f}s")
        print(f"  Total de sesión: {self.orbs_collected} orbes")
        
        return collected
    
    def auto_energy_loading_loop(self):
        """
        Loop automático de carga de energía
        Se ejecuta mientras energy_loading_mode esté activo
        """
        while self.energy_loading_mode and not self.stopped:
            # Buscar orbes
            orbs = self.energy_detector.detect_energy_orbs()
            
            if len(orbs) > 0:
                # Hay orbes disponibles, recolectar
                self.collect_energy_orbs(max_orbs=5, timeout=15)
            else:
                # No hay orbes, esperar
                print("  ⏸ Esperando orbes de energía...")
                time.sleep(2)