"""
Self-Evolving AI Module

Komponen untuk membuat aplikasi AI yang dapat belajar dan berkembang
secara mandiri melalui feedback loop otomatis.
"""

from .data_collector import DataCollector

try:
    from .evaluator import Evaluator
except Exception:
    Evaluator = None

try:
    from .retrainer import AutoRetrain
except Exception:
    AutoRetrain = None

try:
    from .app import SelfEvolvingApp
except Exception:
    SelfEvolvingApp = None

__all__ = ['DataCollector', 'Evaluator', 'AutoRetrain', 'SelfEvolvingApp']
__version__ = '1.0.0'
