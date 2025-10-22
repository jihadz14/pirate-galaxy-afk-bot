###################
# Bot Logger      #
###################

import logging
from datetime import datetime
import json
from pathlib import Path

class BotLogger:
    def __init__(self, log_dir='logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Archivo de log con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"bot_{timestamp}.log"
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('PGBot')
        
        # Estadísticas de la sesión
        self.stats = {
            'session_id': timestamp,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'enemies_killed': 0,
            'loot_collected': 0,
            'deaths': 0,
            'hp_heals': 0,
            'energy_low_alerts': 0,
            'flee_events': 0,
            'combat_profile': 'balanced',
            'total_hp_lost': 0,
            'total_energy_used': 0,
            'errors': [],
            'skills_used': {},
            'time_in_state': {
                'INIT': 0,
                'FARMING': 0,
                'FLEEING': 0
            }
        }
        
        # Tracking de última HP/energía para calcular diferencias
        self.last_hp = 100
        self.last_energy = 10000
        
    def info(self, message):
        """Log nivel INFO"""
        self.logger.info(message)
        
    def warning(self, message):
        """Log nivel WARNING"""
        self.logger.warning(message)
        
    def error(self, message):
        """Log nivel ERROR"""
        self.logger.error(message)
        self.stats['errors'].append({
            'time': datetime.now().isoformat(),
            'message': message
        })
        
    def log_kill(self):
        """Registrar muerte de enemigo"""
        self.stats['enemies_killed'] += 1
        self.info(f"Enemy killed (Total: {self.stats['enemies_killed']})")
        
    def log_loot(self):
        """Registrar loot recolectado"""
        self.stats['loot_collected'] += 1
        
    def log_death(self):
        """Registrar muerte del jugador"""
        self.stats['deaths'] += 1
        self.warning(f"Player died! (Total deaths: {self.stats['deaths']})")
        
    def log_heal(self):
        """Registrar uso de curación"""
        self.stats['hp_heals'] += 1
        self.info(f"Healed (Total heals: {self.stats['hp_heals']})")
        
    def log_energy_low(self, energy_amount):
        """Registrar alerta de energía baja"""
        self.stats['energy_low_alerts'] += 1
        self.warning(f"Low energy alert: {energy_amount}")
        
    def log_flee(self):
        """Registrar evento de huida"""
        self.stats['flee_events'] += 1
        self.warning(f"Fleeing from combat (Total: {self.stats['flee_events']})")
        
    def log_skill_used(self, skill_name):
        """Registrar uso de habilidad"""
        if skill_name not in self.stats['skills_used']:
            self.stats['skills_used'][skill_name] = 0
        self.stats['skills_used'][skill_name] += 1
        
    def log_hp_change(self, current_hp):
        """Registrar cambio en HP"""
        if current_hp < self.last_hp:
            hp_lost = self.last_hp - current_hp
            self.stats['total_hp_lost'] += hp_lost
        self.last_hp = current_hp
        
    def log_energy_change(self, current_energy):
        """Registrar cambio en energía"""
        if current_energy < self.last_energy:
            energy_used = self.last_energy - current_energy
            self.stats['total_energy_used'] += energy_used
        self.last_energy = current_energy
        
    def log_profile_change(self, profile_name):
        """Registrar cambio de perfil de combate"""
        self.stats['combat_profile'] = profile_name
        self.info(f"Combat profile changed to: {profile_name}")
        
    def get_summary(self):
        """Obtener resumen de estadísticas"""
        if self.stats['start_time']:
            start = datetime.fromisoformat(self.stats['start_time'])
            duration = datetime.now() - start
            runtime_seconds = duration.total_seconds()
            
            return {
                'runtime': str(duration).split('.')[0],
                'enemies_killed': self.stats['enemies_killed'],
                'loot_collected': self.stats['loot_collected'],
                'deaths': self.stats['deaths'],
                'heals_used': self.stats['hp_heals'],
                'flee_events': self.stats['flee_events'],
                'enemies_per_hour': round(self.stats['enemies_killed'] / (runtime_seconds / 3600), 2) if runtime_seconds > 0 else 0,
                'heals_per_hour': round(self.stats['hp_heals'] / (runtime_seconds / 3600), 2) if runtime_seconds > 0 else 0,
                'total_hp_lost': self.stats['total_hp_lost'],
                'total_energy_used': self.stats['total_energy_used'],
                'most_used_skill': max(self.stats['skills_used'].items(), key=lambda x: x[1])[0] if self.stats['skills_used'] else 'None',
                'combat_profile': self.stats['combat_profile']
            }
        return {}
        
    def save_stats(self):
        """Guardar estadísticas al finalizar sesión"""
        stats_file = self.log_dir / 'stats.json'
        self.stats['end_time'] = datetime.now().isoformat()
        
        # Cargar stats anteriores si existen
        all_stats = []
        if stats_file.exists():
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    all_stats = json.load(f)
            except:
                pass
        
        # Agregar sesión actual
        all_stats.append(self.stats)
        
        # Guardar todas las sesiones
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(all_stats, f, indent=2, ensure_ascii=False)
        
        # Guardar resumen legible
        summary_file = self.log_dir / f"session_{self.stats['session_id']}_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 50 + "\n")
            f.write(f"SESSION SUMMARY - {self.stats['session_id']}\n")
            f.write("=" * 50 + "\n\n")
            
            summary = self.get_summary()
            for key, value in summary.items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            
            f.write("\n" + "=" * 50 + "\n")
            f.write("SKILLS USAGE\n")
            f.write("=" * 50 + "\n")
            for skill, count in sorted(self.stats['skills_used'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"{skill}: {count} times\n")
        
        self.info(f"Stats saved to: {stats_file}")
        self.info(f"Summary saved to: {summary_file}")