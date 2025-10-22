"""
Utilities Module
Contains logging and helper functions
"""

try:
    from .logger import BotLogger
    __all__ = ['BotLogger']
except ImportError:
    __all__ = []
