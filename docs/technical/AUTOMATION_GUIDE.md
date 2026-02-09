# Ulefone Armor 27T Pro - Automation Integration Guide

## Device Overview
| Property | Value |
|----------|-------|
| Model | Ulefone Armor 27T Pro |
| Android | 15 (SDK 35) |
| Build | A3006TA7_VOTA (Oct 2025) |
| Type | Rugged/Industrial Phone |

## Available Sensors (21 Total)
- Accelerometer (TDK ICM4N607)
- Gyroscope (TDK ICM4N607)
- Magnetometer (Voltafield AF6133E)
- Barometer/Pressure (GoerMicro SPL07)
- Light Sensor (Sensortek STK3A5X)
- Proximity Sensor
- Step Counter/Detector
- Orientation, Gravity, Rotation Vector
- Tilt/Wake Gesture Detection

## Installed Automation Stack

### Core Automation
| App | Status | Purpose |
|-----|--------|---------|
| Tasker | ✅ Configured | Main automation engine |
| Join | ✅ Installed | Cross-device messaging/commands |
| AutoTools | ✅ Installed | Web screens, JSON, dialogs |
| AutoInput | ✅ Installed | UI automation, gestures |
| AutoNotification | ✅ Installed | Notification intercept/create |
| AutoVoice | ✅ Installed | Voice commands |
| AutoApps Hub | ✅ Installed | License management |

### Integration Apps
| App | Purpose | Integration |
|-----|---------|-------------|
| Home Assistant | Smart home control | Sensors, location, notifications |
| Tailscale | VPN mesh network | Secure remote access |
| Termux | Linux terminal | Script execution, SSH |
| HTTP Shortcuts | REST API calls | Webhook triggers |
| Gotify | Push notifications | Server alerts |
| ntfy | Push notifications | Alternative to Gotify |
| Syncthing | File sync | Config/backup sync |
| DroidVNC-NG | Remote control | Screen sharing |
| RustDesk | Remote desktop | Alternative remote |

### Proxmox Integration
| App | Purpose |
|-----|---------|
| Proxmobo | VM/CT management |
| PVE Flutter | Full Proxmox client |

---

## Integration Recommendations

### 1. Home Assistant Integration

#### Enable All Sensors
Open Home Assistant app → Settings → Companion App → Manage Sensors

Enable these for automation:
- **Battery sensors** (level, charging, health)
- **Location sensors** (accurate, zone-based)
- **Activity sensor** (walking, driving, still)
- **Network sensors** (WiFi SSID, IP, cellular)
- **Pressure sensor** (weather/altitude)
- **Light sensor** (ambient light automation)
- **Step counter** (fitness tracking)
- **Phone state** (ringer, DND, call active)
- **App usage** (screen on/off, app in use)

#### Tasker → Home Assistant
Create HTTP shortcuts or use Tasker HTTP Request:
```
URL: http://YOUR_HA_IP:8123/api/services/[domain]/[service]
Headers: Authorization: Bearer YOUR_LONG_LIVED_TOKEN
         Content-Type: application/json
Body: {"entity_id": "light.living_room"}
```

#### Home Assistant → Tasker
Use Join API or AutoRemote:
```yaml
# In HA automation
service: rest_command.tasker_join
data:
  deviceId: YOUR_DEVICE_ID
  text: "run_task=TaskName"
```

### 2. Proxmox Integration

#### Via Tasker + HTTP Shortcuts
Create shortcuts for common operations:
```
# Start VM
POST https://proxmox.local:8006/api2/json/nodes/{node}/qemu/{vmid}/status/start
Headers: Authorization: PVEAPIToken=USER@REALM!TOKENID=TOKEN_SECRET

# Stop VM
POST https://proxmox.local:8006/api2/json/nodes/{node}/qemu/{vmid}/status/stop

# Get VM Status
GET https://proxmox.local:8006/api2/json/nodes/{node}/qemu/{vmid}/status/current
```

