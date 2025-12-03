# ML Model Integration

This folder contains the ML model integration for human detection in the H.A.R.C. system.

## 📁 Folder Structure

```
ml/
├── __init__.py          # Module initialization
├── model_loader.py      # Model loading and management
├── detector.py          # Human detection using ML model
├── README.md           # This file
└── models/             # Place your trained model here
    └── .gitkeep
```

## 🎯 Quick Start

1. **Place your trained model file** in the `ml/models/` directory:
   ```bash
   cp /path/to/your/model.pth backend/ml/models/
   ```

2. **Supported model formats:**
   - PyTorch: `.pth`, `.pt`
   - TensorFlow: `.h5`, `.pb`, `.savedmodel`
   - ONNX: `.onnx`
   - OpenCV DNN: `.onnx`, `.pb`, `.tflite`
   - Darknet/YOLO: `.weights` (requires `.cfg` file)

3. **The system will automatically:**
   - Detect your model file
   - Load it on startup
   - Use it for human detection

## 🔧 Model Requirements

### Input Format
- **Image format**: RGB or BGR (automatically handled)
- **Input size**: Default is 640x640 (configurable)
- **Data format**: Base64 encoded image data URI

### Output Format
The model should output detections in one of these formats:

1. **OpenCV DNN format**: `[batch, num_detections, 7]`
   - Format: `[batch_id, class_id, confidence, x1, y1, x2, y2]`

2. **PyTorch YOLO format**: `[batch, num_detections, 6]`
   - Format: `[x_center, y_center, width, height, confidence, class_id]`

3. **TensorFlow format**: Standard TensorFlow detection output

### Class IDs
- Class ID `0` = Person (human)
- Other class IDs will be filtered out

## 📝 Usage Example

```python
from ml.detector import HumanDetector

# Initialize detector (automatically loads model from ml/models/)
detector = HumanDetector()

# Check if model is loaded
if detector.is_ready():
    # Detect humans in image
    image_data_uri = "data:image/jpeg;base64,..."
    detections = detector.detect(image_data_uri)
    
    for detection in detections:
        print(f"Human detected: {detection.confidence}% confidence")
        print(f"Bounding box: {detection.boundingBox}")
```

## ⚙️ Configuration

You can configure the detector in `model_loader.py`:

```python
# Set input size
detector.model_loader.set_input_size(640, 640)

# Set confidence threshold (0.0 to 1.0)
detector.model_loader.set_confidence_threshold(0.5)

# Set NMS threshold (0.0 to 1.0)
detector.model_loader.set_nms_threshold(0.4)
```

## 🔗 Integration

The ML model is automatically integrated with:
- `AIService` - Uses ML model for human detection
- `AutoTargetingService` - Uses ML detections for automated targeting

## 📦 Dependencies

The ML module uses:
- **OpenCV** (already installed) - For image processing and DNN inference
- **NumPy** (already installed) - For array operations
- **Pillow** (already installed) - For image handling

Optional (install if needed):
- **PyTorch**: `pip install torch` (for `.pth`, `.pt` models)
- **TensorFlow**: `pip install tensorflow` (for `.h5`, `.pb` models)

## 🐛 Troubleshooting

### Model not found
- Ensure your model file is in `backend/ml/models/`
- Check file permissions
- Verify file extension is supported

### Model loading error
- Check model format compatibility
- Install required dependencies (PyTorch/TensorFlow)
- Verify model file is not corrupted

### Low detection accuracy
- Adjust confidence threshold: `set_confidence_threshold(0.3)` for more detections
- Adjust NMS threshold: `set_nms_threshold(0.5)` to reduce overlapping boxes
- Verify model input size matches your model's expected input

### Performance issues
- Use GPU acceleration if available (PyTorch/TensorFlow GPU versions)
- Reduce input image size
- Use ONNX format for faster inference with OpenCV DNN

## 📚 Model Training Notes

If you're training your own model:

1. **Dataset**: Use human detection datasets (COCO, Pascal VOC, custom)
2. **Classes**: Ensure "person" class is class ID 0
3. **Export**: Export in one of the supported formats
4. **Testing**: Test model inference before deployment

## 🔒 Security

- Model files are loaded locally (no external API calls)
- All processing happens offline
- No data is sent to external services

