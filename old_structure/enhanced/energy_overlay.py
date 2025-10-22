"""
Energy Orb Overlay - Superposición transparente para mostrar detección de orbes
"""

from PyQt5.QtWidgets import QWidget, QApplication, QLabel
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QBrush
import sys


class EnergyOverlay(QWidget):
    """Ventana overlay transparente para mostrar detección de orbes"""
    
    def __init__(self):
        super().__init__()
        self.orbs = []
        self.collected_total = 0
        self.cycle = 0
        
        self._init_ui()
    
    def _init_ui(self):
        """Inicializar UI del overlay"""
        # Ventana sin bordes, transparente, siempre encima
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool |
            Qt.WindowTransparentForInput  # Permite clicks atravesar la ventana
        )
        
        # Hacer ventana transparente
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        # Tamaño de pantalla completa
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(screen)
        
        # Timer para actualizar
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(100)  # Actualizar cada 100ms
    
    def set_orbs(self, orbs, collected, cycle):
        """Actualizar lista de orbes detectados"""
        self.orbs = orbs
        self.collected_total = collected
        self.cycle = cycle
        self.update()
    
    def paintEvent(self, event):
        """Dibujar overlay"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Dibujar cada orbe
        for i, orb in enumerate(self.orbs[:10], 1):  # Máximo 10 orbes visibles
            x = orb['x']
            y = orb['y']
            radius = max(orb['radius'], 25)
            
            # Tamaño del cuadro
            box_size = radius * 2 + 20
            
            # Color según posición
            if i == 1:
                # Orbe #1 (siguiente a recolectar) - Verde brillante
                border_color = QColor(0, 255, 0)
                fill_color = QColor(0, 255, 0, 40)
                border_width = 4
            elif i == 2:
                # Orbe #2 - Amarillo
                border_color = QColor(255, 255, 0)
                fill_color = QColor(255, 255, 0, 30)
                border_width = 3
            else:
                # Resto - Cyan
                border_color = QColor(0, 255, 255)
                fill_color = QColor(0, 255, 255, 20)
                border_width = 2
            
            # Dibujar cuadro
            pen = QPen(border_color, border_width)
            painter.setPen(pen)
            painter.setBrush(QBrush(fill_color))
            
            rect = QRect(
                x - box_size // 2,
                y - box_size // 2,
                box_size,
                box_size
            )
            painter.drawRect(rect)
            
            # Dibujar número
            font = QFont('Arial', 24 if i <= 2 else 18, QFont.Bold)
            painter.setFont(font)
            
            # Fondo del número
            number_bg_rect = QRect(x - 20, y - box_size // 2 - 35, 40, 35)
            painter.setBrush(QBrush(QColor(0, 0, 0, 180)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(number_bg_rect, 5, 5)
            
            # Texto del número
            painter.setPen(QPen(border_color))
            painter.drawText(
                number_bg_rect,
                Qt.AlignCenter,
                str(i)
            )
            
            # Información adicional para los primeros 2
            if i <= 2:
                info_text = f"R:{radius}px"
                painter.setFont(QFont('Arial', 10, QFont.Bold))
                info_rect = QRect(x - 30, y + box_size // 2 + 5, 60, 20)
                painter.setPen(QPen(QColor(255, 255, 255)))
                painter.drawText(info_rect, Qt.AlignCenter, info_text)
        
        # Dibujar panel de información (esquina superior izquierda)
        self._draw_info_panel(painter)
    
    def _draw_info_panel(self, painter):
        """Dibujar panel de información"""
        # Fondo del panel
        panel_rect = QRect(10, 10, 280, 100)
        painter.setBrush(QBrush(QColor(30, 30, 46, 200)))
        painter.setPen(QPen(QColor(137, 180, 250), 2))
        painter.drawRoundedRect(panel_rect, 10, 10)
        
        # Texto
        painter.setFont(QFont('Arial', 12, QFont.Bold))
        painter.setPen(QPen(QColor(137, 220, 235)))
        
        y_offset = 30
        painter.drawText(QPoint(20, y_offset), "⚡ ENERGY LOADING ACTIVE")
        
        painter.setFont(QFont('Arial', 10))
        painter.setPen(QPen(QColor(205, 214, 244)))
        
        y_offset += 25
        painter.drawText(QPoint(20, y_offset), f"Orbs Detected: {len(self.orbs)}")
        
        y_offset += 20
        painter.drawText(QPoint(20, y_offset), f"Collected: {self.collected_total}")
        
        y_offset += 20
        painter.drawText(QPoint(20, y_offset), f"Cycle: {self.cycle}")
        
        # Leyenda de colores
        legend_y = 120
        painter.setFont(QFont('Arial', 9))
        
        # Verde = Next
        painter.setBrush(QBrush(QColor(0, 255, 0)))
        painter.drawRect(10, legend_y, 15, 15)
        painter.drawText(QPoint(30, legend_y + 12), "1st - Next Target")
        
        # Amarillo = 2nd
        legend_y += 20
        painter.setBrush(QBrush(QColor(255, 255, 0)))
        painter.drawRect(10, legend_y, 15, 15)
        painter.drawText(QPoint(30, legend_y + 12), "2nd - Queued")
        
        # Cyan = Resto
        legend_y += 20
        painter.setBrush(QBrush(QColor(0, 255, 255)))
        painter.drawRect(10, legend_y, 15, 15)
        painter.drawText(QPoint(30, legend_y + 12), "Others - Detected")
    
    def close_overlay(self):
        """Cerrar overlay"""
        self.update_timer.stop()
        self.close()


# Para testing standalone
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    overlay = EnergyOverlay()
    overlay.show()
    
    # Simular orbes de prueba
    test_orbs = [
        {'x': 500, 'y': 300, 'radius': 30},
        {'x': 700, 'y': 400, 'radius': 25},
        {'x': 600, 'y': 500, 'radius': 28},
        {'x': 800, 'y': 350, 'radius': 22},
    ]
    
    overlay.set_orbs(test_orbs, 15, 42)
    
    sys.exit(app.exec_())