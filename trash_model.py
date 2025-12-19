"""
Trash Detection Model Wrapper

This module provides an interface for trash detection in images using YOLOv8.
Loads a trained model from Weights/best.pt for real trash detection.
"""

from typing import TypedDict
from PIL import Image
from pathlib import Path
import numpy as np
import os

# Import YOLO from ultralytics
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️  Ultralytics not available. Install with: pip install ultralytics")


class Detection(TypedDict):
    """Single trash detection result."""
    bbox: list[float]  # [x1, y1, x2, y2] in pixels
    label: str         # Trash category
    score: float       # Confidence score (0-1)


# Global model instance (loaded once)
_model = None

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
DEFAULT_MODEL_PATH = SCRIPT_DIR / "Weights" / "best.pt"


def load_model(model_path: str = None) -> YOLO:
    """
    Load the YOLOv8 trash detection model.
    
    Args:
        model_path: Path to the model weights file (if None, uses default)
        
    Returns:
        Loaded YOLO model instance
    """
    global _model
    
    if _model is None:
        if not YOLO_AVAILABLE:
            raise ImportError("Ultralytics not installed. Run: pip install ultralytics")
        
        # Use default path if none provided
        if model_path is None:
            model_file = DEFAULT_MODEL_PATH
        else:
            model_file = Path(model_path)
            # If relative path provided, make it relative to script directory
            if not model_file.is_absolute():
                model_file = SCRIPT_DIR / model_file
        
        if not model_file.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_file}\n"
                f"Expected location: {DEFAULT_MODEL_PATH}\n"
                f"Current directory: {os.getcwd()}"
            )
        
        print(f"🔄 Loading YOLO model from {model_file}...")
        _model = YOLO(str(model_file))
        print(f"✅ Model loaded successfully!")
        print(f"   Classes: {_model.names}")
    
    return _model


def detect_trash(image: Image.Image, conf_threshold: float = 0.25) -> list[Detection]:
    """
    Detect trash objects in an image using YOLOv8.
    
    Args:
        image: PIL Image to analyze
        conf_threshold: Confidence threshold for detections (0-1)
        
    Returns:
        List of detections with bounding boxes, labels, and confidence scores
    """
    try:
        # Load model (only happens once)
        model = load_model()
        
        # Run inference
        results = model(image, conf=conf_threshold, verbose=False)
        
        # Parse results
        detections: list[Detection] = []
        
        # Get the first result (single image)
        if len(results) > 0:
            result = results[0]
            
            # Extract boxes, classes, and scores
            if result.boxes is not None and len(result.boxes) > 0:
                boxes = result.boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
                confidences = result.boxes.conf.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy().astype(int)
                
                # Convert to Detection format
                for box, conf, cls_id in zip(boxes, confidences, class_ids):
                    # Get class name
                    label = model.names[cls_id]
                    
                    detection: Detection = {
                        "bbox": box.tolist(),  # [x1, y1, x2, y2]
                        "label": label,
                        "score": float(conf)
                    }
                    detections.append(detection)
        
        return detections
    
    except Exception as e:
        print(f"❌ Error during detection: {e}")
        print("   Falling back to empty detection list")
        return []


def get_model_info():
    """Get information about the loaded model."""
    try:
        model = load_model()
        return {
            "model_type": "YOLOv8",
            "classes": model.names,
            "num_classes": len(model.names),
            "model_path": "Weights/best.pt"
        }
    except Exception as e:
        return {
            "error": str(e),
            "model_type": "None",
            "status": "Model not loaded"
        }
