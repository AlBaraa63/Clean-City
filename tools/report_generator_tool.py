"""
Report Generator MCP Tool

Generates formatted reports for trash detection events.
Suitable for city authorities, community groups, or documentation.
"""

from typing import Optional, Any
from datetime import datetime
from trash_model import Detection
import llm_client


def generate_report(
    detections: list[Detection],
    severity: str,
    location: Optional[str] = None,
    notes: Optional[str] = None,
    event_id: Optional[int] = None,
    plan: Optional[Any] = None,
    format: str = "email"
):
    """
    Generate a formatted report for trash detection event.
    
    Args:
        detections: List of trash detections
        severity: Severity level
        location: Location description
        notes: Additional notes
        event_id: Database event ID if logged
        plan: Optional cleanup plan data
        format: "email" | "markdown" | "plain"
    
    Returns:
        Dict with report text and metadata
    """
    if format == "email":
        report_text = _generate_email_report(detections, severity, location, notes, plan)
    elif format == "markdown":
        report_text = _generate_markdown_report(detections, severity, location, notes, event_id, plan)
    else:
        report_text = _generate_plain_report(detections, severity, location, notes, plan)
    
    return {
        "report": report_text,
        "format": format,
        "generated_at": datetime.now().isoformat(),
        "event_id": event_id
    }


def _generate_email_report(
    detections: list[Detection],
    severity: str,
    location: Optional[str],
    notes: Optional[str],
    plan: Optional[Any]
) -> str:
    """Generate email-formatted report for city authorities."""
    location_str = location or "[Location to be specified]"
    date_str = datetime.now().strftime("%B %d, %Y")
    
    # Summarize detections
    categories = list(set(d["label"] for d in detections))
    category_counts = {}
    for det in detections:
        label = det["label"]
        category_counts[label] = category_counts.get(label, 0) + 1
    
    items_list = "\n".join([
        f"  • {label.replace('_', ' ').title()}: {count} item(s)"
        for label, count in sorted(category_counts.items())
    ])
    
    urgency_text = {
        "high": "URGENT - Immediate attention required",
        "medium": "Moderate priority - Action needed within 1-3 days",
        "low": "Low priority - Routine cleanup recommended"
    }
    
    template = f"""Subject: Trash Cleanup Request - {location_str}

Dear City Services / Environmental Department,

I am writing to report significant litter accumulation that requires attention at the following location:

**Location:** {location_str}
**Date Reported:** {date_str}
**Severity Level:** {severity.upper()} ({urgency_text.get(severity, '')})

**Details of Trash Observed:**
Total items detected: {len(detections)}

{items_list}
"""
    
    if notes:
        template += f"\n**Additional Context:**\n{notes}\n"
    
    if plan:
        template += f"""
**Recommended Action:**
- Estimated cleanup time: {plan.get('estimated_time_minutes', 'N/A')} minutes
- Volunteers needed: {plan.get('recommended_volunteers', 'N/A')}
- Equipment required: {', '.join(plan.get('equipment_needed', []))}
- Urgency: Action within {plan.get('urgency_days', 'N/A')} day(s)
"""
    
    template += """
This accumulation poses environmental and health concerns for the community. I would appreciate a timely response regarding cleanup scheduling.

Thank you for your attention to this matter.

Best regards,
[Your Name / Community Group]
[Contact Information]
"""
    
    return template


