"""
Cleanup Planning Agent

Orchestrates the full workflow from image analysis to actionable cleanup plans.
"""

from typing import Optional, Any
from PIL import Image
import base64
from io import BytesIO

from tools.trash_detection_tool import detect_trash_mcp, format_detections_for_display
from tools.cleanup_planner_tool import plan_cleanup
from tools.history_tool import log_event, get_hotspots
from tools.report_generator_tool import generate_report
from trash_model import Detection


def run_cleanup_workflow(
    image: Image.Image,
    location: Optional[str] = None,
    notes: Optional[str] = None,
    save_to_history: bool = True,
    use_llm_enhancement: bool = False,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
):
    """
    Execute the complete cleanup workflow for a trash detection event.
    
    This is the main orchestration function that:
    1. Detects trash in the image
    2. Plans cleanup actions
    3. Optionally logs to history
    4. Generates reports
    5. Returns all results for UI display
    
    Args:
        image: PIL Image to analyze
        location: Optional location description
        notes: Optional user notes
        save_to_history: Whether to log event to database
        use_llm_enhancement: Whether to use LLM for enhanced text generation
        latitude: Optional GPS latitude
        longitude: Optional GPS longitude
    
    Returns:
        Dict containing:
            - detection_results: Raw detection data
            - plan: Cleanup plan
            - report: Generated report text
            - event_id: Database ID (if saved)
            - visualization_data: Data for UI overlay
            - summary: Human-readable summary
    """
    # Step 1: Detect trash
    print("🔍 Step 1: Detecting trash in image...")
    
    # Convert image to base64 for tool (simulating MCP data format)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode()
    
    detection_result = detect_trash_mcp(img_b64)
    detections: list[Detection] = detection_result["detections"]
    
    print(f"   Found {detection_result['count']} items")
    
    if not detections:
        return {
            "detection_results": detection_result,
            "plan": None,
            "report": None,
            "event_id": None,
            "visualization_data": None,
            "summary": "No trash detected in this image. The area appears clean!",
            "status": "no_trash"
        }
    
    # Step 2: Plan cleanup
    print("📋 Step 2: Planning cleanup actions...")
    plan = plan_cleanup(
        detections,
        location=location,
        notes=notes,
        use_llm=use_llm_enhancement
    )
    print(f"   Severity: {plan['severity']}, Volunteers: {plan['recommended_volunteers']}")
    
    # Step 3: Log to history (if requested)
    event_id = None
    if save_to_history:
        print("💾 Step 3: Logging event to history...")
        log_result = log_event(
            detections=detections,
            severity=plan["severity"],
            location=location,
            notes=notes,
            image_path=None,  # Could save image file here
            latitude=latitude,
            longitude=longitude
        )
        event_id = log_result["event_id"]
        print(f"   Saved as event #{event_id}")
    
    # Step 4: Generate report
    print("📄 Step 4: Generating report...")
    report_result = generate_report(
        detections=detections,
        severity=plan["severity"],
        location=location,
        notes=notes,
        event_id=event_id,
        plan=plan,
        format="email"
    )
    report_text = report_result["report"]
    
    # Step 5: Prepare visualization data
    visualization_data = _prepare_visualization_data(image, detections)
    
    # Step 6: Create summary
    summary = _create_workflow_summary(detection_result, plan, event_id)
    
    print("✅ Workflow complete!")
    
    return {
        "detection_results": detection_result,
        "plan": plan,
        "report": report_text,
        "event_id": event_id,
        "visualization_data": visualization_data,
        "summary": summary,
        "status": "success"
    }


def _prepare_visualization_data(image: Image.Image, detections: list[Detection]):
    """Prepare data for drawing bounding boxes on image."""
    return {
        "image_size": {"width": image.width, "height": image.height},
        "boxes": [
            {
                "bbox": det["bbox"],
                "label": det["label"],
                "score": det["score"],
                "color": _get_color_for_label(det["label"])
            }
            for det in detections
        ]
    }


def _get_color_for_label(label: str) -> str:
    """Get consistent color for trash category."""
    color_map = {
        "plastic_bottle": "#FF6B6B",
        "plastic_bag": "#4ECDC4",
        "food_wrapper": "#FFD93D",
        "cigarette_butt": "#95E1D3",
        "paper_cup": "#F38181",
        "aluminum_can": "#AA96DA",
        "food_container": "#FCBAD3",
        "cardboard_box": "#A8D8EA",
        "glass_bottle": "#FFA07A",
        "other_trash": "#B0B0B0"
    }
    return color_map.get(label, "#FF0000")


def _create_workflow_summary(
    detection_result,
    plan,
    event_id: Optional[int]
) -> str:
    """Create human-readable workflow summary."""
    count = detection_result["count"]
    categories = detection_result["categories"]
    severity = plan["severity"]
    volunteers = plan["recommended_volunteers"]
    time = plan["estimated_time_minutes"]
    
    category_text = ", ".join(categories[:3])
    if len(categories) > 3:
        category_text += f" and {len(categories) - 3} more"
    
    summary = f"""**Analysis Complete**

Detected **{count} trash items** across {len(categories)} categories ({category_text}).

**Severity:** {severity.upper()}

**Recommended Action:**
- {volunteers} volunteer(s) needed
- Approximately {time} minutes
- Action within {plan['urgency_days']} day(s)
"""
    
    if event_id:
        summary += f"\n✓ Event saved to history (ID: {event_id})"
    
    return summary


def analyze_hotspots(days: int = 30):
    """
    Analyze trash hotspots from historical data.
    
    Args:
        days: Time window for analysis
    
    Returns:
        Hotspot analysis with recommendations
    """
    hotspots_data = get_hotspots(min_events=2, days=days)
    
    if not hotspots_data["hotspots"]:
        return {
            "hotspots": [],
            "message": f"No recurring hotspots found in the last {days} days.",
            "recommendation": "Continue monitoring and logging new events."
        }
    
    # Analyze hotspots
    top_hotspot = hotspots_data["hotspots"][0]
    
    recommendation = f"""**Hotspot Alert**

{hotspots_data['count']} location(s) with recurring trash issues identified.

**Top Problem Area:** {top_hotspot['location']}
- {top_hotspot['event_count']} events recorded
- {top_hotspot['total_trash']} total items
- Last event: {top_hotspot['last_event']}

**Recommendation:** Consider setting up regular cleanup schedule or requesting permanent waste receptacles for this location.
"""
    
    return {
        "hotspots": hotspots_data["hotspots"],
        "count": hotspots_data["count"],
        "recommendation": recommendation,
        "top_hotspot": top_hotspot
    }
