"""
Human Detector using ML Model

Processes images and detects humans using the loaded ML model.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import base64
from PIL import Image
import io

from .model_loader import ModelLoader, ModelType
from app.models.tracking import HumanDetection, BoundingBox, Coordinates, Movement

class HumanDetector:
    """Detect humans in images using ML model."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize human detector.
        
        Args:
            model_path: Path to trained model file
        """
        self.model_loader = ModelLoader(model_path)
        self.model = self.model_loader.model
        self.model_type = self.model_loader.model_type
        
    def is_ready(self) -> bool:
        """Check if detector is ready (model loaded)."""
        return self.model_loader.is_loaded()
    
    def _decode_image(self, image_data_uri: str) -> Optional[np.ndarray]:
        """
        Decode base64 image data URI to numpy array.
        
        Args:
            image_data_uri: Base64 encoded image (data:image/jpeg;base64,...)
        
        Returns:
            Image as numpy array (BGR format for OpenCV)
        """
        try:
            # Remove data URI prefix
            if ',' in image_data_uri:
                header, encoded = image_data_uri.split(',', 1)
            else:
                encoded = image_data_uri
            
            # Decode base64
            image_data = base64.b64decode(encoded)
            
            # Convert to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            
            # Decode image
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                print("⚠️  Failed to decode image")
                return None
            
            return img
        except Exception as e:
            print(f"❌ Error decoding image: {e}")
            return None
    
    def _preprocess_image(self, image: np.ndarray) -> Tuple[np.ndarray, float, float]:
        """
        Preprocess image for model input.
        
        Args:
            image: Input image (BGR format)
        
        Returns:
            Tuple of (preprocessed_image, scale_x, scale_y)
        """
        # Get model input size
        input_width, input_height = self.model_loader.input_size
        
        # Get original dimensions
        orig_height, orig_width = image.shape[:2]
        
        # Resize image to model input size
        resized = cv2.resize(image, (input_width, input_height))
        
        # Calculate scale factors for converting back to original coordinates
        scale_x = orig_width / input_width
        scale_y = orig_height / input_height
        
        # Normalize pixel values (0-255 to 0-1)
        normalized = resized.astype(np.float32) / 255.0
        
        # Convert to blob format for OpenCV DNN
        if self.model_type == ModelType.OPENCV_DNN:
            blob = cv2.dnn.blobFromImage(
                normalized,
                scalefactor=1.0,
                size=(input_width, input_height),
                mean=(0, 0, 0),
                swapRB=True,  # BGR to RGB
                crop=False
            )
            return blob, scale_x, scale_y
        
        # For PyTorch/TensorFlow, return as is (may need additional preprocessing)
        return normalized, scale_x, scale_y
    
    def _postprocess_detections(
        self,
        outputs: np.ndarray,
        scale_x: float,
        scale_y: float,
        image_width: int,
        image_height: int
    ) -> List[Dict[str, Any]]:
        """
        Post-process model outputs to extract detections.
        
        Args:
            outputs: Raw model outputs
            scale_x: Scale factor for x coordinates
            scale_y: Scale factor for y coordinates
            image_width: Original image width
            image_height: Original image height
        
        Returns:
            List of detection dictionaries with bounding boxes and confidence
        """
        detections = []
        confidence_threshold = self.model_loader.confidence_threshold
        
        # Handle different output formats
        if self.model_type == ModelType.OPENCV_DNN:
            # OpenCV DNN output format: [batch, num_detections, 7]
            # Format: [batch_id, class_id, confidence, x1, y1, x2, y2]
            if len(outputs.shape) == 3:
                outputs = outputs[0]  # Remove batch dimension
            
            for detection in outputs:
                if len(detection) >= 7:
                    _, class_id, confidence, x1, y1, x2, y2 = detection[:7]
                    
                    if confidence >= confidence_threshold:
                        # Scale coordinates back to original image size
                        x1 = int(x1 * scale_x)
                        y1 = int(y1 * scale_y)
                        x2 = int(x2 * scale_x)
                        y2 = int(y2 * scale_y)
                        
                        # Ensure coordinates are within image bounds
                        x1 = max(0, min(x1, image_width))
                        y1 = max(0, min(y1, image_height))
                        x2 = max(0, min(x2, image_width))
                        y2 = max(0, min(y2, image_height))
                        
                        width = x2 - x1
                        height = y2 - y1
                        
                        if width > 0 and height > 0:
                            detections.append({
                                "bbox": (x1, y1, width, height),
                                "confidence": float(confidence),
                                "class_id": int(class_id)
                            })
        
        elif self.model_type == ModelType.PYTORCH:
            # PyTorch YOLO format: [batch, num_detections, 6]
            # Format: [x_center, y_center, width, height, confidence, class_id]
            if len(outputs.shape) == 3:
                outputs = outputs[0]
            
            for detection in outputs:
                if len(detection) >= 6:
                    x_center, y_center, w, h, conf, class_id = detection[:6]
                    
                    if conf >= confidence_threshold:
                        # Convert center coordinates to top-left
                        x1 = int((x_center - w/2) * scale_x)
                        y1 = int((y_center - h/2) * scale_y)
                        width = int(w * scale_x)
                        height = int(h * scale_y)
                        
                        x1 = max(0, min(x1, image_width))
                        y1 = max(0, min(y1, image_height))
                        width = min(width, image_width - x1)
                        height = min(height, image_height - y1)
                        
                        if width > 0 and height > 0:
                            detections.append({
                                "bbox": (x1, y1, width, height),
                                "confidence": float(conf),
                                "class_id": int(class_id)
                            })
        
        # Apply Non-Maximum Suppression (NMS)
        if detections:
            detections = self._apply_nms(detections)
        
        return detections
    
    def _apply_nms(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply Non-Maximum Suppression to remove overlapping detections."""
        if not detections:
            return []
        
        # Extract bounding boxes and scores
        boxes = []
        scores = []
        
        for det in detections:
            x, y, w, h = det["bbox"]
            boxes.append([x, y, x + w, y + h])
            scores.append(det["confidence"])
        
        boxes = np.array(boxes, dtype=np.float32)
        scores = np.array(scores, dtype=np.float32)
        
        # Apply NMS
        indices = cv2.dnn.NMSBoxes(
            boxes.tolist(),
            scores.tolist(),
            self.model_loader.confidence_threshold,
            self.model_loader.nms_threshold
        )
        
        if len(indices) == 0:
            return []
        
        # Filter detections using NMS indices
        if isinstance(indices, np.ndarray):
            indices = indices.flatten()
        
        filtered_detections = [detections[i] for i in indices]
        
        return filtered_detections
    
    def detect(self, image_data_uri: str) -> List[HumanDetection]:
        """
        Detect humans in image.
        
        Args:
            image_data_uri: Base64 encoded image data URI
        
        Returns:
            List of HumanDetection objects
        """
        if not self.is_ready():
            print("⚠️  Model not loaded. Returning empty detections.")
            return []
        
        # Decode image
        image = self._decode_image(image_data_uri)
        if image is None:
            return []
        
        image_height, image_width = image.shape[:2]
        
        # Preprocess image
        preprocessed, scale_x, scale_y = self._preprocess_image(image)
        
        # Run inference
        try:
            if self.model_type == ModelType.OPENCV_DNN:
                self.model.setInput(preprocessed)
                outputs = self.model.forward()
            elif self.model_type == ModelType.PYTORCH:
                import torch
                with torch.no_grad():
                    if isinstance(preprocessed, np.ndarray):
                        preprocessed = torch.from_numpy(preprocessed).unsqueeze(0)
                    outputs = self.model(preprocessed)
                    if isinstance(outputs, torch.Tensor):
                        outputs = outputs.numpy()
            elif self.model_type == ModelType.TENSORFLOW:
                import tensorflow as tf
                outputs = self.model.predict(preprocessed)
                if isinstance(outputs, tf.Tensor):
                    outputs = outputs.numpy()
            else:
                print(f"⚠️  Unsupported model type for inference: {self.model_type}")
                return []
            
            # Post-process detections
            raw_detections = self._postprocess_detections(
                outputs,
                scale_x,
                scale_y,
                image_width,
                image_height
            )
            
            # Convert to HumanDetection objects
            human_detections = []
            for i, det in enumerate(raw_detections):
                x, y, w, h = det["bbox"]
                
                # Only include "person" class (class_id 0 typically)
                class_id = det.get("class_id", 0)
                if class_id != 0:  # Skip non-person detections
                    continue
                
                bbox = BoundingBox(x=x, y=y, width=w, height=h)
                
                # Calculate center coordinates (for GPS if available)
                center_x = x + w / 2
                center_y = y + h / 2
                coordinates = Coordinates(
                    latitude=0.0,  # Would need calibration for real GPS
                    longitude=0.0
                )
                
                # Create detection
                detection = HumanDetection(
                    id=f"human_{i+1}",
                    boundingBox=bbox,
                    coordinates=coordinates,
                    confidence=det["confidence"] * 100,  # Convert to percentage
                    distance=None,  # Would need depth estimation
                    temperature=None,  # Would need thermal data
                    movement=None  # Would need tracking over time
                )
                
                human_detections.append(detection)
            
            return human_detections
            
        except Exception as e:
            print(f"❌ Error during inference: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return self.model_loader.get_model_info()

