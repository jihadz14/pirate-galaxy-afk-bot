###################
# Bot UI - PyQt5  #
# Modern Design   #
# 800x600 (4:3)   #
# + Crionita      #
###################

import sys
import json
import logging
import subprocess
import pyautogui
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QProgressBar, QGroupBox, QGridLayout, QFrame, 
                             QComboBox, QDialog, QScrollArea,
                             QTabWidget, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QPointF
from PyQt5.QtGui import QFont, QColor, QPainter, QPixmap, QPolygonF
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from datetime import datetime
from collections import deque

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StyleConstants:
    """Constantes de estilo para mantener consistencia"""
    
    # Colores principales (Catppuccin Mocha)
    BG_PRIMARY = "#1e1e2e"
    BG_SECONDARY = "#181825"
    BG_DARK = "#11111b"
    
    SURFACE_0 = "#313244"
    SURFACE_1 = "#45475a"
    SURFACE_2 = "#585b70"
    
    TEXT_PRIMARY = "#cdd6f4"
    TEXT_SECONDARY = "#9399b2"
    TEXT_DARK = "#313244"
    
    # Colores de acento
    BLUE = "#89b4fa"
    CYAN = "#89dceb"
    GREEN = "#a6e3a1"
    YELLOW = "#f9e2af"
    RED = "#f38ba8"
    PURPLE = "#cba6f7"
    TEAL = "#94e2d5"
    PEACH = "#fab387"
    
    # Gradientes
    GRADIENT_BLUE = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #89dceb, stop:0.5 #89b4fa, stop:1 #cba6f7)"
    GRADIENT_GREEN = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a6e3a1, stop:1 #94e2d5)"
    GRADIENT_YELLOW = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f9e2af, stop:1 #f5c2a0)"
    GRADIENT_RED = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f38ba8, stop:1 #eba0ac)"


class ModernComboBox(QComboBox):
    """ComboBox personalizado con diseño moderno"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(35)
        self.setCursor(Qt.PointingHandCursor)
        self._apply_style()
    
    def _apply_style(self):
        self.setStyleSheet(f"""
            QComboBox {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {StyleConstants.SURFACE_2}, stop:1 {StyleConstants.SURFACE_1});
                color: {StyleConstants.TEXT_PRIMARY};
                border: 2px solid {StyleConstants.SURFACE_1};
                border-radius: 6px;
                padding: 6px 35px 6px 12px;
                font-size: 13px;
                font-weight: bold;
            }}
            QComboBox:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6c7086, stop:1 {StyleConstants.SURFACE_2});
                border: 2px solid {StyleConstants.BLUE};
            }}
            QComboBox:focus {{
                border: 2px solid {StyleConstants.CYAN};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 30px;
                border: none;
                background: transparent;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
                width: 12px;
                height: 12px;
            }}
            QComboBox::down-arrow:on {{
                image: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {StyleConstants.SURFACE_0};
                color: {StyleConstants.TEXT_PRIMARY};
                selection-background-color: {StyleConstants.SURFACE_2};
                border: 2px solid {StyleConstants.SURFACE_1};
                border-radius: 6px;
                padding: 4px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px;
                border-radius: 3px;
                min-height: 25px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {StyleConstants.SURFACE_1};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {StyleConstants.SURFACE_2};
                color: {StyleConstants.TEXT_PRIMARY};
            }}
        """)
    
    def paintEvent(self, event):
        """Custom paint para dibujar la flecha"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Obtener área del dropdown
        from PyQt5.QtWidgets import QStyleOptionComboBox
        opt = QStyleOptionComboBox()
        opt.initFrom(self)
        
        dropdown_rect = self.style().subControlRect(
            self.style().CC_ComboBox, 
            opt, 
            self.style().SC_ComboBoxArrow, 
            self
        )
        
        # Dibujar flecha (triángulo)
        arrow_color = QColor(StyleConstants.CYAN)
        painter.setPen(arrow_color)
        painter.setBrush(arrow_color)
        
        # Calcular posición central
        center_x = dropdown_rect.center().x()
        center_y = dropdown_rect.center().y()
        
        # Crear triángulo apuntando hacia abajo
        points = [
            QPointF(center_x - 5, center_y - 2),
            QPointF(center_x + 5, center_y - 2),
            QPointF(center_x, center_y + 3)
        ]
        
        painter.drawPolygon(QPolygonF(points))
        painter.end()


class SkillEditorDialog(QDialog):
    """Diálogo para editar preset custom"""
    
    def __init__(self, current_skills, parent=None):
        super().__init__(parent)
        self.current_skills = current_skills or [""] * 8
        self.skill_combos = []
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("Edit Custom Preset")
        self.setMinimumWidth(500)
        self.setMinimumHeight(550)
        self.setModal(True)
        
        self._apply_style()
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        header = self._create_header()
        layout.addWidget(header)
        layout.addSpacing(8)
        
        scroll = self._create_skill_slots()
        layout.addWidget(scroll)
        
        button_layout = self._create_buttons()
        layout.addLayout(button_layout)
    
    def _apply_style(self):
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {StyleConstants.BG_PRIMARY}, stop:1 {StyleConstants.BG_SECONDARY});
            }}
            QLabel {{
                color: {StyleConstants.TEXT_PRIMARY};
                font-size: 13px;
            }}
            QGroupBox {{
                color: {StyleConstants.BLUE};
                font-size: 13px;
                font-weight: bold;
                border: 2px solid {StyleConstants.SURFACE_1};
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: {StyleConstants.BG_SECONDARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                background-color: {StyleConstants.BG_PRIMARY};
            }}
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {StyleConstants.SURFACE_2}, stop:1 {StyleConstants.SURFACE_1});
                color: {StyleConstants.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6c7086, stop:1 {StyleConstants.SURFACE_2});
                border: 2px solid {StyleConstants.BLUE};
            }}
            QPushButton:pressed {{
                background: {StyleConstants.SURFACE_1};
            }}
        """)
    
    def _create_header(self):
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: {StyleConstants.GRADIENT_BLUE};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(3)
        
        title = QLabel("Custom Preset Editor")
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setStyleSheet(f"color: {StyleConstants.BG_PRIMARY};")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Configure your 8 skill slots (Keys 1-8)")
        subtitle.setStyleSheet(f"color: {StyleConstants.SURFACE_0}; font-size: 11px;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        return header
    
    def _create_skill_slots(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)
        
        all_skills = [
            "(empty)", "blaster", "collector", "repair", "afterburner",
            "rocket", "orbitalstrike", "shield", "protector",
            "scramble", "speedactuator", "aimcomp", "perforator",
            "dmgbuff", "stun", "thermoblast", "taunt", "sniper",
            "attackdroid", "aggrobomb", "mine", "stundome",
            "stickybomb", "magnettrap", "aggrobeacon",
            "repairtarget", "repairfield", "resurrect",
            "beacon", "thermo"
        ]
        
        for i in range(8):
            skill_group = QGroupBox(f"Slot {i+1} (Key {i+1})")
            skill_layout = QHBoxLayout()
            
            combo = ModernComboBox()
            combo.addItems(all_skills)
            combo.setToolTip(f"Select skill for slot {i+1}")
            
            current_skill = self.current_skills[i] if i < len(self.current_skills) and self.current_skills[i] else "(empty)"
            index = combo.findText(current_skill)
            if index >= 0:
                combo.setCurrentIndex(index)
            
            skill_layout.addWidget(combo)
            skill_group.setLayout(skill_layout)
            scroll_layout.addWidget(skill_group)
            
            self.skill_combos.append(combo)
        
        scroll.setWidget(scroll_widget)
        return scroll
    
    def _create_buttons(self):
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        save_btn = QPushButton("Save & Apply")
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {StyleConstants.GRADIENT_GREEN};
                color: {StyleConstants.BG_PRIMARY};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #b4f0b0, stop:1 #a6f0e8);
            }}
        """)
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {StyleConstants.GRADIENT_RED};
                color: {StyleConstants.BG_PRIMARY};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5a0b5, stop:1 #f0b0bb);
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        return button_layout
    
    def get_skills(self):
        """Obtener lista de skills configuradas"""
        skills = []
        for combo in self.skill_combos:
            skill = combo.currentText()
            skills.append("" if skill == "(empty)" else skill)
        return skills


