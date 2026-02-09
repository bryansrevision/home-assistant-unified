# 🔥 Ulefone Armor 27T Pro - Advanced Features Integration

## Device-Specific Features

### Hardware Specifications
- **IR Blaster**: Infrared remote control capability
- **NFC**: Near Field Communication for automation triggers
- **AM/FM Radio**: Built-in radio receiver
- **Rugged Design**: IP68/IP69K water/dust resistant
- **Large Battery**: Extended battery life for automation
- **WiFi 6**: Fast wireless connectivity
- **Bluetooth 5.3**: Low-energy device connections

---

## 📡 Infrared (IR) Remote Control Integration

### Setup IR Universal Remote

1. **Install IR Remote Control App**
   ```
   Recommended Apps:
   - Mi Remote (Xiaomi)
   - AnyMote Universal Remote
   - SURE Universal Remote
   - Smart IR Remote (built-in if available)
   ```

2. **Home Assistant IR Integration**

Create custom integration for IR control:

```yaml
# config/home-assistant/ulefone-ir-control.yaml

# IR Remote Controls via Home Assistant
rest_command:
  send_ir_command:
    url: 'http://192.168.1.134:8123/api/webhook/ir_command'
    method: POST
    content_type: 'application/json'
    payload: '{"device": "{{ device }}", "command": "{{ command }}"}'

# IR Device Templates
input_select:
  ir_tv_commands:
    name: "TV Commands"
    options:
      - "Power"
      - "Volume Up"
      - "Volume Down"
      - "Channel Up"
      - "Channel Down"
      - "Mute"
      - "Input HDMI1"
      - "Input HDMI2"
    icon: mdi:television

  ir_ac_commands:
    name: "AC Commands"
    options:
      - "Power On"
      - "Power Off"
      - "Temp Up"
      - "Temp Down"
      - "Mode Cool"
      - "Mode Heat"
      - "Fan Low"
      - "Fan High"
    icon: mdi:air-conditioner

# IR Automation Scripts
script:
  ir_turn_on_entertainment:
    alias: "IR - Turn On Entertainment System"
    sequence:
      - service: rest_command.send_ir_command
        data:
          device: "tv"
          command: "power_on"
      - delay:
          seconds: 3
      - service: rest_command.send_ir_command
        data:
          device: "soundbar"
          command: "power_on"
      - delay:
          seconds: 2
      - service: rest_command.send_ir_command
        data:
          device: "tv"
          command: "hdmi1"

  ir_control_ac_comfort:
    alias: "IR - Set AC to Comfort Mode"
    sequence:
      - service: rest_command.send_ir_command
        data:
          device: "ac"
          command: "power_on"
      - delay:
          seconds: 2
      - service: rest_command.send_ir_command
        data:
          device: "ac"
          command: "temp_72"
      - service: rest_command.send_ir_command
        data:
          device: "ac"
          command: "mode_cool"
```

### IR Remote Widget Configuration

```yaml
# Android Widget for IR Control
widget_ir_remote:
  name: "IR Remote Control"
  size: "4x2"
  type: "button_widget"
  entities:
    - entity_id: script.ir_turn_on_entertainment
      label: "Entertainment"
      icon: mdi:television-play
    
    - entity_id: script.ir_control_ac_comfort
      label: "AC Comfort"
      icon: mdi:air-conditioner
    
    - entity_id: script.ir_tv_power_toggle
      label: "TV Power"
      icon: mdi:power
    
    - entity_id: script.ir_all_devices_off
      label: "All Off"
      icon: mdi:power-off
```

---

## 🏷️ NFC Tag Automation

### NFC Tag Setup

1. **Purchase NFC Tags**
   - NTAG213/215/216 compatible
   - 144-888 bytes storage
   - Waterproof stickers recommended

2. **NFC Tag Writer App**
   ```
   Recommended:
   - NFC Tools (Play Store)
   - TagWriter by NXP
   - Trigger (automation app)
   ```

### NFC Tag Locations and Actions

