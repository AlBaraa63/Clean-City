"""Tools package for CleanCity Agent MCP server."""

from .trash_detection_tool import detect_trash_mcp
from .cleanup_planner_tool import plan_cleanup
from .history_tool import log_event, query_events
from .report_generator_tool import generate_report

__all__ = [
    "detect_trash_mcp",
    "plan_cleanup",
    "log_event",
    "query_events",
    "generate_report"
]
