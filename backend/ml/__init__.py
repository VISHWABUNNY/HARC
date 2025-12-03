"""
ML Module for Human Detection

This module handles loading and using trained ML models for human detection.
Place your trained model file in the ml/models/ directory.
"""

from .model_loader import ModelLoader, ModelType
from .detector import HumanDetector

__all__ = ['ModelLoader', 'ModelType', 'HumanDetector']