```yaml
# config/home-assistant/ulefone-nfc-automation.yaml

automation:
  # NFC Tag 1: Bedside (Goodnight Routine)
  - alias: "NFC - Bedside Goodnight"
    trigger:
      - platform: event
        event_type: tag_scanned
        event_data:
          tag_id: "nfc_bedside_001"
    action:
      - service: script.goodnight
      - service: notify.mobile_app_ulefone
        data:
          message: "Goodnight routine activated"

  # NFC Tag 2: Front Door (Leaving Home)
  - alias: "NFC - Front Door Departure"
    trigger:
      - platform: event
        event_type: tag_scanned
        event_data:
          tag_id: "nfc_door_002"
    action:
      - service: script.leaving_home
      - service: notify.mobile_app_ulefone
        data:
          message: "Leaving home routine activated. House secured."

  # NFC Tag 3: Car Dashboard (Driving Mode)
  - alias: "NFC - Car Driving Mode"
    trigger:
      - platform: event
        event_type: tag_scanned
        event_data:
          tag_id: "nfc_car_003"
    action:
      - service: notify.mobile_app_ulefone
        data:
          message: "command_dnd"
          data:
            command: "priority_only"
      - service: media_player.play_media
        target:
          entity_id: media_player.car_bluetooth
        data:
          media_content_type: "playlist"
          media_content_id: "driving_playlist"

  # NFC Tag 4: Office Desk (Work Mode)
  - alias: "NFC - Office Work Mode"
    trigger:
      - platform: event
        event_type: tag_scanned
        event_data:
          tag_id: "nfc_office_004"
    action:
      - service: script.work_focus_mode
      - service: input_select.select_option
        target:
          entity_id: input_select.house_mode
        data:
          option: "Away"

  # NFC Tag 5: Gym Bag (Exercise Mode)
  - alias: "NFC - Gym Exercise Mode"
    trigger:
      - platform: event
        event_type: tag_scanned
        event_data:
          tag_id: "nfc_gym_005"
    action:
      - service: notify.mobile_app_ulefone
        data:
          message: "Exercise mode activated. Tracking workout."
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.exercise_mode

  # NFC Tag 6: Wireless Charger (Charging Station)
  - alias: "NFC - Charging Station"
    trigger:
      - platform: event
        event_type: tag_scanned
        event_data:
          tag_id: "nfc_charger_006"
    action:
      - service: script.android_optimize_charging
      - service: notify.mobile_app_ulefone
        data:
          message: "Charging optimization enabled"
```

### NFC Tag Programming Guide

**Tag 1 - Bedside Table**:
```
Action: Launch Task
Task: Goodnight Routine
Webhook: https://your-ha-url/api/webhook/nfc_bedside_001
```

**Tag 2 - Front Door**:
```
Action: Launch Task
Task: Leaving Home
Webhook: https://your-ha-url/api/webhook/nfc_door_002
```

**Tag 3 - Car Dashboard**:
```
Action: Enable Driving Mode
Open App: Android Auto
Webhook: https://your-ha-url/api/webhook/nfc_car_003
```

---

## 📻 AM/FM Radio Integration

### Radio Automation

```yaml
# config/home-assistant/ulefone-radio.yaml

# Radio Presets
input_select:
  radio_presets:
    name: "Radio Station"
    options:
      - "FM 101.1 - News"
      - "FM 95.5 - Rock"
      - "FM 88.9 - Classical"
      - "AM 1050 - Talk Radio"
      - "FM 107.3 - Pop Music"
    icon: mdi:radio

# Radio Automation Scripts
script:
  radio_morning_news:
    alias: "Radio - Morning News"
    sequence:
      - service: notify.mobile_app_ulefone
        data:
          message: "command_broadcast_intent"
          data:
            intent_action: "android.intent.action.VIEW"
            intent_uri: "radio://fm/101.1"
      - delay:
          minutes: 30
      - service: notify.mobile_app_ulefone
        data:
          message: "Morning news complete"

  radio_workout_music:
    alias: "Radio - Workout Music"
    sequence:
      - service: notify.mobile_app_ulefone
        data:
          message: "command_broadcast_intent"
          data:
            intent_action: "android.intent.action.VIEW"
            intent_uri: "radio://fm/95.5"

# Automation: Play radio on alarm
automation:
  - alias: "Radio - Morning Alarm with News"
    trigger:
      - platform: state
        entity_id: sensor.mobile_app_ulefone_next_alarm
    condition:
      - condition: template
        value_template: >
          {{ (as_timestamp(states('sensor.mobile_app_ulefone_next_alarm')) - as_timestamp(now())) < 60 }}
    action:
      - service: script.radio_morning_news
```

---

## 🔐 Lockdown Mode & Security Banner

### Remote Session Detection

