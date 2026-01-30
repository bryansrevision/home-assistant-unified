# 📱 Android Integration Setup Guide for Home Environment Infrastructure

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Phase 1: Core Integration](#phase-1-core-integration)
- [Phase 2: Automation Integration](#phase-2-automation-integration)
- [Phase 3: Advanced Features](#phase-3-advanced-features)
- [Post-Setup Verification](#post-setup-verification)
- [Next Steps](#next-steps)

---

## Overview

This guide walks you through integrating your Android device with your complete home automation infrastructure, including:
- **Home Assistant** (192.168.1.201:8123)
- **Proxmox VE** (192.168.1.185:8006)
- **Unified MCP Hub** (Port 3000)
- **MQTT Broker** (Port 1883)
- **CloudDataSync** and other services

**Estimated Setup Time**: 6-8 hours across 3 phases

---

## Prerequisites

### Required Information
Before starting, gather the following information:

#### Device Information
- [ ] Android version: `_______`
- [ ] Device model: `_______`
- [ ] Google account for HA integration: `_______`
- [ ] Current battery optimization settings: `_______`

#### Network Configuration
```yaml
Local Network:
  WiFi SSID: _______
  WiFi Password: _______
  IP Range: 192.168.1.0/24
  Gateway: 192.168.1.1
  DNS: 192.168.1.1 (or 8.8.8.8)

Home Assistant:
  Local URL: http://192.168.1.201:8123
  External URL (if configured): _______
  Long-Lived Access Token: _______ (generate in HA profile)

Proxmox VE:
  URL: https://192.168.1.185:8006
  Username: _______
  Password: _______ (or use Bitwarden)

Tailscale VPN:
  Account email: _______
  Magic DNS enabled: Yes/No
```

#### Security Credentials
- [ ] Home Assistant long-lived access token (Profile > Long-Lived Access Tokens)
- [ ] Bitwarden account credentials
- [ ] Tailscale account credentials
- [ ] Proxmox root password (or dedicated mobile user)

### Required Android Apps
Install these apps from Google Play Store:

#### Essential Apps (Must Have)
1. **Home Assistant** - Official companion app
2. **Tailscale** - VPN for secure remote access
3. **Bitwarden** - Password manager
4. **MQTT Client** - For direct MQTT interactions (e.g., IoT MQTT Panel)

#### Service-Specific Apps (Recommended)
5. **Jellyfin** - Media streaming
6. **Plex** - Alternative media access
7. **Amazon Alexa** - Voice control integration
8. **SmartThings** - Device management
9. **Proxmox Virtual Environment** - Official Proxmox mobile client (if available) or use web browser

#### Optional Apps (Nice to Have)
10. **Tasker** - Advanced automation (paid app)
11. **IFTTT** - Additional automation options
12. **Termux** - SSH client for advanced users
13. **VLC** - Media player for local streaming

---

## Phase 1: Core Integration (1-2 hours)

### Step 1: Home Assistant Companion App Setup

#### 1.1 Install and Launch
1. Open Google Play Store
2. Search for "Home Assistant"
3. Install the official Home Assistant app (by Nabu Casa, Inc.)
4. Launch the app

#### 1.2 Initial Configuration
1. **Select Connection Method**:
   - Tap "Manual Setup"
   - Enter your Home Assistant URL: `http://192.168.1.201:8123`
   - If you're already on your home WiFi, the app may auto-detect your instance

2. **Login**:
   - Enter your Home Assistant username and password
   - Complete 2FA if enabled

3. **Grant Permissions** (CRITICAL for automation):
   ```
   ✓ Location (Always) - Required for presence detection
   ✓ Physical Activity - For activity recognition
   ✓ Notifications - For alerts and actionable notifications
   ✓ Background App Refresh - Keep connection alive
   ✓ Battery Optimization OFF - Prevent Android from killing the app
   ```

4. **Device Registration**:
   - The app will register your phone as a device in Home Assistant
   - Default name: `mobile_app_<device_name>`
   - Note this device ID - you'll use it in automations

#### 1.3 Enable Device Sensors
Navigate to: **App Configuration > Sensors**

Enable the following sensors:

##### Location & Activity Sensors
- ✅ **Location** - GPS coordinates
- ✅ **Geocoded Location** - Human-readable address
- ✅ **Zone** - Current zone (Home, Work, etc.)
- ✅ **Activity** - Walking, driving, still, etc.
- ✅ **Steps** - Step counter
- ✅ **Distance** - Distance traveled

##### Device Status Sensors
- ✅ **Battery Level** - Current battery percentage
- ✅ **Battery State** - Charging, discharging, full
- ✅ **Charger Type** - AC, USB, wireless
- ✅ **Battery Temperature** - Battery temp in °C
- ✅ **Power Save Mode** - Android battery saver status

##### Network Sensors
- ✅ **WiFi Connection** - Current SSID
- ✅ **WiFi BSSID** - Router MAC address
- ✅ **WiFi IP Address** - Local IP
- ✅ **WiFi Link Speed** - Connection speed
- ✅ **Mobile Data** - Enabled/disabled status
- ✅ **Mobile Network Type** - 4G, 5G, etc.

##### Audio & Display Sensors
- ✅ **Audio Mode** - Normal, vibrate, silent
- ✅ **Ringer Mode** - Ring volume level
- ✅ **Media Volume** - Media volume level
- ✅ **Do Not Disturb** - DND status
- ✅ **Screen Brightness** - Display brightness level
- ✅ **Screen On** - Screen state

##### Advanced Sensors (Optional but Recommended)
- ✅ **Light Sensor** - Ambient light level
- ✅ **Pressure Sensor** - Atmospheric pressure
- ✅ **Proximity Sensor** - Near/far detection
- ✅ **Next Alarm** - Next scheduled alarm time
- ✅ **Sleep Time** - Sleep schedule tracking
- ✅ **App Usage** - Foreground app tracking

**Sensor Update Frequency**:
- Location: Every 15-60 seconds (when moving)
- Battery: Every 15 minutes
- Network: On change
- Other: Every 15 minutes or on change

#### 1.4 Configure Notification Channels
Navigate to: **App Configuration > Notifications**

Set up these notification channels:

```yaml
Critical Alerts:
  - Security breaches
  - Fire/smoke alarms
  - Water leak detection
  - Sound: Loud, persistent
  - Vibration: Strong
  - Do Not Disturb: Override

High Priority:
  - Door/window opened while away
  - Motion detected (no one home)
  - System failures (Proxmox VM down)
  - Sound: Normal
  - Vibration: Normal
  - Do Not Disturb: Allow

Medium Priority:
  - Backup completion
  - Person detected at door
  - Package delivery
  - Sound: Soft
  - Vibration: Short
  - Do Not Disturb: Silence

Low Priority:
  - Daily summaries
  - Non-critical updates
  - Sound: None
  - Vibration: None
  - Do Not Disturb: Silence
```

#### 1.5 Battery Optimization Settings
**CRITICAL**: Disable battery optimization for Home Assistant app

**Method 1 - Via App Settings**:
1. Go to Android Settings > Apps > Home Assistant
2. Tap "Battery" or "Battery usage"
3. Select "Unrestricted" or "Don't optimize"

**Method 2 - Via Battery Settings**:
1. Go to Android Settings > Battery > Battery Optimization
2. Tap dropdown menu, select "All apps"
3. Find "Home Assistant"
4. Select "Don't optimize"
5. Confirm

**Additional Settings** (varies by manufacturer):
- **Samsung**: Settings > Apps > Home Assistant > Battery > Allow background activity
- **Xiaomi**: Settings > Apps > Home Assistant > Battery saver > No restrictions
- **Huawei**: Settings > Apps > Home Assistant > Battery > App launch > Manage manually
- **OnePlus**: Settings > Apps > Home Assistant > Battery optimization > Don't optimize

---

### Step 2: Location Services Configuration

#### 2.1 GPS Settings Optimization
1. **Enable High Accuracy Mode**:
   - Settings > Location > Mode > High accuracy
   - This uses GPS, WiFi, Bluetooth, and mobile networks

2. **Google Location Services**:
   - Settings > Location > Google Location Accuracy > ON
   - Improves location accuracy using Google services

3. **WiFi Scanning** (Even when WiFi is off):
   - Settings > Location > WiFi scanning > ON
   - Helps with indoor location accuracy

#### 2.2 Zone Configuration in Home Assistant

Open Home Assistant web interface and configure zones:

**Zone 1: Home** (Primary zone)
```yaml
# Configuration -> Areas & Zones -> Add Zone
Name: Home
Latitude: 37.7749  # Your home coordinates
Longitude: -122.4194
Radius: 100  # meters
Icon: mdi:home
Passive: false  # Active tracking
```

**Zone 2: Work**
```yaml
Name: Work
Latitude: 37.7849  # Your work coordinates
Longitude: -122.4094
Radius: 150  # meters (larger for parking lots)
Icon: mdi:briefcase
Passive: false
```

**Zone 3: Gym** (Optional)
```yaml
Name: Gym
Latitude: 37.7949
Longitude: -122.3994
Radius: 100
Icon: mdi:dumbbell
Passive: false
```

**Zone 4: Grocery Store** (Optional)
```yaml
Name: Grocery Store
Latitude: 37.7649
Longitude: -122.4294
Radius: 200
Icon: mdi:cart
Passive: true  # Don't trigger automations, just track
```

#### 2.3 Geofencing Setup
Geofencing is automatic once zones are configured. The Home Assistant app will:
- Report `home` when within Home zone radius
- Report `not_home` when outside all zones
- Report zone name when in other zones
- Trigger automations based on zone changes

**Testing Geofencing**:
1. In Home Assistant, go to Developer Tools > States
2. Find your device tracker entity: `device_tracker.mobile_app_<device_name>`
3. Walk outside your home zone radius
4. Within 1-2 minutes, state should change to `not_home`
5. Walk back inside, state should change to `home`

---

### Step 3: Tailscale VPN Setup

#### 3.1 Install Tailscale on Android
1. Open Google Play Store
2. Search for "Tailscale"
3. Install the official Tailscale app
4. Launch Tailscale

#### 3.2 Initial Configuration
1. **Sign In**:
   - Tap "Sign in with Google" or your preferred method
   - Use the same account as your Tailscale network

2. **Connect to Network**:
   - Tap the toggle to connect
   - Grant VPN permission when prompted
   - Your device will receive a Tailscale IP (100.x.x.x)

3. **Verify Connection**:
   - You should see "Connected" status
   - Note your Tailscale IP address

#### 3.3 DNS Configuration
1. Tap the menu (three dots) > **DNS settings**
2. Enable **MagicDNS** (if available on your plan)
3. Add custom nameservers if needed:
   ```
   Primary: 1.1.1.1 (Cloudflare)
   Secondary: 8.8.8.8 (Google)
   ```

#### 3.4 Auto-Connect Rules
1. **On Mobile Data**: Auto-connect enabled
   - When you leave WiFi, Tailscale connects automatically
   
2. **On Trusted WiFi**: Auto-connect disabled
   - On home network (192.168.1.x), Tailscale can disconnect
   - Saves battery and reduces latency

**Configure Trusted Networks**:
1. Tailscale Settings > Auto-connect
2. Add your home WiFi SSID to trusted networks
3. Enable "Disconnect on trusted networks"

#### 3.5 Test Remote Access
**When on Mobile Data**:
1. Disconnect from home WiFi
2. Ensure Tailscale is connected
3. Open Home Assistant app
4. Access should work via Tailscale IP or domain

**Tailscale URLs for Your Services**:
```
Home Assistant: http://<ha-tailscale-ip>:8123
Proxmox: https://<proxmox-tailscale-ip>:8006
MCP Hub: http://<mcp-hub-tailscale-ip>:3000
```

To find Tailscale IPs, check the Tailscale admin console or use the Tailscale app.

---

### Step 4: Quick Settings Tiles

#### 4.1 Add Home Assistant Quick Settings Tiles
1. Swipe down to show Quick Settings panel
2. Tap edit button (pencil icon)
3. Scroll through available tiles
4. Drag Home Assistant tiles to your Quick Settings:
   - **Favorites** - Quick access to favorite entities
   - **Template Tile 1** - Custom template (configure in app)
   - **Template Tile 2** - Another custom template
   - **Script Tile** - Execute HA scripts

5. Save and exit

#### 4.2 Configure Template Tiles
Open Home Assistant app, go to **App Configuration > Manage Tiles**

**Template Tile 1 - "All Lights Off"**:
```yaml
Label: All Lights Off
Icon: mdi:lightbulb-off
Tap Action:
  Action: Call Service
  Service: light.turn_off
  Target: all
```

**Template Tile 2 - "Security Arm"**:
```yaml
Label: Arm Security
Icon: mdi:shield-lock
Tap Action:
  Action: Call Service
  Service: alarm_control_panel.alarm_arm_away
  Target: alarm_control_panel.home_security
```

#### 4.3 Add Widgets to Home Screen
1. Long-press on home screen
2. Tap "Widgets"
3. Scroll to "Home Assistant"
4. Choose widget size and type:

**2x2 Widget - Quick Actions**:
- Add 4 favorite controls (lights, locks, scenes)
- Tap to toggle

**4x2 Widget - Dashboard View**:
- Shows mini dashboard
- Displays sensor states
- Tap to open full app

**1x1 Widget - Single Entity**:
- Control one specific entity
- Useful for most-used controls (garage door, front door lock)

---

### Step 5: Notification Setup and Testing

#### 5.1 Test Notification Delivery
From Home Assistant, go to **Developer Tools > Services**

Send a test notification:
```yaml
Service: notify.mobile_app_<your_device_name>
Service Data:
  message: "Test notification from Home Assistant"
  title: "Test Alert"
  data:
    priority: high
    ttl: 0
    notification_icon: "mdi:home-assistant"
    color: "#03a9f4"
```

You should receive the notification on your Android device within seconds.

#### 5.2 Configure Actionable Notifications
Test an actionable notification:

```yaml
Service: notify.mobile_app_<your_device_name>
Service Data:
  message: "Front door is unlocked. Lock it?"
  title: "Door Alert"
  data:
    actions:
      - action: "LOCK_DOOR"
        title: "Lock Door"
      - action: "DISMISS"
        title: "Dismiss"
```

#### 5.3 Create Automation to Handle Actions
```yaml
# In Home Assistant automations
automation:
  - alias: "Handle Lock Door Action"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: LOCK_DOOR
    action:
      - service: lock.lock
        target:
          entity_id: lock.front_door
      - service: notify.mobile_app_<your_device_name>
        data:
          message: "Front door locked successfully"
```

#### 5.4 Rich Notification with Image
Send notification with camera snapshot:

```yaml
Service: notify.mobile_app_<your_device_name>
Service Data:
  message: "Motion detected at front door"
  title: "Security Alert"
  data:
    image: "/api/camera_proxy/camera.front_door"
    actions:
      - action: "VIEW_CAMERA"
        title: "View Live"
      - action: "ARM_SECURITY"
        title: "Arm Security"
```

---

## Phase 2: Automation Integration (2-3 hours)

### Step 1: Presence-Based Automations

#### 1.1 Arrival Detection - "Welcome Home"

Create automation in Home Assistant:

```yaml
# File: config/home-assistant/android-automations.yaml
automation:
  - alias: "Android - Welcome Home"
    description: "Trigger welcome home routine when Android device arrives"
    trigger:
      - platform: state
        entity_id: device_tracker.mobile_app_<your_device>
        to: 'home'
        from: 'not_home'
    condition:
      - condition: sun
        after: sunset
        before: sunrise
    action:
      # Turn on lights
      - service: light.turn_on
        target:
          entity_id: light.living_room
        data:
          brightness: 200
      
      # Unlock front door
      - service: lock.unlock
        target:
          entity_id: lock.front_door
      
      # Adjust thermostat
      - service: climate.set_temperature
        target:
          entity_id: climate.home_thermostat
        data:
          temperature: 72
      
      # Disarm security
      - service: alarm_control_panel.alarm_disarm
        target:
          entity_id: alarm_control_panel.home_security
        data:
          code: !secret alarm_code
      
      # Send notification
      - service: notify.mobile_app_<your_device>
        data:
          message: "Welcome home! Lights on, door unlocked, security disarmed."
          title: "Home Automation"
```

#### 1.2 Departure Detection - "Away Mode"

```yaml
automation:
  - alias: "Android - Away Mode"
    description: "Enable away mode when Android device leaves home"
    trigger:
      - platform: state
        entity_id: device_tracker.mobile_app_<your_device>
        to: 'not_home'
        from: 'home'
        for:
          minutes: 5  # Delay to avoid false triggers
    action:
      # Lock all doors
      - service: lock.lock
        target:
          entity_id: 
            - lock.front_door
            - lock.back_door
            - lock.garage_door
      
      # Turn off all lights
      - service: light.turn_off
        target:
          entity_id: all
      
      # Arm security system
      - service: alarm_control_panel.alarm_arm_away
        target:
          entity_id: alarm_control_panel.home_security
        data:
          code: !secret alarm_code
      
      # Set thermostat to eco mode
      - service: climate.set_preset_mode
        target:
          entity_id: climate.home_thermostat
        data:
          preset_mode: eco
      
      # Turn off TVs and media
      - service: media_player.turn_off
        target:
          entity_id: all
      
      # Send confirmation
      - service: notify.mobile_app_<your_device>
        data:
          message: "Away mode activated. All doors locked, security armed."
          title: "Security Alert"
          data:
            priority: high
```

#### 1.3 Battery-Aware Charging Automation

```yaml
automation:
  - alias: "Android - Start Charging When Low"
    description: "Notify to charge when battery is low at home"
    trigger:
      - platform: numeric_state
        entity_id: sensor.mobile_app_<your_device>_battery_level
        below: 20
    condition:
      - condition: state
        entity_id: device_tracker.mobile_app_<your_device>
        state: 'home'
      - condition: state
        entity_id: binary_sensor.mobile_app_<your_device>_is_charging
        state: 'off'
    action:
      - service: notify.mobile_app_<your_device>
        data:
          message: "Your phone battery is at {{ states('sensor.mobile_app_<your_device>_battery_level') }}%. Please charge."
          title: "Low Battery Alert"
          data:
            priority: high
            color: "#FF0000"
```

#### 1.4 Do Not Disturb Sync

```yaml
automation:
  - alias: "Android - Sync DND to Home Mode"
    description: "When phone is in DND, set home to quiet mode"
    trigger:
      - platform: state
        entity_id: binary_sensor.mobile_app_<your_device>_do_not_disturb
        to: 'on'
    condition:
      - condition: state
        entity_id: device_tracker.mobile_app_<your_device>
        state: 'home'
    action:
      # Dim lights
      - service: light.turn_on
        target:
          entity_id: all
        data:
          brightness: 50
      
      # Mute notifications on smart speakers
      - service: media_player.volume_set
        target:
          entity_id: media_player.all_speakers
        data:
          volume_level: 0.1
      
      # Set house mode
      - service: input_select.select_option
        target:
          entity_id: input_select.house_mode
        data:
          option: "Quiet"
```

#### 1.5 Driving Mode Detection

```yaml
automation:
  - alias: "Android - Driving Mode Started"
    description: "Detect driving and adjust settings"
    trigger:
      - platform: state
        entity_id: sensor.mobile_app_<your_device>_activity
        to: 'in_vehicle'
    action:
      # Send to car-friendly interface
      - service: notify.mobile_app_<your_device>
        data:
          message: "Drive safely! Car mode activated."
          title: "Driving Detected"
          data:
            priority: low
      
      # Log departure time (for commute tracking)
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.last_departure
        data:
          timestamp: "{{ now().timestamp() }}"
```

---

### Step 2: Advanced Notification Templates

All notification templates are in `/config/home-assistant/android-notifications.yaml`

#### 2.1 Security Breach Alert

```yaml
# Critical security notification with actionable buttons
script:
  android_security_breach_alert:
    alias: "Send Security Breach Alert"
    sequence:
      - service: notify.mobile_app_<your_device>
        data:
          message: "{{ message }}"
          title: "⚠️ SECURITY BREACH"
          data:
            priority: high
            ttl: 0
            importance: max
            channel: Critical Alerts
            color: "#FF0000"
            vibrationPattern: "100, 1000, 100, 1000, 100"
            ledColor: "#FF0000"
            image: "/api/camera_proxy/{{ camera }}"
            actions:
              - action: "CALL_911"
                title: "Call 911"
              - action: "VIEW_CAMERAS"
                title: "View Cameras"
              - action: "SOUND_ALARM"
                title: "Sound Alarm"
```

#### 2.2 Backup Completion Notification

```yaml
script:
  android_backup_complete:
    alias: "Send Backup Completion Notice"
    sequence:
      - service: notify.mobile_app_<your_device>
        data:
          message: |
            Backup completed successfully
            Size: {{ backup_size }}
            Duration: {{ backup_duration }}
            Files: {{ file_count }}
          title: "✅ Backup Complete"
          data:
            priority: low
            channel: Low Priority
            actions:
              - action: "VIEW_DETAILS"
                title: "View Details"
```

#### 2.3 System Health Warning

```yaml
script:
  android_system_health_warning:
    alias: "Send System Health Warning"
    sequence:
      - service: notify.mobile_app_<your_device>
        data:
          message: |
            ⚠️ {{ component }} is experiencing issues:
            Status: {{ status }}
            CPU: {{ cpu_usage }}%
            Memory: {{ memory_usage }}%
            Uptime: {{ uptime }}
          title: "System Health Alert"
          data:
            priority: high
            color: "#FFA500"
            actions:
              - action: "RESTART_SERVICE"
                title: "Restart"
              - action: "VIEW_LOGS"
                title: "View Logs"
              - action: "OPEN_PROXMOX"
                title: "Open Proxmox"
```

---

### Step 3: Widget Configurations

#### 3.1 Favorite Devices Widget

Configure in Home Assistant app settings:

**Widget 1 - Quick Controls (2x2)**
```yaml
Entities:
  - light.living_room
  - light.bedroom
  - lock.front_door
  - switch.garage_door
```

**Widget 2 - Security Dashboard (4x2)**
```yaml
Entities:
  - alarm_control_panel.home_security
  - binary_sensor.front_door
  - binary_sensor.back_door
  - binary_sensor.motion_detector
  - camera.front_door
  - camera.driveway
```

**Widget 3 - Climate Control (2x1)**
```yaml
Entities:
  - climate.home_thermostat
  - sensor.indoor_temperature
```

---

## Phase 3: Advanced Features (3-4 hours)

### Step 1: Proxmox Mobile Management

#### 1.1 Web Interface Access
1. Open Chrome on Android
2. Navigate to `https://192.168.1.185:8006`
3. Accept self-signed certificate warning (if applicable)
4. Login with your credentials
5. Tap menu (three dots) > "Add to Home screen"
   - Name: "Proxmox VE"
   - This creates an app-like shortcut

#### 1.2 Create Dedicated Mobile User (Recommended)
In Proxmox web interface:
1. Datacenter > Permissions > Users > Add
2. Username: `mobile`
3. Realm: `pve` (Proxmox VE authentication)
4. Set strong password
5. Add to appropriate groups with limited permissions

#### 1.3 Configure VM Quick Actions
Use Home Assistant to control Proxmox VMs:

```yaml
# In Home Assistant configuration.yaml
switch:
  - platform: rest
    name: "Proxmox VM 101"
    resource: "https://192.168.1.185:8006/api2/json/nodes/pve/qemu/101/status/current"
    body_on: '{"node":"pve","vmid":101,"command":"start"}'
    body_off: '{"node":"pve","vmid":101,"command":"stop"}'
    headers:
      Authorization: "PVEAuthCookie=..."
    is_on_template: "{{ value_json.data.status == 'running' }}"
```

Add these switches to your Home Assistant dashboard and widgets for quick VM control.

---

### Step 2: Voice Assistant Integration

#### 2.1 Google Assistant Setup with Home Assistant
1. In Home Assistant:
   - Go to Configuration > Integrations
   - Add "Google Assistant" integration
   - Follow OAuth flow to link accounts

2. Configure exposed entities:
```yaml
# configuration.yaml
google_assistant:
  project_id: !secret google_project_id
  service_account: !include google_service_account.json
  report_state: true
  exposed_domains:
    - light
    - switch
    - lock
    - climate
    - scene
    - script
  entity_config:
    light.living_room:
      name: "Living Room Light"
      room: "Living Room"
```

#### 2.2 Create Voice Routines
In Google Assistant app:
1. Tap profile picture > Settings > Assistant > Routines
2. Create custom routines:

**Routine: "Good Morning"**
```
Trigger: Voice command "Hey Google, good morning"
Actions:
  - Control Home Assistant scenes: "Good Morning"
  - Read calendar events
  - Weather report
  - Start coffee maker
```

**Routine: "I'm Home"**
```
Trigger: Voice command "Hey Google, I'm home"
Actions:
  - Unlock front door
  - Turn on lights
  - Adjust thermostat
  - Disarm security
```

**Routine: "Goodnight"**
```
Trigger: Voice command "Hey Google, goodnight"
Actions:
  - Lock all doors
  - Turn off all lights
  - Arm security
  - Set thermostat to night mode
```

#### 2.3 Broadcast Messages
Use Home Assistant to broadcast to Google devices:

```yaml
script:
  announce_arrival:
    sequence:
      - service: notify.google_assistant_sdk
        data:
          message: "Welcome home! Dinner will be ready in 20 minutes."
```

---

### Step 3: Photo Auto-Upload to Home Server

#### 3.1 Setup Using Syncthing (Recommended)
1. Install **Syncthing** on Android from Play Store
2. Install Syncthing on your home server (Proxmox LXC or VM)
3. Configure:
   - On Android: Share `/DCIM/Camera` folder
   - On Server: Sync to `/home/user/photos/phone_backup`
   - Enable "Send Only" on Android (to save space)
   - Set to sync only on WiFi and while charging

#### 3.2 Alternative: Home Assistant Upload
Use Home Assistant to monitor and upload:

```yaml
# In Home Assistant, use a simple automation
automation:
  - alias: "Upload Photos When on WiFi and Charging"
    trigger:
      - platform: state
        entity_id: binary_sensor.mobile_app_<your_device>_is_charging
        to: 'on'
    condition:
      - condition: state
        entity_id: sensor.mobile_app_<your_device>_wifi_connection
        state: "<your_home_wifi_ssid>"
    action:
      - service: notify.mobile_app_<your_device>
        data:
          message: "command_broadcast_intent"
          data:
            intent_action: "com.android.camera.action.BACKUP_PHOTOS"
```

---

### Step 4: Custom Control Scripts

#### 4.1 Movie Mode Script
Add to Home Assistant:

```yaml
script:
  movie_mode:
    alias: "Movie Mode"
    sequence:
      # Dim all lights
      - service: light.turn_on
        target:
          entity_id: all
        data:
          brightness: 20
          rgb_color: [255, 100, 0]
      
      # Close blinds
      - service: cover.close_cover
        target:
          entity_id: cover.living_room_blinds
      
      # Turn on TV
      - service: media_player.turn_on
        target:
          entity_id: media_player.living_room_tv
      
      # Set Do Not Disturb
      - service: notify.mobile_app_<your_device>
        data:
          message: "command_dnd"
          data:
            command: "priority_only"
```

Create Quick Settings tile or widget button to trigger this script.

#### 4.2 Gaming Mode Script

```yaml
script:
  gaming_mode:
    alias: "Gaming Mode"
    sequence:
      # Bright lights
      - service: light.turn_on
        target:
          entity_id: light.gaming_room
        data:
          brightness: 255
          rgb_color: [0, 255, 0]
      
      # Turn on Xbox/PlayStation
      - service: switch.turn_on
        target:
          entity_id: switch.gaming_console
      
      # Notify others not to disturb
      - service: notify.all_devices
        data:
          message: "Gaming session started. Please do not disturb."
```

---

## Post-Setup Verification

### Checklist
Run through this checklist to verify everything is working:

#### Core Functions
- [ ] Home Assistant app connects on local WiFi
- [ ] Home Assistant app connects via Tailscale on mobile data
- [ ] Location tracking updates within 2 minutes of zone change
- [ ] Notifications are received promptly
- [ ] Quick Settings tiles work
- [ ] Home screen widgets display correct states

#### Automations
- [ ] Welcome Home automation triggers when arriving
- [ ] Away Mode automation triggers when leaving
- [ ] Battery low notification received
- [ ] DND sync works
- [ ] Driving detection works

#### Remote Access
- [ ] Can access Home Assistant remotely via Tailscale
- [ ] Can access Proxmox web interface
- [ ] Can control VMs from phone
- [ ] Can view camera feeds

#### Voice Control
- [ ] "Hey Google" triggers Home Assistant actions
- [ ] Voice routines work
- [ ] Broadcast messages play on home speakers

#### Performance
- [ ] Battery drain is acceptable (< 5% per day)
- [ ] App doesn't crash or freeze
- [ ] Location updates don't drain battery excessively
- [ ] No excessive mobile data usage

---

## Next Steps

### Ongoing Optimization
1. **Monitor Battery Usage**:
   - Check battery stats after 1 week
   - Disable unnecessary sensors if drain is high
   - Adjust update frequencies

2. **Refine Automations**:
   - Tweak zone sizes if false triggers occur
   - Adjust time delays for away mode
   - Add more conditions to prevent unwanted triggers

3. **Expand Integrations**:
   - Add more notification templates
   - Create additional voice routines
   - Integrate more smart devices

4. **Security Hardening**:
   - Review security checklist (see SECURITY_CHECKLIST.md)
   - Enable MFA on all services
   - Regularly update apps and firmware

### Advanced Features to Explore
- Tasker integration for complex automations
- NFC tags for location-independent triggers
- Wear OS companion app
- Custom Android app development

### Regular Maintenance
- **Weekly**: Check battery stats, review notification log
- **Monthly**: Update all apps, review automation performance
- **Quarterly**: Review security settings, update passwords

---

## Troubleshooting

For common issues and solutions, see [ANDROID_TROUBLESHOOTING.md](ANDROID_TROUBLESHOOTING.md)

For security guidelines, see [SECURITY_CHECKLIST.md](../../SECURITY_CHECKLIST.md)

---

## Support & Resources

### Official Documentation
- [Home Assistant Companion Docs](https://companion.home-assistant.io/)
- [Tailscale Android Setup](https://tailscale.com/kb/1080/android/)
- [Proxmox Mobile Access](https://pve.proxmox.com/wiki/Mobile_Access)

### Community Resources
- Home Assistant Community Forum
- r/homeassistant on Reddit
- Home Assistant Discord

### Your Infrastructure Docs
- Main README: [../../README.md](../../README.md)
- Troubleshooting: [ANDROID_TROUBLESHOOTING.md](ANDROID_TROUBLESHOOTING.md)
- Security: [../../SECURITY_CHECKLIST.md](../../SECURITY_CHECKLIST.md)

---

**Setup Complete! Enjoy your integrated smart home on Android! 🎉**