def _generate_markdown_report(
    detections: list[Detection],
    severity: str,
    location: Optional[str],
    notes: Optional[str],
    event_id: Optional[int],
    plan: Optional[Any]
) -> str:
    """Generate Markdown-formatted report for documentation."""
    location_str = location or "Unspecified location"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Group detections
    category_counts = {}
    for det in detections:
        label = det["label"]
        category_counts[label] = category_counts.get(label, 0) + 1
    
    report = f"""# Trash Detection Report

## Event Information
- **Event ID:** {event_id if event_id else 'Not logged'}
- **Timestamp:** {timestamp}
- **Location:** {location_str}
- **Severity:** {severity.upper()}

## Detection Summary
- **Total Items:** {len(detections)}
- **Unique Categories:** {len(category_counts)}

### Items Breakdown
"""
    
    for label, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        report += f"- **{label.replace('_', ' ').title()}:** {count} item(s)\n"
    
    if plan:
        report += f"""
## Cleanup Plan
- **Recommended Volunteers:** {plan.get('recommended_volunteers', 'N/A')}
- **Estimated Time:** {plan.get('estimated_time_minutes', 'N/A')} minutes
- **Urgency:** Within {plan.get('urgency_days', 'N/A')} day(s)
- **Equipment Needed:** 
"""
        for equipment in plan.get('equipment_needed', []):
            report += f"  - {equipment}\n"
        
        report += f"\n### Environmental Impact\n{plan.get('environmental_impact', 'N/A')}\n"
    
    if notes:
        report += f"\n## Additional Notes\n{notes}\n"
    
    report += "\n---\n*Generated by CleanCity Agent*"
    
    return report


def _generate_plain_report(
    detections: list[Detection],
    severity: str,
    location: Optional[str],
    notes: Optional[str],
    plan: Optional[Any]
) -> str:
    """Generate plain text report."""
    lines = [
        "=" * 60,
        "TRASH DETECTION REPORT",
        "=" * 60,
        "",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Location: {location or 'Unspecified'}",
        f"Severity: {severity.upper()}",
        "",
        f"Total Items Detected: {len(detections)}",
        ""
    ]
    
    # Group items
    category_counts = {}
    for det in detections:
        label = det["label"]
        category_counts[label] = category_counts.get(label, 0) + 1
    
    lines.append("Items by Category:")
    for label, count in sorted(category_counts.items()):
        lines.append(f"  - {label.replace('_', ' ').title()}: {count}")
    
    if plan:
        lines.extend([
            "",
            "Cleanup Recommendations:",
            f"  - Volunteers needed: {plan.get('recommended_volunteers', 'N/A')}",
            f"  - Estimated time: {plan.get('estimated_time_minutes', 'N/A')} minutes",
            f"  - Action within: {plan.get('urgency_days', 'N/A')} day(s)",
            f"  - Equipment: {', '.join(plan.get('equipment_needed', []))}"
        ])
    
    if notes:
        lines.extend(["", "Notes:", notes])
    
    lines.extend(["", "=" * 60])
    
    return "\n".join(lines)


def generate_llm_enhanced_report(
    detections: list[Detection],
    severity: str,
    location: Optional[str] = None,
    notes: Optional[str] = None,
    plan: Optional[Any] = None
) -> str:
    """Use LLM to generate a more sophisticated, context-aware report."""
    context = f"""Trash detection event:
- Location: {location or 'unspecified'}
- Items detected: {len(detections)}
- Severity: {severity}
- Categories: {', '.join(set(d['label'] for d in detections))}
"""
    
    if notes:
        context += f"- Context: {notes}\n"
    
    if plan:
        context += f"- Recommended volunteers: {plan.get('recommended_volunteers')}\n"
        context += f"- Estimated cleanup time: {plan.get('estimated_time_minutes')} minutes\n"
    
    prompt = f"""Based on this trash detection data, write a professional report suitable for city authorities:

{context}

Create a clear, actionable report that:
1. Describes the situation factually
2. Emphasizes environmental/community impact
3. Provides specific cleanup recommendations
4. Has an appropriate professional tone

Format as an email that could be sent to city services."""
    
    try:
        report = llm_client.generate_text(
            prompt,
            system_prompt="You are a professional environmental reporter writing to city officials.",
            max_tokens=500,
            temperature=0.5
        )
        return report
    except Exception as e:
        print(f"LLM report generation failed: {e}")
        # Fallback to template
        return _generate_email_report(detections, severity, location, notes, plan)
