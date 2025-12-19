"""
History Tracking MCP Tool

Logs trash detection events and provides querying capabilities for analysis.
Uses SQLite for persistent storage.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, Any
from pathlib import Path
from trash_model import Detection


DB_PATH = Path(__file__).parent.parent / "data" / "trash_events.db"


def _get_connection() -> sqlite3.Connection:
    """Get SQLite connection and ensure schema exists."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Create schema if not exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            location TEXT,
            latitude REAL,
            longitude REAL,
            severity TEXT NOT NULL,
            trash_count INTEGER NOT NULL,
            categories TEXT NOT NULL,
            detections_json TEXT NOT NULL,
            notes TEXT,
            image_path TEXT,
            cleaned BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_location ON events(location)
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_severity ON events(severity)
    """)
    
    conn.commit()
    return conn


def log_event(
    detections: list[Detection],
    severity: str,
    location: Optional[str] = None,
    notes: Optional[str] = None,
    image_path: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
):
    """
    Log a trash detection event to the database.
    
    Args:
        detections: List of trash detections
        severity: "low" | "medium" | "high"
        location: Human-readable location description
        notes: Optional user notes
        image_path: Optional path to saved image
        latitude: Optional GPS latitude
        longitude: Optional GPS longitude
    
    Returns:
        Dict with event_id and confirmation message
    """
    conn = _get_connection()
    
    timestamp = datetime.now().isoformat()
    trash_count = len(detections)
    categories = json.dumps(list(set(d["label"] for d in detections)))
    detections_json = json.dumps(detections)
    
    cursor = conn.execute("""
        INSERT INTO events (
            timestamp, location, latitude, longitude, severity,
            trash_count, categories, detections_json, notes, image_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp, location, latitude, longitude, severity,
        trash_count, categories, detections_json, notes, image_path
    ))
    
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "event_id": event_id,
        "timestamp": timestamp,
        "message": f"Event logged successfully (ID: {event_id})"
    }


def query_events(
    days: Optional[int] = None,
    location: Optional[str] = None,
    severity: Optional[str] = None,
    min_trash_count: Optional[int] = None,
    cleaned_only: bool = False,
    limit: int = 100
):
    """
    Query trash events with filtering options.
    
    Args:
        days: Only events from last N days
        location: Filter by location (partial match)
        severity: Filter by severity level
        min_trash_count: Minimum trash items threshold
        cleaned_only: Only show cleaned events
        limit: Maximum results to return
    
    Returns:
        Dict containing:
            - events: List of matching events
            - total_count: Total matching events
            - summary: Aggregate statistics
    """
    conn = _get_connection()
    
    # Build query
    conditions = []
    params = []
    
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        conditions.append("timestamp >= ?")
        params.append(cutoff)
    
    if location:
        conditions.append("location LIKE ?")
        params.append(f"%{location}%")
    
    if severity:
        conditions.append("severity = ?")
        params.append(severity)
    
    if min_trash_count:
        conditions.append("trash_count >= ?")
        params.append(min_trash_count)
    
    if cleaned_only:
        conditions.append("cleaned = 1")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Get events
    query = f"""
        SELECT 
            id, timestamp, location, latitude, longitude,
            severity, trash_count, categories, notes, image_path, cleaned
        FROM events
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT ?
    """
    params.append(limit)
    
    cursor = conn.execute(query, params)
    events = [dict(row) for row in cursor.fetchall()]
    
    # Parse JSON fields
    for event in events:
        event["categories"] = json.loads(event["categories"])
    
    # Get summary statistics
    summary_query = f"""
        SELECT 
            COUNT(*) as total_events,
            SUM(trash_count) as total_trash_items,
            AVG(trash_count) as avg_trash_per_event,
            COUNT(DISTINCT location) as unique_locations
        FROM events
        WHERE {where_clause}
    """
    summary_cursor = conn.execute(summary_query, params[:-1])  # Exclude limit param
    summary = dict(summary_cursor.fetchone())
    
    conn.close()
    
    return {
        "events": events,
        "total_count": len(events),
        "summary": summary,
        "filters_applied": {
            "days": days,
            "location": location,
            "severity": severity,
            "min_trash_count": min_trash_count
        }
    }


def get_hotspots(min_events: int = 2, days: Optional[int] = 30):
    """
    Identify locations with recurring trash problems.
    
    Args:
        min_events: Minimum number of events to qualify as hotspot
        days: Time window to analyze (None = all time)
    
    Returns:
        Dict with hotspot locations and their statistics
    """
    conn = _get_connection()
    
    conditions = ["location IS NOT NULL"]
    params = []
    
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        conditions.append("timestamp >= ?")
        params.append(cutoff)
    
    where_clause = " AND ".join(conditions)
    
    query = f"""
        SELECT 
            location,
            COUNT(*) as event_count,
            SUM(trash_count) as total_trash,
            AVG(trash_count) as avg_trash,
            MAX(timestamp) as last_event,
            GROUP_CONCAT(DISTINCT severity) as severities
        FROM events
        WHERE {where_clause}
        GROUP BY location
        HAVING event_count >= ?
        ORDER BY event_count DESC, total_trash DESC
    """
    params.append(min_events)
    
    cursor = conn.execute(query, params)
    hotspots = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "hotspots": hotspots,
        "count": len(hotspots),
        "criteria": f"Locations with {min_events}+ events" + (f" in last {days} days" if days else "")
    }


def mark_cleaned(event_id: int):
    """Mark an event as cleaned."""
    conn = _get_connection()
    conn.execute("UPDATE events SET cleaned = 1 WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    
    return {"message": f"Event {event_id} marked as cleaned"}
