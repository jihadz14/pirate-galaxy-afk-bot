"""
UI Module
Contains graphical user interface components
"""

try:
    from .bot_window import BotUIWindow
    from .energy_overlay import EnergyOverlay
    __all__ = ['BotUIWindow', 'EnergyOverlay']
except ImportError:
    # PyQt5 might not be installed
    __all__ = []
