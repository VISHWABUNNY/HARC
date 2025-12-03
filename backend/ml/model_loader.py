"""
Model Loader for Human Detection ML Models

Supports multiple model formats:
- PyTorch (.pth, .pt)
- TensorFlow (.h5, .pb, .savedmodel)
- ONNX (.onnx)
- OpenCV DNN (.onnx, .pb, .tflite)
"""

import os
import cv2
import numpy as np
from typing import Optional, Union, Dict, Any
from enum import Enum
from pathlib import Path

class ModelType(Enum):
    """Supported model types."""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnx"
    OPENCV_DNN = "opencv_dnn"
    UNKNOWN = "unknown"

class ModelLoader:
    """Load and manage ML models for human detection."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize model loader.
        
        Args:
            model_path: Path to the trained model file. If None, will search in ml/models/
        """
        self.model_path = model_path
        self.model = None
        self.model_type: ModelType = ModelType.UNKNOWN
        self.input_size: tuple = (640, 640)  # Default input size
        self.confidence_threshold: float = 0.5
        self.nms_threshold: float = 0.4
        self.class_names: list = ["person"]  # Default class name
        
        # Find model file if path not provided
        if not self.model_path:
            self.model_path = self._find_model_file()
        
        if self.model_path and os.path.exists(self.model_path):
            self._detect_model_type()
            self._load_model()
    
    def _find_model_file(self) -> Optional[str]:
        """Search for model file in ml/models/ directory."""
        models_dir = Path(__file__).parent / "models"
        
        if not models_dir.exists():
            models_dir.mkdir(parents=True, exist_ok=True)
            return None
        
        # Common model file extensions
        extensions = ['.pth', '.pt', '.onnx', '.h5', '.pb', '.tflite', '.weights']
        
        for ext in extensions:
            for file in models_dir.glob(f"*{ext}"):
                if file.is_file():
                    print(f"✅ Found model file: {file}")
                    return str(file)
        
        print(f"⚠️  No model file found in {models_dir}")
        print(f"   Please place your trained model file in: {models_dir}")
        return None
    
    def _detect_model_type(self):
        """Detect model type from file extension."""
        if not self.model_path:
            return
        
        ext = Path(self.model_path).suffix.lower()
        
        if ext in ['.pth', '.pt']:
            self.model_type = ModelType.PYTORCH
        elif ext in ['.h5', '.pb', '.savedmodel']:
            self.model_type = ModelType.TENSORFLOW
        elif ext == '.onnx':
            self.model_type = ModelType.ONNX
        elif ext == '.tflite':
            self.model_type = ModelType.OPENCV_DNN
        else:
            self.model_type = ModelType.UNKNOWN
        
        print(f"📦 Detected model type: {self.model_type.value}")
    
    def _load_model(self):
        """Load the model based on detected type."""
        if not self.model_path or not os.path.exists(self.model_path):
            print("⚠️  Model file not found. Using fallback detection.")
            return
        
        try:
            if self.model_type == ModelType.PYTORCH:
                self._load_pytorch()
            elif self.model_type == ModelType.TENSORFLOW:
                self._load_tensorflow()
            elif self.model_type == ModelType.ONNX:
                self._load_onnx()
            elif self.model_type == ModelType.OPENCV_DNN:
                self._load_opencv_dnn()
            else:
                print(f"⚠️  Unknown model type. Attempting OpenCV DNN load...")
                self._load_opencv_dnn()
            
            print(f"✅ Model loaded successfully: {self.model_path}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print(f"   Falling back to OpenCV DNN...")
            try:
                self._load_opencv_dnn()
            except Exception as e2:
                print(f"❌ Failed to load model: {e2}")
                self.model = None
    
    def _load_pytorch(self):
        """Load PyTorch model."""
        try:
            import torch
            self.model = torch.load(self.model_path, map_location='cpu')
            self.model.eval() if hasattr(self.model, 'eval') else None
            print("✅ PyTorch model loaded")
        except ImportError:
            print("⚠️  PyTorch not installed. Install with: pip install torch")
            raise
        except Exception as e:
            print(f"❌ Error loading PyTorch model: {e}")
            raise
    
    def _load_tensorflow(self):
        """Load TensorFlow model."""
        try:
            import tensorflow as tf
            self.model = tf.keras.models.load_model(self.model_path)
            print("✅ TensorFlow model loaded")
        except ImportError:
            print("⚠️  TensorFlow not installed. Install with: pip install tensorflow")
            raise
        except Exception as e:
            print(f"❌ Error loading TensorFlow model: {e}")
            raise
    
    def _load_onnx(self):
        """Load ONNX model using OpenCV DNN."""
        try:
            self.model = cv2.dnn.readNetFromONNX(self.model_path)
            self.model_type = ModelType.OPENCV_DNN  # Use OpenCV DNN for inference
            print("✅ ONNX model loaded via OpenCV DNN")
        except Exception as e:
            print(f"❌ Error loading ONNX model: {e}")
            raise
    
    def _load_opencv_dnn(self):
        """Load model using OpenCV DNN (supports ONNX, TensorFlow, Darknet)."""
        try:
            # Try ONNX first
            if self.model_path.endswith('.onnx'):
                self.model = cv2.dnn.readNetFromONNX(self.model_path)
                self.model_type = ModelType.OPENCV_DNN
                print("✅ Model loaded via OpenCV DNN (ONNX)")
            # Try TensorFlow
            elif self.model_path.endswith('.pb'):
                # Need config file for TensorFlow
                config_path = self.model_path.replace('.pb', '.pbtxt')
                if os.path.exists(config_path):
                    self.model = cv2.dnn.readNetFromTensorflow(self.model_path, config_path)
                else:
                    self.model = cv2.dnn.readNetFromTensorflow(self.model_path)
                self.model_type = ModelType.OPENCV_DNN
                print("✅ Model loaded via OpenCV DNN (TensorFlow)")
            # Try Darknet/YOLO
            elif self.model_path.endswith('.weights'):
                config_path = self.model_path.replace('.weights', '.cfg')
                if os.path.exists(config_path):
                    self.model = cv2.dnn.readNetFromDarknet(config_path, self.model_path)
                    self.model_type = ModelType.OPENCV_DNN
                    print("✅ Model loaded via OpenCV DNN (Darknet/YOLO)")
                else:
                    raise FileNotFoundError(f"Config file not found: {config_path}")
            else:
                raise ValueError(f"Unsupported file format for OpenCV DNN: {self.model_path}")
        except Exception as e:
            print(f"❌ Error loading model with OpenCV DNN: {e}")
            raise
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "loaded": self.is_loaded(),
            "model_path": self.model_path,
            "model_type": self.model_type.value,
            "input_size": self.input_size,
            "confidence_threshold": self.confidence_threshold,
            "nms_threshold": self.nms_threshold,
            "class_names": self.class_names
        }
    
    def set_input_size(self, width: int, height: int):
        """Set model input size."""
        self.input_size = (width, height)
    
    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold for detections."""
        self.confidence_threshold = threshold
    
    def set_nms_threshold(self, threshold: float):
        """Set NMS (Non-Maximum Suppression) threshold."""
        self.nms_threshold = threshold

