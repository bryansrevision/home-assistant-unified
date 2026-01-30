# API Reference - New Features

## Overview

This document provides a quick reference for the new API endpoints added for Home Assistant integration, mobile device connectivity, remote control, and multi-AI provider support.

## Base URL

All endpoints are relative to: `http://localhost:5000`

## Table of Contents

- [Home Assistant API](#home-assistant-api)
- [Remote Control API](#remote-control-api)
- [Mobile Device API](#mobile-device-api)
- [AI Provider API](#ai-provider-api)

---

## Home Assistant API

### Test Connection

**GET** `/api/homeassistant/connection`

Test connectivity to Home Assistant server.

**Response:**
```json
{
  "success": true,
  "message": "Connected to Home Assistant",
  "data": {
    "message": "API running"
  }
}
```

### Get All Entity States

**GET** `/api/homeassistant/states`

Retrieve all entity states from Home Assistant.

**Response:**
```json
{
  "success": true,
  "states": [
    {
      "entity_id": "light.living_room",
      "state": "on",
      "attributes": {
        "brightness": 255,
        "friendly_name": "Living Room Light"
      }
    }
  ]
}
```

### Get Entity State

**GET** `/api/homeassistant/control/<entity_id>`

Get the state of a specific entity.

**Example:**
```bash
curl http://localhost:5000/api/homeassistant/control/light.living_room
```

**Response:**
```json
{
  "success": true,
  "state": {
    "entity_id": "light.living_room",
    "state": "on",
    "attributes": {...}
  }
}
```

### Control Entity

**POST** `/api/homeassistant/control/<entity_id>`

Control a Home Assistant entity (turn on/off/toggle).

**Request Body:**
```json
{
  "action": "turn_on",
  "parameters": {
    "brightness": 255,
    "color_temp": 370
  }
}
```

**Actions:**
- `turn_on` - Turn on the entity
- `turn_off` - Turn off the entity
- `toggle` - Toggle the entity state

**Example:**
```bash
curl -X POST http://localhost:5000/api/homeassistant/control/light.living_room \
  -H "Content-Type: application/json" \
  -d '{"action": "turn_on", "parameters": {"brightness": 128}}'
```

**Response:**
```json
{
  "success": true,
  "message": "Service light.turn_on called successfully",
  "data": [...]
}
```

---

## Remote Control API

### List Remote Devices

**GET** `/api/remote/devices`

Get all configured remote controllable devices.

**Response:**
```json
{
  "success": true,
  "devices": [
    {
      "name": "Living Room Samsung TV",
      "type": "samsung_tv",
      "ip_address": "192.168.1.100",
      "port": 8002,
      "entity_id": "media_player.living_room_tv"
    }
  ]
}
```

### Get Device Status

**GET** `/api/remote/control/<device_name>`

Get the current status of a remote device.

**Example:**
```bash
curl "http://localhost:5000/api/remote/control/Living%20Room%20Samsung%20TV"
```

**Response:**
```json
{
  "success": true,
  "device": "Living Room Samsung TV",
  "type": "samsung_tv",
  "available": true
}
```

### Send Remote Command

**POST** `/api/remote/control/<device_name>`

Send a remote control command to a device.

**Request Body:**
```json
{
  "command": "power_on"
}
```

**Available Commands:**
- Power: `power`, `power_on`, `power_off`
- Volume: `volume_up`, `volume_down`, `volume_mute`
- Navigation: `up`, `down`, `left`, `right`, `select`, `back`, `home`, `menu`
- Media: `play`, `pause`, `stop`, `rewind`, `fast_forward`
- Input: `input_hdmi1`, `input_hdmi2`, `input_hdmi3`
- Apps: `netflix`, `youtube`, `prime_video`
- Channels: `channel_up`, `channel_down`

**Example:**
```bash
curl -X POST "http://localhost:5000/api/remote/control/Living%20Room%20Samsung%20TV" \
  -H "Content-Type: application/json" \
  -d '{"command": "power_on"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Command power_on sent to Living Room Samsung TV"
}
```

---

## Mobile Device API

### List Mobile Devices

**GET** `/api/mobile/devices`

Get all configured mobile devices.

**Response:**
```json
{
  "success": true,
  "devices": {
    "android_phone_001": {
      "name": "My Android Phone",
      "device_id": "android_phone_001",
      "ip_address": "192.168.1.150",
      "port": 8080,
      "connection_method": "wireless",
      "connected": true
    }
  }
}
```

### Get Device Info

**GET** `/api/mobile/connection/<device_id>`

Get detailed information about a mobile device.

**Example:**
```bash
curl http://localhost:5000/api/mobile/connection/android_phone_001
```

**Response:**
```json
{
  "success": true,
  "device": {
    "name": "My Android Phone",
    "device_id": "android_phone_001",
    "connection_method": "wireless",
    "connected": true
  }
}
```

### Test Device Connection

**POST** `/api/mobile/connection/<device_id>`

Test the connection to a mobile device.

**Example:**
```bash
curl -X POST http://localhost:5000/api/mobile/connection/android_phone_001
```

**Response:**
```json
{
  "success": true,
  "message": "Connected to My Android Phone",
  "method": "wireless",
  "ip_address": "192.168.1.150",
  "port": 8080
}
```

### Send Notification

**POST** `/api/mobile/notify/<device_id>`

Send a push notification to a mobile device.

**Request Body:**
```json
{
  "title": "Alert",
  "message": "Motion detected in living room"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/mobile/notify/android_phone_001 \
  -H "Content-Type: application/json" \
  -d '{"title": "Home Automation", "message": "Welcome home!"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Notification sent to My Android Phone"
}
```

---

## AI Provider API

### Get AI Provider Status

**GET** `/api/ai/status`

Check the status of all configured AI providers.

**Response:**
```json
{
  "success": true,
  "available_providers": ["openai", "gemini", "grok"],
  "connection_status": {
    "openai": true,
    "gemini": false,
    "grok": false
  }
}
```

---

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "success": false,
  "message": "Error description here"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (entity/device not found)
- `500` - Internal Server Error
- `503` - Service Unavailable (integration not configured)

---

## Web Interface Routes

In addition to the API endpoints, the following web pages are available:

- `/` - Main dashboard
- `/dashboard` - Dashboard page
- `/remote` - Remote control interface
- `/mobile` - Mobile device setup page

---

## Authentication

Currently, the API does not require authentication. For production use, consider adding:
- API key authentication
- JWT tokens
- OAuth 2.0

---

## Rate Limiting

The `/api/command` endpoint is rate-limited to 10 requests per minute to prevent abuse of AI services.

---

## Examples

### Complete Workflow: Turn on TV and Start Netflix

```bash
# 1. Turn on the TV
curl -X POST "http://localhost:5000/api/remote/control/Living%20Room%20Samsung%20TV" \
  -H "Content-Type: application/json" \
  -d '{"command": "power_on"}'

# 2. Wait a few seconds for TV to boot
sleep 5

# 3. Launch Netflix
curl -X POST "http://localhost:5000/api/remote/control/Living%20Room%20Samsung%20TV" \
  -H "Content-Type: application/json" \
  -d '{"command": "netflix"}'
```

### Complete Workflow: Home Assistant + Mobile Notification

```bash
# 1. Turn on living room lights via Home Assistant
curl -X POST http://localhost:5000/api/homeassistant/control/light.living_room \
  -H "Content-Type: application/json" \
  -d '{"action": "turn_on", "parameters": {"brightness": 255}}'

# 2. Send notification to mobile device
curl -X POST http://localhost:5000/api/mobile/notify/android_phone_001 \
  -H "Content-Type: application/json" \
  -d '{"title": "Lights", "message": "Living room lights turned on"}'
```

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/bryansrevision/HOME-AI-AUTOMATION/issues
- Documentation: See MOBILE_REMOTE_SETUP.md for detailed setup instructions
- Main README: See README.md for general information
