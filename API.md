# CleanCity Agent - MCP Server API Documentation

This document describes the **Model Context Protocol (MCP) tools** exposed by CleanCity Agent's MCP server.

## 🔌 Server Information

- **Server Name:** `cleancity-agent`
- **Version:** 1.0.0
- **Protocol:** MCP (Model Context Protocol)
- **Transport:** stdio

## 🛠️ Available Tools

CleanCity Agent exposes **6 powerful tools** that AI agents can use to detect trash, plan cleanups, track events, and generate reports.

---

## 1. `detect_trash`

Analyze an image and detect trash/litter using computer vision.

### Input Schema

```json
{
  "image_path": "string (required)",
  "location": "string (optional)",
  "notes": "string (optional)"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_path` | string | ✅ Yes | Absolute path to image file on disk |
| `location` | string | ❌ No | Location where trash was found (e.g., "Central Park") |
| `notes` | string | ❌ No | Additional context or observations |

### Returns

```json
{
  "detections": [
    {
      "object_type": "plastic_bottle",
      "confidence": 0.95,
      "bbox": [100, 150, 250, 400]
    }
  ],
  "count": 5,
  "annotated_image_path": "/path/to/annotated_image.jpg"
}
```

### Example Usage

**Claude Desktop:**
```
User: Analyze the trash in /home/user/beach_litter.jpg at Ocean Beach