class BotUIWindow(QMainWindow):
    """Ventana principal de la UI del bot - 800x600 (4:3) redimensionable"""
    
    update_signal = pyqtSignal()
    
    def __init__(self, bot_instance):
        super().__init__()
        self.bot = bot_instance
        self.hp_history = deque(maxlen=100)
        self.energy_history = deque(maxlen=100)
        self.start_time = datetime.now()
        self.is_paused = False
        
        # NUEVO: Tracking de crionita inicial
        self.initial_crionita = 0
        self.crionita_loaded = False
        
        self.settings_path = Path(__file__).parent.parent / 'core' / 'settings.json'
        
        self._validate_bot_instance()
        self._init_ui()
        self._start_update_timer()
        
        logger.info("Bot UI initialized successfully")
    
    def _validate_bot_instance(self):
        """Validar que el bot tiene los atributos necesarios"""
        required_attrs = ['skills', 'plr_hp', 'plr_energy', 'state', 'targets', 
                         'healOnHp', 'defendOnHp', 'runOnHp', 'occasionalSkill', 
                         'healCooldown', 'paused', 'stopped']
        
        for attr in required_attrs:
            if not hasattr(self.bot, attr):
                logger.warning(f"Bot instance missing attribute: {attr}")
                setattr(self.bot, attr, None)
    
    def _init_ui(self):
        """Inicializar la interfaz de usuario"""
        self.setWindowTitle('Pirate Galaxy Bot - Dashboard')
        self.setGeometry(200, 100, 800, 600)
        self.setMinimumSize(640, 480)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self._apply_global_style()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        header = self._create_header()
        main_layout.addWidget(header)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        
        left_panel = self._create_status_panel()
        content_layout.addWidget(left_panel, 2)
        
        center_panel = self._create_tabs_panel()
        content_layout.addWidget(center_panel, 3)
        
        right_panel = self._create_monitor_panel()
        content_layout.addWidget(right_panel, 3)
        
        main_layout.addLayout(content_layout, 1)
        
        footer = self._create_controls()
        main_layout.addWidget(footer)
    
    def _apply_global_style(self):
        """Aplicar estilos globales"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {StyleConstants.BG_PRIMARY}, stop:1 {StyleConstants.BG_SECONDARY});
            }}
            QLabel {{
                color: {StyleConstants.TEXT_PRIMARY};
            }}
            QTabWidget::pane {{
                border: 2px solid {StyleConstants.SURFACE_1};
                border-radius: 6px;
                background-color: {StyleConstants.BG_SECONDARY};
                top: -2px;
            }}
            QTabBar::tab {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {StyleConstants.SURFACE_0}, stop:1 #282836);
                color: {StyleConstants.TEXT_SECONDARY};
                padding: 8px 20px;
                margin-right: 3px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                min-width: 60px;
            }}
            QTabBar::tab:selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {StyleConstants.SURFACE_2}, stop:1 {StyleConstants.SURFACE_1});
                color: {StyleConstants.TEXT_PRIMARY};
                border: 2px solid {StyleConstants.BLUE};
                border-bottom: none;
            }}
            QTabBar::tab:hover:!selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {StyleConstants.SURFACE_1}, stop:1 #383a4a);
            }}
            QGroupBox {{
                color: {StyleConstants.BLUE};
                font-size: 13px;
                font-weight: bold;
                border: 2px solid {StyleConstants.SURFACE_1};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {StyleConstants.BG_PRIMARY}, stop:1 {StyleConstants.BG_SECONDARY});
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {StyleConstants.SURFACE_2}, stop:1 {StyleConstants.SURFACE_1});
                color: {StyleConstants.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6c7086, stop:1 {StyleConstants.SURFACE_2});
                border: 2px solid {StyleConstants.BLUE};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {StyleConstants.SURFACE_1}, stop:1 #383a4a);
            }}
            QTextEdit {{
                background-color: {StyleConstants.BG_DARK};
                color: {StyleConstants.TEXT_PRIMARY};
                border: 2px solid {StyleConstants.SURFACE_1};
                border-radius: 6px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                padding: 6px;
            }}
            QProgressBar {{
                border: 2px solid {StyleConstants.SURFACE_1};
                border-radius: 8px;
                text-align: center;
                background-color: {StyleConstants.BG_DARK};
                color: {StyleConstants.TEXT_PRIMARY};
                font-weight: bold;
                font-size: 12px;
            }}
            QProgressBar::chunk {{
                border-radius: 6px;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QToolTip {{
                background-color: {StyleConstants.SURFACE_0};
                color: {StyleConstants.TEXT_PRIMARY};
                border: 2px solid {StyleConstants.SURFACE_1};
                border-radius: 4px;
                padding: 4px;
            }}
        """)
    
    def _create_header(self):
        """Crear header compacto"""
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet(f"""
            QFrame {{
                background: {StyleConstants.GRADIENT_BLUE};
                border-radius: 8px;
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(15)
        
        logo_label = self._create_logo()
        layout.addWidget(logo_label)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        title = QLabel("PIRATE GALAXY BOT")
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setStyleSheet(f"color: {StyleConstants.BG_DARK};")
        
        subtitle = QLabel("Advanced Automation System v2.0")
        subtitle.setStyleSheet(f"color: {StyleConstants.SURFACE_0}; font-size: 10px; font-weight: bold;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        self.status_label = QLabel("RUNNING")
        self.status_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.status_label.setStyleSheet(f"""
            color: {StyleConstants.BG_DARK};
            background-color: rgba(166, 227, 161, 0.35);
            padding: 6px 15px;
            border-radius: 8px;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        config_regions_btn = QPushButton("⚙️")
        config_regions_btn.setFixedSize(40, 40)
        config_regions_btn.setCursor(Qt.PointingHandCursor)
        config_regions_btn.setToolTip("Configurar regiones de lectura (Crionita, Energía)")
        config_regions_btn.setStyleSheet(f"""
            QPushButton {{
                background: {StyleConstants.SURFACE_1};
                color: {StyleConstants.CYAN};
                border: 2px solid {StyleConstants.SURFACE_1};
                border-radius: 20px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background: {StyleConstants.SURFACE_2};
                border: 2px solid {StyleConstants.CYAN};
            }}
            QPushButton:pressed {{
                background: {StyleConstants.SURFACE_0};
            }}
        """)
        config_regions_btn.clicked.connect(self._open_region_config)
        layout.addWidget(config_regions_btn)
        
        return header
    
    def _create_logo(self):
        """Crear widget de logo"""
        logo_label = QLabel()
        logo_path = Path(__file__).parent.parent / 'data' / 'images' / 'pirategalaxy_skull.png'
        
        if logo_path.exists():
            try:
                pixmap = QPixmap(str(logo_path))
                scaled_pixmap = pixmap.scaled(45, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
            except Exception as e:
                logger.warning(f"Error loading logo: {e}")
                logo_label.setText("PG")
                logo_label.setFont(QFont('Arial', 24, QFont.Bold))
        else:
            logo_label.setText("PG")
            logo_label.setFont(QFont('Arial', 24, QFont.Bold))
        
        logo_label.setStyleSheet(f"color: {StyleConstants.BG_DARK};")
        logo_label.setFixedSize(45, 45)
        logo_label.setAlignment(Qt.AlignCenter)
        
        return logo_label
    
    def _create_status_panel(self):
        """Panel de estado compacto"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        
        hp_group = self._create_hp_widget()
        layout.addWidget(hp_group)
        
        energy_group = self._create_energy_widget()
        layout.addWidget(energy_group)
        
        state_group = self._create_state_widget()
        layout.addWidget(state_group)
        
        stats_group = self._create_stats_widget()
        layout.addWidget(stats_group)
        
        layout.addStretch()
        
        return panel
    
    def _create_hp_widget(self):
        """Crear widget de HP"""
        hp_group = QGroupBox("Health Points")
        hp_layout = QVBoxLayout()
        hp_layout.setSpacing(6)
        
        self.hp_label = QLabel("100")
        self.hp_label.setFont(QFont('Arial', 24, QFont.Bold))
        self.hp_label.setStyleSheet(f"color: {StyleConstants.GREEN};")
        self.hp_label.setAlignment(Qt.AlignCenter)
        hp_layout.addWidget(self.hp_label)
        
        self.hp_bar = QProgressBar()
        self.hp_bar.setRange(0, 100)
        self.hp_bar.setValue(100)
        self.hp_bar.setFormat("%v%")
        self.hp_bar.setFixedHeight(25)
        self.hp_bar.setStyleSheet(f"QProgressBar::chunk {{ background: {StyleConstants.GRADIENT_GREEN}; }}")
        hp_layout.addWidget(self.hp_bar)
        
        hp_group.setLayout(hp_layout)
        return hp_group
    
    def _create_energy_widget(self):
        """Crear widget de Energy"""
        energy_group = QGroupBox("Energy")
        energy_layout = QVBoxLayout()
        energy_layout.setSpacing(6)
        
        self.energy_label = QLabel("15,000")
        self.energy_label.setFont(QFont('Arial', 20, QFont.Bold))
        self.energy_label.setStyleSheet(f"color: {StyleConstants.CYAN};")
        self.energy_label.setAlignment(Qt.AlignCenter)
        energy_layout.addWidget(self.energy_label)
        
        self.energy_bar = QProgressBar()
        self.energy_bar.setRange(0, 22000)
        self.energy_bar.setValue(15000)
        self.energy_bar.setFormat("%v E")
        self.energy_bar.setFixedHeight(25)
        self.energy_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {StyleConstants.CYAN}, stop:1 {StyleConstants.BLUE});
            }}
        """)
        energy_layout.addWidget(self.energy_bar)
        
        energy_group.setLayout(energy_layout)
        return energy_group
    
    def _create_state_widget(self):
        """Crear widget de Bot State"""
        state_group = QGroupBox("Bot Status")
        state_layout = QGridLayout()
        state_layout.setSpacing(8)
        state_layout.setColumnStretch(0, 1)
        state_layout.setColumnStretch(1, 2)
        
        state_label = QLabel("State:")
        state_label.setStyleSheet(f"color: {StyleConstants.TEXT_SECONDARY}; font-size: 11px;")
        self.state_value = QLabel("FARMING")
        self.state_value.setStyleSheet(f"color: {StyleConstants.GREEN}; font-weight: bold; font-size: 12px;")
        state_layout.addWidget(state_label, 0, 0)
        state_layout.addWidget(self.state_value, 0, 1)
        
        target_label = QLabel("Target:")
        target_label.setStyleSheet(f"color: {StyleConstants.TEXT_SECONDARY}; font-size: 11px;")
        self.targets_value = QLabel("—")
        self.targets_value.setStyleSheet(f"color: {StyleConstants.YELLOW}; font-weight: bold; font-size: 12px;")
        state_layout.addWidget(target_label, 1, 0)
        state_layout.addWidget(self.targets_value, 1, 1)
        
        runtime_label = QLabel("Runtime:")
        runtime_label.setStyleSheet(f"color: {StyleConstants.TEXT_SECONDARY}; font-size: 11px;")
        self.runtime_value = QLabel("00:00:00")
        self.runtime_value.setStyleSheet(f"color: {StyleConstants.PURPLE}; font-weight: bold; font-size: 12px;")
        state_layout.addWidget(runtime_label, 2, 0)
        state_layout.addWidget(self.runtime_value, 2, 1)
        
        state_group.setLayout(state_layout)
        return state_group
    
    def _create_stats_widget(self):
        """Crear widget de Session Statistics - MEJORADO CON CRIONITA"""
        stats_group = QGroupBox("Session Stats")
        stats_layout = QGridLayout()
        stats_layout.setSpacing(6)
        stats_layout.setColumnStretch(0, 1)
        stats_layout.setColumnStretch(1, 1)
        
        # Row 0: Kills
        kills_label = QLabel("Kills:")
        kills_label.setStyleSheet(f"color: {StyleConstants.TEXT_SECONDARY}; font-size: 11px;")
        self.kills_value = QLabel("0")
        self.kills_value.setStyleSheet(f"color: {StyleConstants.RED}; font-weight: bold; font-size: 12px;")
        self.kills_value.setAlignment(Qt.AlignRight)
        stats_layout.addWidget(kills_label, 0, 0)
        stats_layout.addWidget(self.kills_value, 0, 1)
        
        # Row 1: Heals
        heals_label = QLabel("Heals:")
        heals_label.setStyleSheet(f"color: {StyleConstants.TEXT_SECONDARY}; font-size: 11px;")
        self.heals_value = QLabel("0")
        self.heals_value.setStyleSheet(f"color: {StyleConstants.GREEN}; font-weight: bold; font-size: 12px;")
        self.heals_value.setAlignment(Qt.AlignRight)
        stats_layout.addWidget(heals_label, 1, 0)
        stats_layout.addWidget(self.heals_value, 1, 1)
        
        # Row 2: Collections
        collections_label = QLabel("Collections:")
        collections_label.setStyleSheet(f"color: {StyleConstants.TEXT_SECONDARY}; font-size: 11px;")
        self.collections_value = QLabel("0")
        self.collections_value.setStyleSheet(f"color: {StyleConstants.TEAL}; font-weight: bold; font-size: 12px;")
        self.collections_value.setAlignment(Qt.AlignRight)
        stats_layout.addWidget(collections_label, 2, 0)
        stats_layout.addWidget(self.collections_value, 2, 1)
        
        # Row 3: Crionita (NUEVO)
        crionita_label = QLabel("Crionita:")
        crionita_label.setStyleSheet(f"color: {StyleConstants.TEXT_SECONDARY}; font-size: 11px;")
        self.crionita_value = QLabel("0 (+0)")
        self.crionita_value.setStyleSheet(f"color: {StyleConstants.CYAN}; font-weight: bold; font-size: 11px;")
        self.crionita_value.setAlignment(Qt.AlignRight)
        self.crionita_value.setToolTip("Formato: Actual (+Ganado en sesión)")
        stats_layout.addWidget(crionita_label, 3, 0)
        stats_layout.addWidget(self.crionita_value, 3, 1)
        
        # Row 4: Low Life Events (NUEVO)
        lowlife_label = QLabel("Low Life:")
        lowlife_label.setStyleSheet(f"color: {StyleConstants.TEXT_SECONDARY}; font-size: 11px;")
        self.lowlife_value = QLabel("0")
        self.lowlife_value.setStyleSheet(f"color: {StyleConstants.YELLOW}; font-weight: bold; font-size: 12px;")
        self.lowlife_value.setAlignment(Qt.AlignRight)
        self.lowlife_value.setToolTip("Veces que la vida bajó de 30%")
        stats_layout.addWidget(lowlife_label, 4, 0)
        stats_layout.addWidget(self.lowlife_value, 4, 1)
        
        stats_group.setLayout(stats_layout)
        return stats_group
    
    def _create_tabs_panel(self):
        """Panel con tabs de configuración"""
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        
        preset_tab = self._create_preset_tab()
        tabs.addTab(preset_tab, "Skills")
        
        combat_tab = self._create_combat_tab()
        tabs.addTab(combat_tab, "Combat")
        
        settings_tab = self._create_settings_tab()
        tabs.addTab(settings_tab, "Settings")
        
        return tabs
    
    def _create_preset_tab(self):
        """Tab de skill presets compacto"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        preset_group = QGroupBox("Skill Preset Selection")
        preset_layout = QVBoxLayout()
        
        selector_layout = QHBoxLayout()
        preset_label = QLabel("Active Preset:")
        preset_label.setStyleSheet(f"font-size: 12px; color: {StyleConstants.TEXT_PRIMARY};")
        
        self.preset_combo = ModernComboBox()
        self.preset_combo.setToolTip("Select a skill preset")
        presets = self._load_presets()
        self.preset_combo.addItems(list(presets.keys()))
        current_preset = self._get_current_preset_name()
        index = self.preset_combo.findText(current_preset)
        if index >= 0:
            self.preset_combo.setCurrentIndex(index)
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        
        selector_layout.addWidget(preset_label)
        selector_layout.addWidget(self.preset_combo, 1)
        preset_layout.addLayout(selector_layout)
        
        self.edit_custom_btn = QPushButton("Edit Custom Preset")
        self.edit_custom_btn.setFixedHeight(38)
        self.edit_custom_btn.setCursor(Qt.PointingHandCursor)
        self.edit_custom_btn.setToolTip("Customize your skill configuration")
        self.edit_custom_btn.setStyleSheet(f"""
            QPushButton {{
                background: {StyleConstants.GRADIENT_YELLOW};
                color: {StyleConstants.BG_PRIMARY};
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fcedb5, stop:1 #f9d5b5);
                border: 2px solid {StyleConstants.YELLOW};
            }}
        """)
        self.edit_custom_btn.clicked.connect(self._open_skill_editor)
        preset_layout.addWidget(self.edit_custom_btn)
        
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        skills_group = QGroupBox("Current Configuration")
        skills_layout = QVBoxLayout()
        
        self.current_skills_label = QLabel("")
        self.current_skills_label.setStyleSheet(f"""
            color: {StyleConstants.TEXT_PRIMARY};
            font-size: 11px;
            background-color: {StyleConstants.BG_DARK};
            padding: 12px;
            border-radius: 6px;
            border: 2px solid {StyleConstants.SURFACE_1};
        """)
        self.current_skills_label.setWordWrap(True)
        skills_layout.addWidget(self.current_skills_label)
        self._update_skills_display()
        
        skills_group.setLayout(skills_layout)
        layout.addWidget(skills_group)
        
        layout.addStretch()
        return widget
    
    def _create_settings_tab(self):
        """Tab de configuración general"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        region_group = QGroupBox("Screen Region Configuration")
        region_layout = QVBoxLayout()
        
        info_label = QLabel(
            "Configure screen reading positions for different resolutions.\n"
            "Required for: Crionita tracking, Energy monitoring, etc."
        )
        info_label.setStyleSheet(f"""
            color: {StyleConstants.TEXT_PRIMARY};
            font-size: 11px;
            background-color: {StyleConstants.BG_DARK};
            padding: 12px;
            border-radius: 6px;
            border: 2px solid {StyleConstants.SURFACE_1};
        """)
        info_label.setWordWrap(True)
        region_layout.addWidget(info_label)
        
        screen_width, screen_height = pyautogui.size()
        resolution_info = QLabel(f"Current Resolution: {screen_width}x{screen_height}")
        resolution_info.setStyleSheet(f"""
            color: {StyleConstants.CYAN};
            font-size: 12px;
            font-weight: bold;
            padding: 8px;
        """)
        resolution_info.setAlignment(Qt.AlignCenter)
        region_layout.addWidget(resolution_info)
        
        open_config_btn = QPushButton("🎯 Open Region Configuration Tool")
        open_config_btn.setFixedHeight(50)
        open_config_btn.setCursor(Qt.PointingHandCursor)
        open_config_btn.setToolTip("Configure Crionita, Energy, and other screen regions")
        open_config_btn.setStyleSheet(f"""
            QPushButton {{
                background: {StyleConstants.GRADIENT_BLUE};
                color: {StyleConstants.BG_DARK};
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #a0dcf0, stop:0.5 #a0c4ff, stop:1 #d5c0ff);
            }}
            QPushButton:pressed {{
                background: {StyleConstants.SURFACE_2};
            }}
        """)
        open_config_btn.clicked.connect(self._open_region_config)
        region_layout.addWidget(open_config_btn)
        
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {StyleConstants.BG_DARK};
                border-radius: 6px;
                border: 2px solid {StyleConstants.SURFACE_1};
                padding: 10px;
            }}
        """)
        status_layout = QVBoxLayout(status_frame)
        
        status_title = QLabel("Configured Regions:")
        status_title.setStyleSheet(f"color: {StyleConstants.TEXT_SECONDARY}; font-size: 11px; font-weight: bold;")
        status_layout.addWidget(status_title)
        
        config_status = self._check_region_configuration()
        for region, configured in config_status.items():
            status_text = f"{'✅' if configured else '❌'} {region.capitalize()}"
            status_label = QLabel(status_text)
            status_label.setStyleSheet(f"""
                color: {StyleConstants.GREEN if configured else StyleConstants.RED};
                font-size: 11px;
                padding: 3px;
            """)
            status_layout.addWidget(status_label)
        
        region_layout.addWidget(status_frame)
        region_group.setLayout(region_layout)
        layout.addWidget(region_group)
        
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout()
        
        info_text = QLabel(
            "<b>Note:</b> After configuring regions, restart the bot for changes to take effect.\n\n"
            "<b>When to reconfigure:</b>\n"
            "• Changed screen resolution\n"
            "• Changed display scaling\n"
            "• Switched to different monitor\n"
            "• Game UI layout changed"
        )
        info_text.setStyleSheet(f"""
            color: {StyleConstants.TEXT_PRIMARY};
            font-size: 10px;
            background-color: {StyleConstants.BG_DARK};
            padding: 10px;
            border-radius: 6px;
            border: 2px solid {StyleConstants.SURFACE_1};
        """)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        return widget
    
    def _check_region_configuration(self):
        """Verificar qué regiones están configuradas"""
        config_status = {
            'crionita': False,
            'energy': False
        }
        
        try:
            if not self.settings_path.exists():
                return config_status
            
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            screen_width, screen_height = pyautogui.size()
            resolution_key = f"{screen_width}x{screen_height}"
            
            if 'stats_config' in settings:
                config = settings['stats_config']
                
                if 'crionita_region' in config:
                    if resolution_key in config['crionita_region']:
                        config_status['crionita'] = True
                
                if 'energy_region' in config:
                    if resolution_key in config['energy_region']:
                        config_status['energy'] = True
                        
        except Exception as e:
            logger.error(f"Error checking region configuration: {e}")
        
        return config_status
    
    def _create_combat_tab(self):
        """Tab de combat profiles compacto"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        profile_group = QGroupBox("Combat Profile Selection")
        profile_layout = QVBoxLayout()
        
        selector_layout = QHBoxLayout()
        profile_label = QLabel("Active Profile:")
        profile_label.setStyleSheet(f"font-size: 12px; color: {StyleConstants.TEXT_PRIMARY};")
        
        self.profile_combo = ModernComboBox()
        self.profile_combo.setToolTip("Select combat behavior")
        self.profile_combo.addItems(['Aggressive', 'Balanced', 'Defensive', 'Spam'])
        self.profile_combo.setCurrentText('Balanced')
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        
        selector_layout.addWidget(profile_label)
        selector_layout.addWidget(self.profile_combo, 1)
        profile_layout.addLayout(selector_layout)
        
        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)
        
        info_group = QGroupBox("Profile Settings")
        info_layout = QVBoxLayout()
        
        self.profile_info = QLabel("Heal: 30% | Defend: 45% | Run: 10%")
        self.profile_info.setStyleSheet(f"""
            color: {StyleConstants.TEXT_PRIMARY};
            font-size: 12px;
            background-color: {StyleConstants.BG_DARK};
            padding: 12px;
            border-radius: 6px;
            border: 2px solid {StyleConstants.SURFACE_1};
        """)
        self.profile_info.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.profile_info)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        desc_group = QGroupBox("Profile Descriptions")
        desc_layout = QVBoxLayout()
        
        desc_text = QLabel(
            f"<p style='line-height: 1.6;'>"
            f"<b style='color: {StyleConstants.RED};'>Aggressive:</b> Max damage, minimal healing<br>"
            f"<b style='color: {StyleConstants.GREEN};'>Balanced:</b> Optimal mix of offense/defense<br>"
            f"<b style='color: {StyleConstants.BLUE};'>Defensive:</b> Maximum survivability<br>"
            f"<b style='color: {StyleConstants.PURPLE};'>Spam:</b> Constant skill usage"
            f"</p>"
        )
        desc_text.setStyleSheet(f"""
            color: {StyleConstants.TEXT_PRIMARY};
            font-size: 11px;
            background-color: {StyleConstants.BG_DARK};
            padding: 12px;
            border-radius: 6px;
            border: 2px solid {StyleConstants.SURFACE_1};
        """)
        desc_text.setWordWrap(True)
        desc_layout.addWidget(desc_text)
        
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        layout.addStretch()
        return widget
    
    def _create_monitor_panel(self):
        """Panel de monitoreo compacto"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        chart_group = QGroupBox("Real-Time Monitor")
        chart_layout = QVBoxLayout()
        
        self.chart = self._create_chart()
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setStyleSheet(f"""
            QChartView {{
                background-color: {StyleConstants.BG_DARK};
                border-radius: 6px;
                border: 2px solid {StyleConstants.SURFACE_1};
            }}
        """)
        chart_layout.addWidget(chart_view)
        
        chart_group.setLayout(chart_layout)
        layout.addWidget(chart_group, 2)
        
        log_group = QGroupBox("Event Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group, 1)
        
        return widget
    
    def _create_chart(self):
        """Crear gráfico compacto"""
        chart = QChart()
        chart.setTitle("Status Over Time")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QColor(StyleConstants.BG_DARK))
        chart.setTitleBrush(QColor(StyleConstants.TEXT_PRIMARY))
        chart.setTitleFont(QFont('Arial', 12, QFont.Bold))
        
        self.hp_series = QLineSeries()
        self.hp_series.setName("HP")
        self.hp_series.setColor(QColor(StyleConstants.GREEN))
        pen_hp = self.hp_series.pen()
        pen_hp.setWidth(2)
        self.hp_series.setPen(pen_hp)
        
        self.energy_series = QLineSeries()
        self.energy_series.setName("Energy")
        self.energy_series.setColor(QColor(StyleConstants.CYAN))
        pen_energy = self.energy_series.pen()
        pen_energy.setWidth(2)
        self.energy_series.setPen(pen_energy)
        
        chart.addSeries(self.hp_series)
        chart.addSeries(self.energy_series)
        
        axisX = QValueAxis()
        axisX.setRange(0, 100)
        axisX.setLabelFormat("%d")
        axisX.setLabelsColor(QColor(StyleConstants.TEXT_SECONDARY))
        axisX.setGridLineColor(QColor(StyleConstants.SURFACE_0))
        axisX.setTitleText("Time")
        axisX.setTitleBrush(QColor(StyleConstants.TEXT_SECONDARY))
        
        axisY = QValueAxis()
        axisY.setRange(0, 100)
        axisY.setLabelsColor(QColor(StyleConstants.GREEN))
        axisY.setGridLineColor(QColor(StyleConstants.SURFACE_0))
        axisY.setTitleText("HP (%)")
        axisY.setTitleBrush(QColor(StyleConstants.GREEN))
        
        chart.addAxis(axisX, Qt.AlignBottom)
        chart.addAxis(axisY, Qt.AlignLeft)
        
        self.hp_series.attachAxis(axisX)
        self.hp_series.attachAxis(axisY)
        self.energy_series.attachAxis(axisX)
        
        axisY2 = QValueAxis()
        axisY2.setRange(0, 22000)
        axisY2.setLabelsColor(QColor(StyleConstants.CYAN))
        axisY2.setGridLineColor(QColor(StyleConstants.SURFACE_0))
        axisY2.setTitleText("Energy")
        axisY2.setTitleBrush(QColor(StyleConstants.CYAN))
        chart.addAxis(axisY2, Qt.AlignRight)
        self.energy_series.attachAxis(axisY2)
        
        chart.legend().setLabelColor(QColor(StyleConstants.TEXT_PRIMARY))
        chart.legend().setBackgroundVisible(True)
        chart.legend().setColor(QColor(StyleConstants.BG_SECONDARY))
        chart.legend().setBorderColor(QColor(StyleConstants.SURFACE_1))
        
        return chart
    
    def _create_controls(self):
        """Footer compacto con controles + Energy Loading"""
        footer = QFrame()
        footer.setFixedHeight(60)
        footer.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {StyleConstants.SURFACE_0}, stop:1 #282836);
                border-radius: 8px;
                border: 2px solid {StyleConstants.SURFACE_1};
            }}
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        self.pause_btn = QPushButton("PAUSE")
        self.pause_btn.setFixedHeight(40)
        self.pause_btn.setCursor(Qt.PointingHandCursor)
        self.pause_btn.setToolTip("Pause bot execution (Hotkey: P)")
        self.pause_btn.setStyleSheet(f"""
            QPushButton {{
                background: {StyleConstants.GRADIENT_YELLOW};
                color: {StyleConstants.BG_PRIMARY};
                font-size: 14px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fcedb5, stop:1 #f9d5b5);
                border: 2px solid {StyleConstants.YELLOW};
            }}
        """)
        self.pause_btn.clicked.connect(self._toggle_pause)
        
        self.energy_btn = QPushButton("⚡ LOAD ENERGY")
        self.energy_btn.setFixedHeight(40)
        self.energy_btn.setCursor(Qt.PointingHandCursor)
        self.energy_btn.setToolTip("Toggle Energy Loading (Hotkey: E)")
        self.energy_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {StyleConstants.CYAN}, stop:1 {StyleConstants.BLUE});
                color: {StyleConstants.BG_PRIMARY};
                font-size: 13px;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #a0f0ff, stop:1 #a0c4ff);
                border: 2px solid {StyleConstants.CYAN};
            }}
            QPushButton:pressed {{
                background: {StyleConstants.SURFACE_2};
            }}
        """)
        self.energy_btn.clicked.connect(self._start_energy_loading)
        
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setToolTip("Stop bot completely (Hotkey: Q)")
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background: {StyleConstants.GRADIENT_RED};
                color: {StyleConstants.BG_PRIMARY};
                font-size: 14px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5a0b5, stop:1 #f0b0bb);
                border: 2px solid {StyleConstants.RED};
            }}
        """)
        self.stop_btn.clicked.connect(self._stop_bot)
        
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.energy_btn)
        layout.addWidget(self.stop_btn)
        
        return footer
    
    def _load_presets(self):
        """Cargar presets desde settings.json"""
        try:
            if not self.settings_path.exists():
                logger.warning(f"Settings file not found: {self.settings_path}")
                return {"custom": [""]*8}
            
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get('presets', {"custom": [""]*8})
        except Exception as e:
            logger.error(f"Error loading presets: {e}")
            return {"custom": [""]*8}
    
    def _get_current_preset_name(self):
        """Obtener nombre del preset actual"""
        try:
            if not self.settings_path.exists():
                return 'custom'
            
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get('skillset', 'custom')
        except Exception as e:
            logger.error(f"Error getting preset name: {e}")
            return 'custom'
    
    def _update_skills_display(self):
        """Actualizar display de skills"""
        try:
            skills = self.bot.skills if hasattr(self.bot, 'skills') else [""]*8
            
            skills_formatted = []
            for i, skill in enumerate(skills[:8]):
                skill_name = skill if skill else "<i>(empty)</i>"
                skills_formatted.append(f"<b>[{i+1}]</b> {skill_name}")
            
            col1 = "<br>".join(skills_formatted[:4])
            col2 = "<br>".join(skills_formatted[4:8])
            
            html = f"""
            <table width="100%" cellpadding="4">
            <tr>
            <td width="50%" valign="top" style="padding-right: 8px;">{col1}</td>
            <td width="50%" valign="top">{col2}</td>
            </tr>
            </table>
            """
            
            self.current_skills_label.setText(html)
        except Exception as e:
            logger.error(f"Error updating skills display: {e}")
    
    def _on_preset_changed(self, preset_name):
        """Cambiar preset"""
        try:
            presets = self._load_presets()
            
            if preset_name not in presets:
                self._log(f"Preset not found: {preset_name}")
                return
            
            self.bot.skills = presets[preset_name]
            
            if self.settings_path.exists():
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                settings['skillset'] = preset_name
                
                with open(self.settings_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=4)
            
            self._log(f"Preset changed to: {preset_name}")
            self._update_skills_display()
            
        except Exception as e:
            logger.error(f"Error changing preset: {e}")
            self._log(f"Error changing preset: {str(e)}")
    
    def _open_skill_editor(self):
        """Abrir editor de skills"""
        try:
            dialog = SkillEditorDialog(self.bot.skills, self)
            
            if dialog.exec_() == QDialog.Accepted:
                new_skills = dialog.get_skills()
                
                if len(new_skills) != 8:
                    self._log("Invalid skills configuration")
                    return
                
                self.bot.skills = new_skills
                
                if self.settings_path.exists():
                    with open(self.settings_path, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    
                    settings['presets']['custom'] = new_skills
                    settings['skillset'] = 'custom'
                    
                    with open(self.settings_path, 'w', encoding='utf-8') as f:
                        json.dump(settings, f, indent=4)
                
                self.preset_combo.setCurrentText('custom')
                self._log("Custom preset updated successfully")
                self._update_skills_display()
                
        except Exception as e:
            logger.error(f"Error opening skill editor: {e}")
            self._log(f"Error: {str(e)}")
    
    def _on_profile_changed(self, profile_name):
        """Cambiar perfil de combate"""
        try:
            profile_map = {
                'Aggressive': 'aggressive',
                'Balanced': 'balanced',
                'Defensive': 'defensive',
                'Spam': 'spam'
            }
            
            profile_key = profile_map.get(profile_name, 'balanced')
            
            if hasattr(self.bot, 'apply_combat_profile'):
                if self.bot.apply_combat_profile(profile_key):
                    self._log(f"Combat profile: {profile_name}")
                    
                    heal = getattr(self.bot, 'healOnHp', 30)
                    defend = getattr(self.bot, 'defendOnHp', 45)
                    run = getattr(self.bot, 'runOnHp', 10)
                    skill_freq = getattr(self.bot, 'occasionalSkill', 4)
                    heal_cd = getattr(self.bot, 'healCooldown', 10)
                    
                    info_html = f"""
                    <center style='padding: 8px;'>
                    <p style='font-size: 13px; margin: 4px;'>
                    <b style='color: {StyleConstants.GREEN};'>Heal:</b> {heal}% &nbsp;
                    <b style='color: {StyleConstants.YELLOW};'>Defend:</b> {defend}% &nbsp;
                    <b style='color: {StyleConstants.RED};'>Run:</b> {run}%
                    </p>
                    <p style='color: {StyleConstants.CYAN}; font-size: 11px; margin: 4px;'>
                    Skill freq: 1/{skill_freq} | Heal CD: {heal_cd}s
                    </p>
                    </center>
                    """
                    self.profile_info.setText(info_html)
                else:
                    self._log(f"Failed to apply profile: {profile_name}")
            else:
                self._log("Bot doesn't support combat profiles")
                
        except Exception as e:
            logger.error(f"Error changing profile: {e}")
            self._log(f"Error changing profile: {str(e)}")
    
    def _start_update_timer(self):
        """Iniciar timer de actualización"""
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_ui)
        self.timer.start(500)
    
    def _update_ui(self):
        """Actualizar toda la UI - MEJORADO CON STATS"""
        try:
            if not hasattr(self.bot, 'plr_hp'):
                return
            
            # HP
            hp = max(0, min(100, self.bot.plr_hp or 0))
            self.hp_label.setText(f"{hp}")
            self.hp_bar.setValue(hp)
            
            if hp > 60:
                hp_color = StyleConstants.GREEN
                hp_gradient = StyleConstants.GRADIENT_GREEN
            elif hp > 30:
                hp_color = StyleConstants.YELLOW
                hp_gradient = StyleConstants.GRADIENT_YELLOW
            else:
                hp_color = StyleConstants.RED
                hp_gradient = StyleConstants.GRADIENT_RED
            
            self.hp_label.setStyleSheet(f"color: {hp_color};")
            self.hp_bar.setStyleSheet(f"QProgressBar::chunk {{ background: {hp_gradient}; }}")
            
            # Energy
            energy = max(0, self.bot.plr_energy or 0)
            self.energy_label.setText(f"{energy:,}")
            self.energy_bar.setValue(min(energy, 22000))
            self.energy_bar.setFormat(f"{energy:,} E")
            
            # State
            states = {0: "INIT", 1: "FARMING", 2: "FLEEING"}
            state_text = states.get(self.bot.state, "UNKNOWN")
            self.state_value.setText(state_text)
            
            state_colors = {
                "INIT": StyleConstants.CYAN,
                "FARMING": StyleConstants.GREEN,
                "FLEEING": StyleConstants.RED
            }
            self.state_value.setStyleSheet(
                f"color: {state_colors.get(state_text, StyleConstants.TEXT_PRIMARY)}; "
                f"font-weight: bold; font-size: 12px;"
            )
            
            # Targets
            if hasattr(self.bot, 'targets') and self.bot.targets:
                target_type = self.bot.targets[2] if len(self.bot.targets) > 2 else "unknown"
                self.targets_value.setText(f"{target_type.upper()}")
            else:
                self.targets_value.setText("—")
            
            # Runtime
            runtime = datetime.now() - self.start_time
            hours, remainder = divmod(int(runtime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.runtime_value.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # Chart
            self.hp_history.append(hp)
            self.energy_history.append(energy)
            
            self.hp_series.clear()
            self.energy_series.clear()
            
            for i, value in enumerate(self.hp_history):
                self.hp_series.append(i, value)
            
            for i, value in enumerate(self.energy_history):
                self.energy_series.append(i, value)
            
            # ===== ESTADÍSTICAS DE SESIÓN =====
            if hasattr(self.bot, 'session_stats'):
                stats = self.bot.session_stats
                
                # Kills
                self.kills_value.setText(str(stats.get('kills', 0)))
                
                # Heals
                self.heals_value.setText(str(stats.get('heals', 0)))
                
                # Collections
                self.collections_value.setText(str(stats.get('collections', 0)))
                
                # Crionita - con tracking inicial
                current_crionita = stats.get('crionita', 0)
                
                if not self.crionita_loaded and current_crionita > 0:
                    self.initial_crionita = current_crionita
                    self.crionita_loaded = True
                
                gained = current_crionita - self.initial_crionita if self.crionita_loaded else 0
                
                if gained > 0:
                    self.crionita_value.setText(f"{current_crionita:,} (+{gained:,})")
                    self.crionita_value.setStyleSheet(f"color: {StyleConstants.CYAN}; font-weight: bold; font-size: 11px;")
                elif gained < 0:
                    self.crionita_value.setText(f"{current_crionita:,} ({gained:,})")
                    self.crionita_value.setStyleSheet(f"color: {StyleConstants.RED}; font-weight: bold; font-size: 11px;")
                else:
                    self.crionita_value.setText(f"{current_crionita:,}")
                    self.crionita_value.setStyleSheet(f"color: {StyleConstants.TEXT_SECONDARY}; font-weight: bold; font-size: 11px;")
                
                # Low Life
                self.lowlife_value.setText(str(stats.get('lowlife', 0)))
                
        except Exception as e:
            logger.error(f"Error updating UI: {e}")
    
    def _toggle_pause(self):
        """Toggle pausa"""
        try:
            self.is_paused = not self.is_paused
            
            if hasattr(self.bot, 'paused'):
                self.bot.paused = self.is_paused
            
            if self.is_paused:
                self.pause_btn.setText("RESUME")
                self.pause_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {StyleConstants.GRADIENT_GREEN};
                        color: {StyleConstants.BG_PRIMARY};
                        font-size: 14px;
                        border-radius: 8px;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #b4f0b0, stop:1 #a6f0e8);
                        border: 2px solid {StyleConstants.GREEN};
                    }}
                """)
                self.status_label.setText("PAUSED")
                self.status_label.setStyleSheet(f"""
                    color: {StyleConstants.BG_DARK};
                    background-color: rgba(249, 226, 175, 0.4);
                    padding: 6px 15px;
                    border-radius: 8px;
                """)
                self._log("Bot paused")
            else:
                self.pause_btn.setText("PAUSE")
                self.pause_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {StyleConstants.GRADIENT_YELLOW};
                        color: {StyleConstants.BG_PRIMARY};
                        font-size: 14px;
                        border-radius: 8px;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #fcedb5, stop:1 #f9d5b5);
                        border: 2px solid {StyleConstants.YELLOW};
                    }}
                """)
                self.status_label.setText("RUNNING")
                self.status_label.setStyleSheet(f"""
                    color: {StyleConstants.BG_DARK};
                    background-color: rgba(166, 227, 161, 0.35);
                    padding: 6px 15px;
                    border-radius: 8px;
                """)
                self._log("Bot resumed")
                
        except Exception as e:
            logger.error(f"Error toggling pause: {e}")
    
    def _start_energy_loading(self):
        """Toggle modo de carga infinita de energía"""
        try:
            if hasattr(self.bot, 'toggle_energy_loading'):
                is_active = self.bot.toggle_energy_loading()
                
                if is_active:
                    self.energy_btn.setText("⚡ LOADING...")
                    self.energy_btn.setStyleSheet(f"""
                        QPushButton {{
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {StyleConstants.GREEN}, stop:1 {StyleConstants.TEAL});
                            color: {StyleConstants.BG_PRIMARY};
                            font-size: 13px;
                            border-radius: 8px;
                            font-weight: bold;
                            border: 2px solid {StyleConstants.GREEN};
                        }}
                        QPushButton:hover {{
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #b4f0b0, stop:1 #a6f0e8);
                        }}
                    """)
                    self._log("⚡ Energy Loading: ACTIVADO (Presiona E o el botón para desactivar)")
                else:
                    self.energy_btn.setText("⚡ LOAD ENERGY")
                    self.energy_btn.setStyleSheet(f"""
                        QPushButton {{
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {StyleConstants.CYAN}, stop:1 {StyleConstants.BLUE});
                            color: {StyleConstants.BG_PRIMARY};
                            font-size: 13px;
                            border-radius: 8px;
                            font-weight: bold;
                        }}
                        QPushButton:hover {{
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #a0f0ff, stop:1 #a0c4ff);
                            border: 2px solid {StyleConstants.CYAN};
                        }}
                    """)
                    self._log("⚡ Energy Loading: DESACTIVADO")
            else:
                self._log("❌ Bot no soporta energy loading")
                
        except Exception as e:
            logger.error(f"Error toggling energy loading: {e}")
            self._log(f"Error: {str(e)}")
    
    def _stop_bot(self):
        """Detener el bot"""
        try:
            reply = QMessageBox.question(
                self,
                'Confirm Stop',
                'Are you sure you want to stop the bot?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if hasattr(self.bot, 'stop'):
                    self.bot.stop()
                
                self.status_label.setText("STOPPED")
                self.status_label.setStyleSheet(f"""
                    color: {StyleConstants.BG_DARK};
                    background-color: rgba(243, 139, 168, 0.4);
                    padding: 6px 15px;
                    border-radius: 8px;
                """)
                self._log("Bot stopped by user")
                
                QTimer.singleShot(1000, QApplication.quit)
                
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
    
    def _open_region_config(self):
        """Abrir herramienta de configuración de regiones"""
        try:
            import subprocess
            import sys
            
            config_tool_path = Path(__file__).parent / 'crionita_config_tool.py'
            
            if not config_tool_path.exists():
                QMessageBox.warning(
                    self,
                    'Tool Not Found',
                    f'Configuration tool not found at:\n{config_tool_path}\n\n'
                    'Make sure crionita_config_tool.py is in the same directory.'
                )
                return
            
            reply = QMessageBox.question(
                self,
                'Open Configuration Tool',
                '🎯 Region Configuration Tool\n\n'
                'This tool allows you to configure screen reading positions for:\n'
                '  • Crionita counter\n'
                '  • Energy value\n\n'
                'The configuration window will open. Configure the regions and save.\n'
                'The bot will automatically use the new settings on restart.\n\n'
                'Open the configuration tool now?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                if sys.platform == 'win32':
                    subprocess.Popen([sys.executable, str(config_tool_path)], 
                                   creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    subprocess.Popen([sys.executable, str(config_tool_path)])
                
                self._log("Region configuration tool opened")
                
        except Exception as e:
            logger.error(f"Error opening region config tool: {e}")
            QMessageBox.critical(
                self,
                'Error',
                f'Failed to open configuration tool:\n{str(e)}'
            )
    
    def log(self, message):
        """Agregar mensaje al log (método público para uso externo)"""
        self._log(message)
    
    def _log(self, message):
        """Agregar mensaje al log"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if "success" in message.lower() or "started" in message.lower() or "iniciado" in message.lower():
                color = StyleConstants.GREEN
            elif "warning" in message.lower() or "paused" in message.lower() or "pausado" in message.lower():
                color = StyleConstants.YELLOW
            elif "error" in message.lower() or "stopped" in message.lower():
                color = StyleConstants.RED
            elif "combat" in message.lower() or "profile" in message.lower() or "curación" in message.lower():
                color = StyleConstants.BLUE
            else:
                color = StyleConstants.CYAN
            
            formatted_msg = (
                f'<span style="color: {StyleConstants.TEXT_SECONDARY};">[{timestamp}]</span> '
                f'<span style="color: {color};">{message}</span>'
            )
            
            self.log_text.append(formatted_msg)
            
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
        except Exception as e:
            logger.error(f"Error logging message: {e}")
    
    def closeEvent(self, event):
        """Manejo de cierre de ventana"""
        try:
            reply = QMessageBox.question(
                self,
                'Close Application',
                'Are you sure you want to close the bot?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if hasattr(self.bot, 'stop'):
                    self.bot.stop()
                event.accept()
            else:
                event.ignore()
                
        except Exception as e:
            logger.error(f"Error in closeEvent: {e}")
            event.accept()


def main():
    """Función principal para testing"""
    
    class MockBot:
        """Bot mock para testing"""
        def __init__(self):
            self.skills = ["blaster", "rocket", "shield", "repair", "", "", "", ""]
            self.plr_hp = 75
            self.plr_energy = 15000
            self.state = 1
            self.targets = [0, 0, "enemy"]
            self.healOnHp = 30
            self.defendOnHp = 45
            self.runOnHp = 10
            self.occasionalSkill = 4
            self.healCooldown = 10
            self.paused = False
            self.stopped = False
            self.session_stats = {
                'kills': 42,
                'heals': 15,
                'collections': 87,
                'crionita': 45320,
                'lowlife': 3
            }
        
        def apply_combat_profile(self, profile):
            profiles = {
                'aggressive': (20, 35, 5, 2, 15),
                'balanced': (30, 45, 10, 4, 10),
                'defensive': (50, 60, 20, 6, 8),
                'spam': (25, 40, 8, 1, 12)
            }
            
            if profile in profiles:
                self.healOnHp, self.defendOnHp, self.runOnHp, self.occasionalSkill, self.healCooldown = profiles[profile]
                return True
            return False
        
        def stop(self):
            self.stopped = True
            logger.info("Bot stopped")
        
        def toggle_energy_loading(self):
            return True
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    bot = MockBot()
    window = BotUIWindow(bot)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()