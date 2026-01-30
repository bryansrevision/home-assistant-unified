# Home Assistant Configuration

## Overview

This document describes the Home Assistant configuration for Android device integration on the Proxmox infrastructure.

## Server Configuration

### Instance Details
- **URL**: http://192.168.1.201:8123
- **HTTPS URL**: https://192.168.1.201:8123 (if SSL configured)
- **Internal URL**: http://192.168.1.201:8123
- **Entities**: 263 configured entities

### Installation Location
- **Platform**: Proxmox VE (VM or LXC)
- **Host**: 192.168.1.185:8006
- **Container/VM IP**: 192.168.1.201

## Configuration Files

### configuration.yaml

Basic configuration structure:

```yaml
# Home Assistant Core Configuration
homeassistant:
  name: Home
  latitude: !secret home_latitude
  longitude: !secret home_longitude
  elevation: !secret home_elevation
  unit_system: metric
  time_zone: !secret timezone
  internal_url: "http://192.168.1.201:8123"
  external_url: !secret external_url

# Enable HTTP
http:
  server_port: 8123
  use_x_forwarded_for: true
  trusted_proxies:
    - 192.168.1.0/24
  ip_ban_enabled: true
  login_attempts_threshold: 5

# Enable API
api:

# Enable frontend
frontend:
  themes: !include_dir_merge_named themes

# Enable config editor
config:

# Enable system health
system_health:

# Enable history
history:
  include:
    domains:
      - sensor
      - binary_sensor
      - switch
      - light
      - climate
      - cover
      - lock

# Enable recorder for database
recorder:
  db_url: !secret db_url
  purge_keep_days: 7
  commit_interval: 30
  exclude:
    domains:
      - automation
      - updater
    entity_globs:
      - sensor.weather_*

# Enable logbook
logbook:

# Enable mobile app
mobile_app:

# Enable person tracking
person:

# Enable zone detection
zone:
  - name: Home
    latitude: !secret home_latitude
    longitude: !secret home_longitude
    radius: 100
    icon: mdi:home

  - name: Work
    latitude: !secret work_latitude
    longitude: !secret work_longitude
    radius: 200
    icon: mdi:briefcase

# Enable device tracker
device_tracker:

# MQTT Configuration
mqtt:
  broker: 192.168.1.201
  port: 1883
  username: !secret mqtt_username
  password: !secret mqtt_password
  discovery: true
  discovery_prefix: homeassistant
  birth_message:
    topic: 'homeassistant/status'
    payload: 'online'
  will_message:
    topic: 'homeassistant/status'
    payload: 'offline'

# REST API for AI Automation
rest_command:
  ai_automation_trigger:
    url: "http://192.168.1.201:5000/api/automation/trigger"
    method: POST
    headers:
      Authorization: !secret ai_automation_token
      Content-Type: "application/json"
    payload: '{"automation_id": "{{ automation_id }}", "trigger": "{{ trigger }}"}'

# Notify configuration for Android
notify:
  - name: mobile_app_android
    platform: group
    services:
      - service: mobile_app_<device_name>

# Webhooks for external services
webhook:

# Automation split files
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

# Custom integration includes
sensor: !include sensors.yaml
binary_sensor: !include binary_sensors.yaml
```

### secrets.yaml

Template for storing sensitive information:

```yaml
# Geographic coordinates
home_latitude: XX.XXXX
home_longitude: XX.XXXX
home_elevation: XXX
timezone: "America/New_York"

# Work location (if used)
work_latitude: XX.XXXX
work_longitude: XX.XXXX

# External URL (via Tailscale or other)
external_url: "https://your-tailscale-url.ts.net:8123"

# Database
db_url: "postgresql://homeassistant:password@localhost/homeassistant"

# MQTT Credentials
mqtt_username: "homeassistant"
mqtt_password: "your-secure-mqtt-password"

# API Tokens
ai_automation_token: "Bearer your-api-token-here"
mcp_hub_token: "your-mcp-hub-token"

# Authentication
http_password: "your-secure-password"
```

### automations.yaml

Example automations for Android integration:

```yaml
# Android Device Connected to Home WiFi
- id: android_device_home
  alias: "Android Device Arrived Home"
  trigger:
    - platform: state
      entity_id: device_tracker.android_phone
      to: 'home'
  condition:
    - condition: state
      entity_id: person.owner
      state: 'not_home'
  action:
    - service: notify.mobile_app_android
      data:
        message: "Welcome home! Adjusting settings."
    - service: light.turn_on
      target:
        entity_id: light.living_room
    - service: climate.set_temperature
      target:
        entity_id: climate.main
      data:
        temperature: 22

# Battery Low Alert
- id: android_battery_low
  alias: "Android Battery Low"
  trigger:
    - platform: numeric_state
      entity_id: sensor.android_phone_battery_level
      below: 20
  condition:
    - condition: state
      entity_id: binary_sensor.android_phone_is_charging
      state: 'off'
  action:
    - service: notify.mobile_app_android
      data:
        message: "Battery low ({{ states('sensor.android_phone_battery_level') }}%). Please charge."
        data:
          priority: high
          ttl: 0

# Critical System Alert
- id: system_alert_to_android
  alias: "Send Critical System Alert"
  trigger:
    - platform: state
      entity_id: binary_sensor.critical_system_alert
      to: 'on'
  action:
    - service: notify.mobile_app_android
      data:
        message: "Critical system alert: {{ trigger.to_state.attributes.message }}"
        title: "⚠️ System Alert"
        data:
          priority: high
          ttl: 0
          channel: critical_alerts
          actions:
            - action: "VIEW_SYSTEM"
              title: "View System"
            - action: "ACKNOWLEDGE"
              title: "Acknowledge"

# Actionable Notification Response
- id: handle_android_notification_action
  alias: "Handle Android Notification Action"
  trigger:
    - platform: event
      event_type: mobile_app_notification_action
      event_data:
        action: 'LOCK_DOOR'
  action:
    - service: lock.lock
      target:
        entity_id: lock.front_door
    - service: notify.mobile_app_android
      data:
        message: "Front door locked"

# Location-based Automation
- id: android_leaving_home
  alias: "Android Device Left Home"
  trigger:
    - platform: state
      entity_id: device_tracker.android_phone
      from: 'home'
      to: 'not_home'
      for:
        minutes: 5
  action:
    - service: notify.mobile_app_android
      data:
        message: "You've left home. Securing..."
    - service: script.away_mode
```