```yaml
# config/home-assistant/ulefone-security.yaml

# Detect Remote Sessions
binary_sensor:
  - platform: template
    sensors:
      ulefone_remote_session:
        friendly_name: "Remote Session Active"
        value_template: >
          {{ is_state('sensor.mobile_app_ulefone_adb_enabled', 'on') or
             is_state('sensor.mobile_app_ulefone_unknown_sources', 'on') }}
        icon_template: mdi:security

# Lockdown Mode Script
script:
  ulefone_lockdown_mode:
    alias: "Ulefone - Enable Lockdown Mode"
    sequence:
      - service: notify.mobile_app_ulefone
        data:
          message: "🔒 LOCKDOWN MODE ACTIVATED"
          title: "Security Alert"
          data:
            priority: max
            ttl: 0
            sticky: true
            color: "#FF0000"
            notification_icon: "mdi:lock"
      
      # Disable location sharing
      - service: device_tracker.see
        data:
          dev_id: ulefone_armor_27t_pro
          location_name: "hidden"
      
      # Enable DND
      - service: notify.mobile_app_ulefone
        data:
          message: "command_dnd"
          data:
            command: "total_silence"
      
      # Log security event
      - service: logbook.log
        data:
          name: "Ulefone Security"
          message: "Lockdown mode activated"
          entity_id: device_tracker.mobile_app_ulefone

  ulefone_display_security_banner:
    alias: "Ulefone - Display Security Banner"
    sequence:
      - service: notify.mobile_app_ulefone
        data:
          message: "⚠️ REMOTE SESSION DETECTED\n3rd party access active\nTerminal control enabled"
          title: "🔴 SECURITY ALERT"
          data:
            priority: max
            ttl: 0
            sticky: true
            color: "#FF0000"
            vibrationPattern: "100, 1000, 100, 1000"
            actions:
              - action: "TERMINATE_SESSION"
                title: "Terminate Session"
              - action: "LOCKDOWN_DEVICE"
                title: "Lockdown Device"

# Automation: Detect and alert on remote access
automation:
  - alias: "Security - Remote Session Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.ulefone_remote_session
        to: 'on'
    action:
      - service: script.ulefone_display_security_banner
      - service: notify.all_admins
        data:
          message: "Remote session detected on Ulefone device!"
          title: "Security Warning"

  # Auto-lockdown after hours
  - alias: "Security - Auto Lockdown After Hours"
    trigger:
      - platform: time
        at: "22:00:00"
    condition:
      - condition: state
        entity_id: device_tracker.mobile_app_ulefone
        state: 'not_home'
    action:
      - service: script.ulefone_lockdown_mode
```

---

## 📊 Daily Activities & Health Monitoring

### Daily Activity Tracking

```yaml
# config/home-assistant/ulefone-health-tracking.yaml

# Health & Activity Sensors
sensor:
  - platform: template
    sensors:
      ulefone_daily_steps:
        friendly_name: "Daily Steps"
        value_template: "{{ states('sensor.mobile_app_ulefone_steps_sensor') }}"
        unit_of_measurement: "steps"
        icon_template: mdi:walk

      ulefone_daily_distance:
        friendly_name: "Daily Distance"
        value_template: >
          {{ (states('sensor.mobile_app_ulefone_steps_sensor') | int * 0.0008) | round(2) }}
        unit_of_measurement: "km"
        icon_template: mdi:map-marker-distance

      ulefone_calories_burned:
        friendly_name: "Calories Burned"
        value_template: >
          {{ (states('sensor.mobile_app_ulefone_steps_sensor') | int * 0.04) | round(0) }}
        unit_of_measurement: "kcal"
        icon_template: mdi:fire

# Daily Health Report Script
script:
  ulefone_daily_health_report:
    alias: "Ulefone - Daily Health Report"
    sequence:
      - service: notify.mobile_app_ulefone
        data:
          message: |
            📊 Daily Health Report
            
            🚶 Steps: {{ states('sensor.ulefone_daily_steps') }}
            📏 Distance: {{ states('sensor.ulefone_daily_distance') }} km
            🔥 Calories: {{ states('sensor.ulefone_calories_burned') }} kcal
            💓 Avg Heart Rate: {{ states('sensor.ulefone_heart_rate') }} bpm
            😴 Sleep: {{ states('sensor.ulefone_sleep_hours') }} hours
            🔋 Battery Used: {{ 100 - states('sensor.mobile_app_ulefone_battery_level') | int }}%
            
            Goal Progress: {{ (states('sensor.ulefone_daily_steps') | int / 10000 * 100) | round(0) }}%
          title: "Health Report"
          data:
            priority: low

# Automation: Daily health report
automation:
  - alias: "Health - Daily Summary Report"
    trigger:
      - platform: time
        at: "21:00:00"
    action:
      - service: script.ulefone_daily_health_report

  # Step goal achievement
  - alias: "Health - Step Goal Achieved"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ulefone_daily_steps
        above: 10000
    action:
      - service: notify.mobile_app_ulefone
        data:
          message: "🎉 Congratulations! You've reached your 10,000 step goal!"
          title: "Goal Achieved"
          data:
            priority: normal
            color: "#4CAF50"
```