#### Via Termux Scripts
```bash
#!/data/data/com.termux/files/usr/bin/bash
# proxmox_control.sh

PVE_HOST="proxmox.tailscale:8006"
PVE_TOKEN="user@pam!token=xxxxxxxx"

curl -k -X POST "https://$PVE_HOST/api2/json/nodes/pve/qemu/$1/status/$2" \
  -H "Authorization: PVEAPIToken=$PVE_TOKEN"
```

### 3. Tailscale Integration

Your Tailscale is running (v1.92.3). Use for:
- Secure access to Home Assistant from anywhere
- SSH into Proxmox nodes
- Access internal services without port forwarding

Tasker can detect Tailscale connection:
```
State: Net → Tailscale Connected
  (check if tailscale0 interface exists)
```

### 4. Notification Hub Setup

#### Gotify + ntfy for Server Alerts
Configure in Home Assistant:
```yaml
notify:
  - name: phone_gotify
    platform: rest
    resource: https://gotify.your.domain/message
    method: POST_JSON
    headers:
      X-Gotify-Key: YOUR_APP_TOKEN
    data:
      title: "{{ title }}"
      message: "{{ message }}"
      priority: 5
```

#### Tasker Notification Intercept
AutoNotification can catch Gotify/ntfy notifications and trigger Tasker tasks.

---

## Recommended Tasker Profiles

### 1. Home Presence
```
Profile: At Home (WiFi Connected to HomeNetwork)
  → Send location to HA
  → Enable home automations
  → Sync files via Syncthing
```

### 2. Server Monitoring
```
Profile: Gotify Notification Received
  Filter: title contains "Alert"
  → Parse notification with AutoTools JSON
  → Show popup with AutoTools Dialog
  → Option to run Proxmox commands
```

### 3. Voice Control
```
Profile: AutoVoice "Proxmox [command] [vm]"
  → HTTP Request to Proxmox API
  → Flash result
```

### 4. Device as Sensor
```
Profile: Every 5 minutes
  → Read barometer, light, battery
  → Send to Home Assistant via REST API
```

### 5. Remote Control
```
Profile: Join command received "vnc_start"
  → Launch DroidVNC-NG
  → Reply with Tailscale IP
```

---

## Quick Setup Commands

### Already Applied ✅
- Battery optimization disabled for all automation apps
- Accessibility services enabled (Tasker, AutoInput)
- Notification listeners enabled (AutoNotification, Join, Tasker)
- Background execution allowed
- WRITE_SECURE_SETTINGS granted

### Manual Steps Required

1. **Tasker**: Open app → enable when prompted
2. **Home Assistant**: Login and enable sensors
3. **Join**: Sign in with Google account
4. **AutoApps**: Tap each plugin → verify license
5. **Termux**: Install termux-api package:
   ```
   pkg install termux-api
   ```

6. **Create Proxmox API Token**:
   - Proxmox → Datacenter → Permissions → API Tokens
   - Create token for automation user

7. **Create Home Assistant Long-Lived Token**:
   - HA → Profile → Long-Lived Access Tokens → Create

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    ARMOR 27T PRO                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ Tasker  │←→│  Join   │←→│AutoTools│←→│AutoInput│   │
│  └────┬────┘  └────┬────┘  └─────────┘  └─────────┘   │
│       │            │                                    │
│       ▼            ▼                                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                │
│  │ Termux  │  │HTTP Short│  │  HA App │                │
│  └────┬────┘  └────┬────┘  └────┬────┘                │
└───────┼────────────┼────────────┼───────────────────────┘
        │            │            │
        ▼            ▼            ▼
   ┌─────────────────────────────────────┐
   │           TAILSCALE MESH            │
   └─────────────────────────────────────┘
        │            │            │
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ Proxmox │  │  Home   │  │ Gotify/ │
   │  Nodes  │  │Assistant│  │  ntfy   │
   └─────────┘  └─────────┘  └─────────┘
```

---

## Missing Recommended Apps

Consider installing via Aurora Store:
1. **Termux:API** - Access device sensors from scripts
2. **Termux:Tasker** - Run Termux commands from Tasker
3. **AutoLocation** - Advanced geofencing
4. **AutoShare** - Share intents automation
5. **MacroDroid** (backup) - Simpler automation alternative