## Android Mobile App Integration

### Sensors from Android Device

The Home Assistant mobile app provides numerous sensors:

```yaml
# sensor entities created automatically:
# sensor.android_phone_battery_level
# sensor.android_phone_battery_state
# sensor.android_phone_battery_temperature
# sensor.android_phone_charger_type
# sensor.android_phone_wifi_connection
# sensor.android_phone_wifi_bssid
# binary_sensor.android_phone_is_charging
# binary_sensor.android_phone_interactive
# sensor.android_phone_last_reboot
# sensor.android_phone_last_update
# sensor.android_phone_steps_sensor
```

### Notification Channels

Configure notification channels in `configuration.yaml`:

```yaml
mobile_app:
  android:
    notification_channels:
      critical_alerts:
        name: "Critical Alerts"
        description: "Important system alerts"
        importance: high
        
      home_automation:
        name: "Home Automation"
        description: "Automation notifications"
        importance: default
        
      information:
        name: "Information"
        description: "General information"
        importance: low
```

## Integration with Other Services

### MCP Hub Integration

```yaml
# REST sensor for MCP Hub status
sensor:
  - platform: rest
    name: "MCP Hub Status"
    resource: "http://192.168.1.201:3000/api/status"
    method: GET
    headers:
      Authorization: !secret mcp_hub_token
    value_template: "{{ value_json.status }}"
    json_attributes:
      - services
      - uptime
      - version
    scan_interval: 60
```

### AI Automation Integration

```yaml
# Template sensor for AI automation
sensor:
  - platform: template
    sensors:
      ai_automation_status:
        friendly_name: "AI Automation Status"
        value_template: >
          {% set status = states('sensor.ai_automation_api_status') %}
          {% if status == 'online' %}
            Active
          {% else %}
            Offline
          {% endif %}
        icon_template: >
          {% if is_state('sensor.ai_automation_api_status', 'online') %}
            mdi:robot
          {% else %}
            mdi:robot-off
          {% endif %}
```

### Zigbee2MQTT Integration

```yaml
# Zigbee2MQTT Bridge
mqtt:
  sensor:
    - name: "Zigbee2MQTT Bridge State"
      state_topic: "zigbee2mqtt/bridge/state"
      icon: mdi:zigbee
      
    - name: "Zigbee2MQTT Version"
      state_topic: "zigbee2mqtt/bridge/info"
      value_template: "{{ value_json.version }}"
```

## Backup Configuration

### Automated Backups

```yaml
# Automation for configuration backup
automation:
  - id: daily_backup
    alias: "Daily Configuration Backup"
    trigger:
      - platform: time
        at: "03:00:00"
    action:
      - service: hassio.backup_full
        data:
          name: "Automated backup {{ now().strftime('%Y-%m-%d') }}"
      - service: notify.mobile_app_android
        data:
          message: "Daily backup completed successfully"
```

## Performance Optimization

### Recorder Optimization

```yaml
recorder:
  auto_purge: true
  purge_keep_days: 7
  commit_interval: 5
  exclude:
    domains:
      - automation
      - group
      - scene
      - script
      - updater
    entities:
      - sun.sun
      - sensor.date
      - sensor.time
```

### History Optimization

```yaml
history:
  use_include_order: true
  include:
    domains:
      - sensor
      - binary_sensor
      - switch
      - light
  exclude:
    entities:
      - sensor.last_boot
      - sensor.uptime
```

## Troubleshooting

### Enable Debug Logging

```yaml
logger:
  default: info
  logs:
    homeassistant.components.mobile_app: debug
    homeassistant.components.mqtt: debug
    homeassistant.components.device_tracker: debug
```

### Check Configuration

```bash
# SSH into Home Assistant
ha core check

# View logs
ha core logs

# Restart Home Assistant
ha core restart
```

## Security Hardening

### Authentication

```yaml
# Use authentication providers
auth_providers:
  - type: homeassistant
  - type: trusted_networks
    trusted_networks:
      - 192.168.1.0/24
    trusted_users:
      192.168.1.0/24:
        - user_id_here
    allow_bypass_login: true
```

### IP Filtering

```yaml
http:
  ip_ban_enabled: true
  login_attempts_threshold: 5
  use_x_forwarded_for: true
  trusted_proxies:
    - 192.168.1.0/24
```

## Monitoring

### System Monitor Integration

```yaml
sensor:
  - platform: systemmonitor
    resources:
      - type: disk_use_percent
        arg: /
      - type: memory_use_percent
      - type: processor_use
      - type: last_boot
```

## Additional Resources

- [Home Assistant Documentation](https://www.home-assistant.io/docs/)
- [Mobile App Documentation](https://companion.home-assistant.io/)
- [MQTT Documentation](https://www.home-assistant.io/integrations/mqtt/)
