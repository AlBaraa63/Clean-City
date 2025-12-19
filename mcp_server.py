"""
MCP Server for CleanCity Agent

Exposes trash detection and cleanup planning tools via the Model Context Protocol.
Can be used by Claude Desktop or other MCP clients.
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
import json
from typing import Any

from tools import (
    detect_trash_mcp,
    plan_cleanup,
    log_event,
    query_events,
    generate_report
)
from tools.history_tool import get_hotspots, mark_cleaned


# Initialize MCP server
server = Server("cleancity-agent")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="detect_trash",
            description="Detect trash objects in an image using computer vision. Returns bounding boxes, labels, and confidence scores.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "Base64 encoded image data"
                    }
                },
                "required": ["image_data"]
            }
        ),
        Tool(
            name="plan_cleanup",
            description="Generate a cleanup action plan based on detected trash. Returns severity level, resource requirements, and recommendations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "detections": {
                        "type": "array",
                        "description": "Array of trash detection objects from detect_trash",
                        "items": {"type": "object"}
                    },
                    "location": {
                        "type": "string",
                        "description": "Location description (optional)"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Additional context or notes (optional)"
                    },
                    "use_llm": {
                        "type": "boolean",
                        "description": "Use LLM for enhanced planning (optional, default: false)"
                    }
                },
                "required": ["detections"]
            }
        ),
        Tool(
            name="log_event",
            description="Log a trash detection event to the history database for tracking and analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "detections": {
                        "type": "array",
                        "description": "Array of trash detection objects",
                        "items": {"type": "object"}
                    },
                    "severity": {
                        "type": "string",
                        "description": "Severity level: low, medium, or high"
                    },
                    "location": {
                        "type": "string",
                        "description": "Location description (optional)"
                    },
                    "notes": {
                        "type": "string",
                        "description": "User notes (optional)"
                    }
                },
                "required": ["detections", "severity"]
            }
        ),
        Tool(
            name="query_events",
            description="Query trash events from history database with filtering options. Useful for finding patterns and hotspots.",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Only events from last N days (optional)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Filter by location (partial match, optional)"
                    },
                    "severity": {
                        "type": "string",
                        "description": "Filter by severity: low, medium, high (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return (default: 100)"
                    }
                }
            }
        ),
        Tool(
            name="get_hotspots",
            description="Identify locations with recurring trash problems based on historical data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_events": {
                        "type": "integer",
                        "description": "Minimum events to qualify as hotspot (default: 2)"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Time window in days (optional, default: 30)"
                    }
                }
            }
        ),
        Tool(
            name="generate_report",
            description="Generate a formatted report for trash detection event, suitable for city authorities or documentation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "detections": {
                        "type": "array",
                        "description": "Array of trash detection objects",
                        "items": {"type": "object"}
                    },
                    "severity": {
                        "type": "string",
                        "description": "Severity level"
                    },
                    "location": {
                        "type": "string",
                        "description": "Location description (optional)"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Additional notes (optional)"
                    },
                    "plan": {
                        "type": "object",
                        "description": "Cleanup plan object (optional)"
                    },
                    "format": {
                        "type": "string",
                        "description": "Report format: email, markdown, or plain (default: email)"
                    }
                },
                "required": ["detections", "severity"]
            }
        ),
        Tool(
            name="mark_cleaned",
            description="Mark a logged event as cleaned/resolved.",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "integer",
                        "description": "Database event ID to mark as cleaned"
                    }
                },
                "required": ["event_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments) -> list[TextContent]:
    """Handle tool execution."""
    try:
        if name == "detect_trash":
            result = detect_trash_mcp(arguments["image_data"])
        
        elif name == "plan_cleanup":
            result = plan_cleanup(
                detections=arguments["detections"],
                location=arguments.get("location"),
                notes=arguments.get("notes"),
                use_llm=arguments.get("use_llm", False)
            )
        
        elif name == "log_event":
            result = log_event(
                detections=arguments["detections"],
                severity=arguments["severity"],
                location=arguments.get("location"),
                notes=arguments.get("notes")
            )
        
        elif name == "query_events":
            result = query_events(
                days=arguments.get("days"),
                location=arguments.get("location"),
                severity=arguments.get("severity"),
                limit=arguments.get("limit", 100)
            )
        
        elif name == "get_hotspots":
            result = get_hotspots(
                min_events=arguments.get("min_events", 2),
                days=arguments.get("days", 30)
            )
        
        elif name == "generate_report":
            result = generate_report(
                detections=arguments["detections"],
                severity=arguments["severity"],
                location=arguments.get("location"),
                notes=arguments.get("notes"),
                plan=arguments.get("plan"),
                format=arguments.get("format", "email")
            )
        
        elif name == "mark_cleaned":
            result = mark_cleaned(arguments["event_id"])
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
        
        # Return result as JSON
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
