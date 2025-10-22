"""
Detection Module
Contains OCR, energy detection, and position tracking
"""

from .energy_detector import EnergyDetector
from .position_tracker import PositionTracker

try:
    from .ocr_enhanced import EnhancedOCR
    __all__ = ['EnergyDetector', 'PositionTracker', 'EnhancedOCR']
except ImportError:
    __all__ = ['EnergyDetector', 'PositionTracker']