---

## 📱 Device Status Dashboard

### Comprehensive Device Monitoring

```yaml
# config/home-assistant/ulefone-status-dashboard.yaml

# Device Status Sensors
sensor:
  - platform: template
    sensors:
      ulefone_system_status:
        friendly_name: "System Status"
        value_template: >
          {% set battery = states('sensor.mobile_app_ulefone_battery_level') | int %}
          {% set charging = is_state('binary_sensor.mobile_app_ulefone_is_charging', 'on') %}
          {% set wifi = states('sensor.mobile_app_ulefone_wifi_connection') %}
          {% if battery < 20 and not charging %}
            Critical
          {% elif battery < 50 and not charging %}
            Warning
          {% elif wifi == 'not_connected' %}
            Offline
          {% else %}
            Normal
          {% endif %}
        icon_template: >
          {% set status = states('sensor.ulefone_system_status') %}
          {% if status == 'Critical' %}
            mdi:alert-circle
          {% elif status == 'Warning' %}
            mdi:alert
          {% else %}
            mdi:check-circle
          {% endif %}

# Daily Status Summary Script
script:
  ulefone_status_summary:
    alias: "Ulefone - System Status Summary"
    sequence:
      - service: notify.mobile_app_ulefone
        data:
          message: |
            📱 Ulefone Armor 27T Pro Status
            
            🔋 Battery: {{ states('sensor.mobile_app_ulefone_battery_level') }}%
            {{ '⚡ Charging' if is_state('binary_sensor.mobile_app_ulefone_is_charging', 'on') else '🔌 Not Charging' }}
            
            📶 WiFi: {{ states('sensor.mobile_app_ulefone_wifi_connection') }}
            📡 Network: {{ states('sensor.mobile_app_ulefone_mobile_network_type') }}
            
            📍 Location: {{ states('sensor.mobile_app_ulefone_geocoded_location') }}
            🏃 Activity: {{ states('sensor.mobile_app_ulefone_activity') }}
            
            💾 Storage: {{ states('sensor.mobile_app_ulefone_storage_free') }} GB free
            🧠 RAM: {{ states('sensor.mobile_app_ulefone_memory_free') }} MB free
            
            🌡️ Temperature: {{ states('sensor.mobile_app_ulefone_battery_temperature') }}°C
            ⏱️ Uptime: {{ states('sensor.mobile_app_ulefone_uptime') }}
          title: "Device Status"

# Automation: Morning status report
automation:
  - alias: "Status - Morning Device Report"
    trigger:
      - platform: time
        at: "08:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.workday_sensor
        state: 'on'
    action:
      - service: script.ulefone_status_summary
```

---

## 🔗 Quick Reference

### NFC Tag Locations
1. **Bedside**: Goodnight routine
2. **Front Door**: Leaving home
3. **Car Dashboard**: Driving mode
4. **Office Desk**: Work mode
5. **Gym Bag**: Exercise mode
6. **Charging Station**: Charging optimization

### IR Remote Devices
- Living Room TV
- Bedroom TV  
- Air Conditioner
- Sound System
- Media Players

### Daily Automations
- 08:00 - Morning status report
- 21:00 - Health summary
- 22:00 - Auto-lockdown (if away)
- On alarm - Radio news

### Security Features
- Remote session detection
- Auto-lockdown mode
- Security banners
- Access logging

---

**Next Steps**: 
1. Install NFC tags in strategic locations
2. Program IR remote codes
3. Configure health tracking sensors
4. Test all automations
5. Review security settings

See [AI_AGENT_CONTROL.md](./AI_AGENT_CONTROL.md) for AI integration features.
