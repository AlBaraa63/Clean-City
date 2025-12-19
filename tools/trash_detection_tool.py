"""
Trash Detection MCP Tool

Wraps the trash detection model for use as an MCP tool.
"""

from typing import Any
from PIL import Image
import base64
from io import BytesIO
import json

from trash_model import detect_trash, Detection


def detect_trash_mcp(image_data: str | dict):
    """
    MCP tool wrapper for trash detection.
    
    Args:
        image_data: Either:
            - Base64 encoded image string
            - Dict with 'path' key pointing to image file
            - Dict with 'base64' key containing base64 image
    
    Returns:
        Dict containing:
            - detections: List of trash objects found
            - count: Total number of items detected
            - categories: Unique trash categories found
            - summary: Human-readable summary
    """
    # Parse input
    image = _load_image_from_input(image_data)
    
    # Run detection
    detections = detect_trash(image)
    
    # Analyze results
    categories = list(set(d["label"] for d in detections))
    avg_confidence = sum(d["score"] for d in detections) / len(detections) if detections else 0
    
    summary = f"Detected {len(detections)} trash items across {len(categories)} categories. "
    summary += f"Average confidence: {avg_confidence:.1%}"
    
    return {
        "detections": detections,
        "count": len(detections),
        "categories": categories,
        "average_confidence": avg_confidence,
        "summary": summary,
        "image_dimensions": {"width": image.width, "height": image.height}
    }


def _load_image_from_input(image_data: str | dict) -> Image.Image:
    """Load PIL Image from various input formats."""
    if isinstance(image_data, str):
        # Assume base64 encoded
        if image_data.startswith('data:image'):
            # Remove data URL prefix
            image_data = image_data.split(',', 1)[1]
        image_bytes = base64.b64decode(image_data)
        return Image.open(BytesIO(image_bytes))
    
    elif isinstance(image_data, dict):
        if 'path' in image_data:
            return Image.open(image_data['path'])
        elif 'base64' in image_data:
            image_bytes = base64.b64decode(image_data['base64'])
            return Image.open(BytesIO(image_bytes))
    
    raise ValueError("Invalid image_data format. Provide base64 string or dict with 'path' or 'base64' key")


def format_detections_for_display(detections: list[Detection]) -> str:
    """Format detection results as readable text."""
    if not detections:
        return "No trash detected in the image."
    
    lines = [f"Found {len(detections)} trash items:\n"]
    
    # Group by category
    by_category = {}
    for det in detections:
        category = det["label"]
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(det)
    
    for category, items in sorted(by_category.items()):
        avg_conf = sum(d["score"] for d in items) / len(items)
        lines.append(f"  • {category}: {len(items)} item(s) (confidence: {avg_conf:.1%})")
    
    return "\n".join(lines)
