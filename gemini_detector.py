"""
Google Gemini Vision - Trash Detection Module

Uses Gemini's multimodal capabilities to detect and describe trash in images.
Complements YOLOv8 with natural language understanding and detailed analysis.
"""

import os
from typing import Dict, List, Optional
from PIL import Image
import base64
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()


class GeminiVisionDetector:
    """Trash detection using Google Gemini Vision API."""
    
    def __init__(self):
        """Initialize Gemini Vision detector."""
        self.enabled = False
        self.model = None
        
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.enabled = True
                print("✓ Gemini Vision detector initialized")
            except ImportError:
                print("⚠ Google GenAI package not installed (pip install google-generativeai)")
            except Exception as e:
                print(f"⚠ Gemini Vision initialization failed: {e}")
        else:
            print("ℹ Gemini Vision disabled (no GEMINI_API_KEY)")
    
    def detect_trash(self, image: Image.Image) -> Dict:
        """
        Detect trash items in image using Gemini Vision.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with detection results:
            {
                'items': List[str],  # List of detected items
                'count': int,         # Total item count
                'description': str,   # Detailed description
                'severity': str,      # LOW, MEDIUM, HIGH
                'categories': Dict    # Category counts
            }
        """
        if not self.enabled:
            return self._offline_fallback()
        
        try:
            # Create prompt for Gemini
            prompt = """Analyze this image for trash and litter. Provide a detailed analysis:

1. List all visible trash items (be specific: "plastic bottle", "cigarette butt", not just "trash")
2. Estimate the total number of items
3. Categorize items (plastic, paper, metal, organic, other)
4. Assess severity (LOW: 1-5 items, MEDIUM: 6-15 items, HIGH: 16+ items)
5. Describe the location/context

Format your response as:
ITEMS: item1, item2, item3, ...
COUNT: <number>
CATEGORIES: plastic:<count>, paper:<count>, metal:<count>, organic:<count>, other:<count>
SEVERITY: <LOW|MEDIUM|HIGH>
DESCRIPTION: <1-2 sentence description>"""

            # Generate response
            response = self.model.generate_content([prompt, image])
            
            # Parse response
            return self._parse_gemini_response(response.text)
            
        except Exception as e:
            print(f"⚠ Gemini Vision detection failed: {e}")
            return self._offline_fallback()
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse Gemini's structured response."""
        lines = response_text.strip().split('\n')
        
        result = {
            'items': [],
            'count': 0,
            'description': '',
            'severity': 'MEDIUM',
            'categories': {}
        }
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('ITEMS:'):
                items_str = line.replace('ITEMS:', '').strip()
                result['items'] = [item.strip() for item in items_str.split(',')]
            
            elif line.startswith('COUNT:'):
                try:
                    result['count'] = int(line.replace('COUNT:', '').strip())
                except:
                    result['count'] = len(result['items'])
            
            elif line.startswith('CATEGORIES:'):
                cats_str = line.replace('CATEGORIES:', '').strip()
                for cat_pair in cats_str.split(','):
                    if ':' in cat_pair:
                        cat, count = cat_pair.split(':')
                        try:
                            result['categories'][cat.strip()] = int(count.strip())
                        except:
                            pass
            
            elif line.startswith('SEVERITY:'):
                severity = line.replace('SEVERITY:', '').strip().upper()
                if severity in ['LOW', 'MEDIUM', 'HIGH']:
                    result['severity'] = severity
            
            elif line.startswith('DESCRIPTION:'):
                result['description'] = line.replace('DESCRIPTION:', '').strip()
        
        return result
    
    def _offline_fallback(self) -> Dict:
        """Return mock results when Gemini is not available."""
        return {
            'items': ['plastic bottle', 'food wrapper', 'paper cup'],
            'count': 3,
            'description': 'Gemini Vision not configured. Using mock detection.',
            'severity': 'MEDIUM',
            'categories': {
                'plastic': 2,
                'paper': 1
            }
        }
    
    def compare_with_yolo(self, yolo_results: Dict, gemini_results: Dict) -> str:
        """
        Generate comparison between YOLOv8 and Gemini detections.
        
        Args:
            yolo_results: Results from YOLOv8 detector
            gemini_results: Results from Gemini Vision
            
        Returns:
            Formatted comparison text
        """
        # Safely extract YOLO counts
        if isinstance(yolo_results, dict):
            yolo_count = yolo_results.get('total_items', 0)
            if yolo_count == 0 and 'detections' in yolo_results:
                yolo_count = len(yolo_results.get('detections', []))
            yolo_categories = list(yolo_results.get('categories', {}).keys())
            yolo_confidence = yolo_results.get('avg_confidence', 0)
        else:
            # yolo_results might be a list of detections
            yolo_count = len(yolo_results) if isinstance(yolo_results, list) else 0
            yolo_categories = []
            yolo_confidence = 0
        
        comparison = f"""
🔍 **Dual-Engine Detection Comparison**

**YOLOv8 (Computer Vision):**
- Detected: {yolo_count} items
- Categories: {', '.join(yolo_categories) if yolo_categories else 'Multiple types'}
- Confidence: {yolo_confidence:.1f}%

**Gemini Vision (Multimodal AI):**
- Detected: {gemini_results['count']} items
- Categories: {', '.join(gemini_results['categories'].keys())}
- Severity: {gemini_results['severity']}
- Context: {gemini_results['description']}

**Insights:**
{self._generate_insights(yolo_count, yolo_confidence, gemini_results)}
"""
        return comparison.strip()
    
    def _generate_insights(self, yolo_count: int, yolo_confidence: float, gemini: Dict) -> str:
        """Generate insights from comparing both detections."""
        insights = []
        
        # Compare counts
        gemini_count = gemini['count']
        
        if abs(yolo_count - gemini_count) <= 2:
            insights.append("✓ Both models agree on item count")
        else:
            insights.append(f"⚠ Count difference: YOLOv8={yolo_count}, Gemini={gemini_count}")
        
        # Highlight Gemini's advantage
        if gemini['description']:
            insights.append(f"💡 Gemini provides context: \"{gemini['description']}\"")
        
        # Highlight YOLOv8's advantage
        if yolo_confidence > 80:
            insights.append(f"🎯 YOLOv8 provides precise bounding boxes ({yolo_confidence:.0f}% confidence)")
        elif yolo_confidence > 0:
            insights.append(f"📍 YOLOv8 provides precise bounding boxes")
        
        return '\n'.join(insights) if insights else "Both models detected trash successfully"


# Global instance
_gemini_detector = None

def get_gemini_detector() -> GeminiVisionDetector:
    """Get singleton Gemini detector instance."""
    global _gemini_detector
    if _gemini_detector is None:
        _gemini_detector = GeminiVisionDetector()
    return _gemini_detector
