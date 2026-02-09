# 🔗 IFTTT & Tasker Advanced Automation

## Overview

This guide covers advanced automation using IFTTT (If This Then That) and Tasker for Android, integrated with your home automation infrastructure.

---

## 🌐 IFTTT Integration

### Setup IFTTT with Home Assistant

#### 1. Install IFTTT App
```
Google Play Store → Search "IFTTT" → Install
Create account or sign in
```

#### 2. Configure Webhooks

**In Home Assistant**:
```yaml
# configuration.yaml
ifttt:
  key: !secret ifttt_webhook_key
```

**Get Your Webhook Key**:
1. Visit: https://ifttt.com/maker_webhooks
2. Click "Documentation"
3. Copy your webhook key
4. Add to `secrets.yaml`: `ifttt_webhook_key: YOUR_KEY_HERE`

---

### IFTTT Applets for Home Automation

#### Applet 1: Location-Based Actions

**Trigger**: Android location enters area
**Action**: Webhook to Home Assistant

```
IF: Android Device → Location → You enter an area
THEN: Webhooks → Make a web request

URL: https://your-ha-url/api/webhook/ifttt_location_trigger
Method: POST
Content Type: application/json
Body:
{
  "trigger": "entering_home",
  "device": "ulefone_armor",
  "timestamp": "{{OccurredAt}}"
}
```

**Home Assistant Automation**:
```yaml
automation:
  - alias: "IFTTT - Location Enter Home"
    trigger:
      - platform: webhook
        webhook_id: ifttt_location_trigger
    condition:
      - condition: template
        value_template: "{{ trigger.json.trigger == 'entering_home' }}"
    action:
      - service: script.arriving_home
```

#### Applet 2: Battery Charging Reminder

**Trigger**: Android battery level below 20%
**Action**: Notification + HA webhook

```
IF: Android Device → Battery level drops below → 20%
THEN: 
  1. Notification → Send notification from IFTTT app
  2. Webhooks → Make web request to HA
```

#### Applet 3: Weather-Based Automation

**Trigger**: Weather forecast tomorrow
**Action**: Prepare home for weather

```
IF: Weather Underground → Tomorrow's forecast calls for
THEN: Webhooks → Adjust home automation

Examples:
- Rain → Close windows, arm leak sensors
- Snow → Increase heating, alert to check pipes
- Hot → Pre-cool house, close blinds
```

#### Applet 4: Calendar Integration

**Trigger**: Google Calendar event starts
**Action**: Home automation scene

```
IF: Google Calendar → Event from search starts
  Search for: "Meeting" OR "Work"
THEN: Webhooks → Enable work mode

URL: https://your-ha-url/api/webhook/calendar_work_mode
Method: POST
Body:
{
  "event": "{{Title}}",
  "start_time": "{{Starts}}",
  "action": "enable_work_mode"
}
```

#### Applet 5: Smart Device Triggers

**Trigger**: SmartThings device state change
**Action**: Notify and log in HA

```
IF: SmartThings → Device turned on/off
THEN: 
  1. Notification
  2. Webhooks → Log to Home Assistant
```

#### Applet 6: Email-Based Commands

**Trigger**: Email received with subject
**Action**: Execute home command

```
IF: Email → New email from specific sender
  Subject contains: "Execute: [command]"
THEN: Webhooks → Parse and execute command
```

---

### Advanced IFTTT Recipes

#### Recipe 1: Multi-Service Backup Trigger

```yaml
# Home Assistant trigger
automation:
  - alias: "IFTTT - Trigger Multi-Service Backup"
    trigger:
      - platform: time
        at: "02:00:00"
    action:
      - service: ifttt.trigger
        data:
          event: "backup_all_services"
          value1: "{{ now().strftime('%Y-%m-%d') }}"
          value2: "{{ states('sensor.backup_size') }}"

# IFTTT Applets
Applet A: Backup to Google Drive
IF: Webhooks → backup_all_services
THEN: Google Drive → Upload file

Applet B: Backup to Dropbox
IF: Webhooks → backup_all_services
THEN: Dropbox → Upload file

Applet C: Notification
IF: Webhooks → backup_all_services
THEN: Notification → Backup started
```

#### Recipe 2: Social Media Home Status

```yaml
# Post home status to social media
automation:
  - alias: "IFTTT - Share Vacation Mode"
    trigger:
      - platform: state
        entity_id: input_boolean.vacation_mode
        to: 'on'
    action:
      - service: ifttt.trigger
        data:
          event: "vacation_mode_enabled"
          value1: "{{ states('sensor.indoor_temperature') }}"

# IFTTT Applet
IF: Webhooks → vacation_mode_enabled
THEN: 
  - Twitter → Post tweet: "Home on vacation mode 🏖️"
  - Facebook → Create status: "Away for vacation!"
```

#### Recipe 3: Voice Assistant Cross-Platform

```yaml
# Trigger from multiple voice assistants
automation:
  # Google Assistant via IFTTT
  - alias: "IFTTT - Google Assistant Command"
    trigger:
      - platform: webhook
        webhook_id: google_assistant_command
    action:
      - service: script.process_voice_command
        data:
          command: "{{ trigger.json.command }}"
          source: "google_assistant"

# IFTTT Applet
IF: Google Assistant → Say a phrase with a text ingredient
  "Tell my home to $"
THEN: Webhooks → Send command to HA
```

---

## 📱 Tasker Advanced Automation

### Setup Tasker

1. **Install Tasker**: Play Store → Tasker ($3.49)
2. **Install Plugins**:
   - AutoApps
   - AutoTools
   - AutoLocation
   - AutoNotification
   - AutoInput

3. **Grant Permissions**:
   - Accessibility (for AutoInput)
   - Location (always)
   - Notification access
   - Device admin (optional, for advanced features)

---

### Tasker Profiles for Home Automation

#### Profile 1: Home WiFi Connected

**Context**: WiFi Connected (Your home SSID)

**Tasks**:
```
Task: Home WiFi Actions
1. HTTP Post
   URL: http://192.168.1.134:8123/api/webhook/tasker_home_wifi
   Content Type: application/json
   Body: {"device":"ulefone","action":"wifi_connected","ssid":"%WIFII"}
   
2. Set Variable %HOME_WIFI = true

3. Notify
   Title: Home Network
   Text: Connected to home WiFi
```

#### Profile 2: Location-Based Automation

**Context**: Location (Cell Near or GPS)

**Entry Task**:
```
Task: Entering Home Zone
1. HTTP Post
   URL: http://192.168.1.134:8123/api/webhook/tasker_entering_home
   
2. Variable Set %AT_HOME = true

3. Flash "Welcome Home!"

4. Launch App → Home Assistant

5. Vibrate Pattern → 0,100,100,100
```

**Exit Task**:
```
Task: Leaving Home Zone
1. HTTP Post
   URL: http://192.168.1.134:8123/api/webhook/tasker_leaving_home
   
2. Variable Set %AT_HOME = false

3. Notify → Reminder to lock doors

4. If %AUTOLOCK = true
   HTTP Post → Lock all doors
```

#### Profile 3: Driving Mode Detection

**Context**: Variable Value %ACTIVITY ~ in_vehicle

**Task**:
```
Task: Enable Driving Mode
1. Auto Mode → On

2. Do Not Disturb → Priority Only

3. Launch App → Android Auto

4. HTTP Post
   URL: http://192.168.1.134:8123/api/webhook/tasker_driving
   Body: {"device":"ulefone","activity":"driving","speed":"%LOCSPD"}

5. Say → "Driving mode enabled"
```

#### Profile 4: NFC Tag Scan

**Context**: NFC Tag (specific tag ID)

**Task**:
```
Task: NFC Bedside Scanned
1. Variable Set %SCANNED_TAG = %nfc_id

2. HTTP Post
   URL: http://192.168.1.134:8123/api/webhook/nfc_scanned
   Body: {"tag_id":"%nfc_id","location":"bedside"}

3. Wait 1 second

4. Get Location

5. Flash "Goodnight routine starting..."
```

#### Profile 5: Battery Level Triggers

**Context**: Battery Level < 20%

**Task**:
```
Task: Low Battery Actions
1. HTTP Post → Notify HA of low battery

2. Brightness → 50%

3. Auto-Sync → Off

4. Notify
   Title: Low Battery
   Text: Battery at %BATT%. Power saving enabled.

5. If %AT_HOME = true
   Flash "Please charge your phone"
```

#### Profile 6: Time-Based Automation

**Context**: Time 22:00-06:00 + At Home

**Task**:
```
Task: Night Mode
1. Do Not Disturb → On

2. Display Brightness → 10%

3. Blue Light Filter → On

4. HTTP Post
   URL: http://192.168.1.134:8123/api/webhook/tasker_night_mode
   Body: {"mode":"night","time":"%TIME"}

5. Launch App → Sleep Tracker

6. Vibrate → 0,50
```

---

### Advanced Tasker Tasks

#### Task 1: Voice Command Processor

```
Task: Process Voice Command
1. Get Voice
   Language: English
   Timeout: 5 seconds
   
2. Variable Set %VOICE_CMD = %VOICE

3. If %VOICE_CMD ~ *lights off*
   HTTP Post → Turn off all lights
   Say → "Turning off all lights"

4. Else If %VOICE_CMD ~ *lock doors*
   HTTP Post → Lock all doors
   Say → "Locking all doors"

5. Else If %VOICE_CMD ~ *temperature*
   HTTP Get → Get temperature from HA
   Say → "Temperature is %temperature degrees"

6. Else
   Say → "I didn't understand that command"
```

#### Task 2: Smart Response System

```
Task: Auto-Reply When Driving
1. AutoNotification Query
   App: Messages, WhatsApp, SMS
   
2. If %ACTIVITY = in_vehicle
   Variable Set %SENDER = %anapp
   
3. Perform Task: Send Auto Reply
   Priority: 5
   Parameter 1: %SENDER
   Parameter 2: "I'm driving. I'll respond when safe."

4. HTTP Post → Log auto-reply to HA
```

#### Task 3: Security Alert Response

```
Task: Security Alert Handler
1. AutoNotification Intercept
   App: Home Assistant
   Title: *Security Alert*
   
2. Flash "SECURITY ALERT!"

3. Vibrate Pattern → 0,500,100,500,100,500

4. Set Ringer Volume → 7

5. Play Sound → alarm.mp3

6. Launch App → Home Assistant

7. AutoNotification Action Buttons
   Button 1: Call 911
   Button 2: View Cameras
   Button 3: False Alarm
```

#### Task 4: Automated Photo Backup

```
Task: Backup New Photos
1. List Files
   Dir: /DCIM/Camera
   Match: *.jpg,*.png
   Variable: %photos
   
2. For %photo in %photos
   HTTP Post
   URL: http://192.168.1.134:3000/api/upload
   File: %photo
   
3. If %http_response_code = 200
   Delete File: %photo
   Flash "Photo backed up: %photo"
```

#### Task 5: Context-Aware Notifications

```
Task: Smart Notification Filter
1. AutoNotification Query
   Persistency Type: Both
   
2. If %AT_HOME = false AND %PRIORITY = low
   AutoNotification Cancel
   
3. Else If %ACTIVITY = in_vehicle
   AutoNotification → Convert to voice
   Say → "Message from %sender: %message"

4. Else If %SLEEP_MODE = true
   AutoNotification → Delay until morning
```

---

### Tasker Scenes for Home Control

#### Scene 1: Home Control Dashboard

```
Scene: Home Dashboard
Layout:
- 4x4 Grid
- Buttons for:
  • All Lights On/Off
  • Lock/Unlock Doors
  • Arm/Disarm Security
  • Temperature Control
  • Scene Selection (Movie, Sleep, Away)
  • Emergency (Panic, Fire)

Each button triggers HTTP Post to HA webhook
```

#### Scene 2: Quick Actions Menu

```
Scene: Quick Actions
- Circular menu (AutoTools Web Screen)
- Icons for:
  • Home Status
  • Turn Off Everything
  • Goodnight
  • Leaving Home
  • I'm Back

Swipe gestures:
- Swipe up → Home Status
- Swipe down → All Off
- Swipe left → Previous scene
- Swipe right → Next scene
```

---

### Tasker Variables for Home Automation

```
Global Variables:
%HOME_WIFI = true/false
%AT_HOME = true/false
%ACTIVITY = still/walking/in_vehicle
%HOUSE_MODE = normal/away/sleep/party
%LAST_LOCATION = home/work/gym
%AUTOLOCK = true/false
%SLEEP_MODE = true/false
%VACATION_MODE = true/false

Task Variables:
%TEMP = Current temperature
%LIGHTS_ON = Number of lights on
%DOORS_LOCKED = All doors locked status
%SECURITY_ARMED = Security system status
```

---

### Integration with Home Assistant

#### Webhook Handlers in HA

```yaml
# config/home-assistant/tasker-webhooks.yaml

automation:
  # Generic Tasker webhook
  - alias: "Tasker - Generic Action"
    trigger:
      - platform: webhook
        webhook_id: tasker_action
    action:
      - service: script.process_tasker_action
        data:
          action: "{{ trigger.json.action }}"
          device: "{{ trigger.json.device }}"
          data: "{{ trigger.json }}"

  # WiFi connection webhook
  - alias: "Tasker - WiFi Connected"
    trigger:
      - platform: webhook
        webhook_id: tasker_home_wifi
    action:
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.ulefone_home_wifi

  # Driving mode webhook
  - alias: "Tasker - Driving Detected"
    trigger:
      - platform: webhook
        webhook_id: tasker_driving
    action:
      - service: script.android_driving_started

  # NFC scan webhook
  - alias: "Tasker - NFC Scanned"
    trigger:
      - platform: webhook
        webhook_id: nfc_scanned
    action:
      - service: script.handle_nfc_scan
        data:
          tag_id: "{{ trigger.json.tag_id }}"
          location: "{{ trigger.json.location }}"

script:
  process_tasker_action:
    alias: "Process Tasker Action"
    fields:
      action:
        description: "Action type"
      device:
        description: "Device name"
      data:
        description: "Additional data"
    sequence:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ action == 'lights_off' }}"
            sequence:
              - service: light.turn_off
                target:
                  entity_id: all
          
          - conditions:
              - condition: template
                value_template: "{{ action == 'lock_all' }}"
            sequence:
              - service: lock.lock
                target:
                  entity_id: all
        
        default:
          - service: notify.mobile_app_ulefone
            data:
              message: "Unknown Tasker action: {{ action }}"
```

---

## 🔗 Combined IFTTT + Tasker Workflows

### Workflow 1: Intelligent Home Entry

```
1. Tasker detects home WiFi
2. Tasker posts to IFTTT webhook
3. IFTTT triggers multiple services:
   - Disarm security via HA
   - Turn on lights
   - Unlock door
   - Start music
   - Adjust thermostat
4. Tasker receives confirmation
5. Tasker shows notification
```

### Workflow 2: Vacation Mode Activation

```
1. User enables vacation mode in HA
2. HA triggers IFTTT webhook
3. IFTTT:
   - Stops mail delivery
   - Forwards calls
   - Posts social media status
4. Tasker receives vacation mode flag
5. Tasker enables:
   - Location spoofing
   - Auto-reply messages
   - Random light patterns
```

### Workflow 3: Emergency Response

```
1. Security sensor triggers in HA
2. HA sends webhook to IFTTT
3. IFTTT:
   - Sends SMS to emergency contacts
   - Calls phone
   - Posts to security service
4. Tasker receives emergency notification
5. Tasker:
   - Maximum volume
   - Persistent alarm
   - Launches camera app
   - Starts recording
```

---

## 📱 Tasker Plugins Configuration

### AutoLocation

```
Profile: Geofence Monitoring
Context: AutoLocation → Geofence
Radius: 100m
Center: Home coordinates

Entry: Arriving home task
Exit: Leaving home task
```

### AutoNotification

```
Profile: Priority Notification Handler
Context: AutoNotification Intercept
Apps: Home Assistant, Security
Priority: High

Task: Process High Priority
1. Extract notification content
2. Analyze urgency
3. Take appropriate action
4. Log to HA
```

### AutoInput

```
Profile: Auto-Unlock Screen
Context: Display Off + At Home

Task: Smart Unlock
1. Wait 1 second
2. AutoInput → Unlock with pattern
3. Launch Home Assistant app
```

---

## 🎯 Best Practices

### IFTTT
- ✅ Use descriptive applet names
- ✅ Test thoroughly before deploying
- ✅ Monitor rate limits (free tier: 2 applets)
- ✅ Use webhooks for HA integration
- ✅ Enable applets only when needed

### Tasker
- ✅ Use meaningful variable names
- ✅ Add comments to complex tasks
- ✅ Test each profile independently
- ✅ Optimize battery usage
- ✅ Use collision handling (abort/queue)
- ✅ Keep tasks modular and reusable

### Integration
- ✅ Secure all webhooks with authentication
- ✅ Use HTTPS when possible
- ✅ Log all automated actions
- ✅ Create fallback/error handling
- ✅ Document all workflows

---

## 🔧 Troubleshooting

### IFTTT Issues
**Applet not triggering**:
- Check internet connection
- Verify webhook URL
- Check IFTTT service status
- Review applet logs

**Slow execution**:
- IFTTT can have delays (seconds to minutes)
- Consider using Tasker for time-sensitive actions

### Tasker Issues
**Profile not activating**:
- Check context conditions
- Verify all permissions granted
- Review collision handling
- Check profile priority

**High battery usage**:
- Reduce location update frequency
- Use WiFi instead of GPS when possible
- Disable unused profiles

---

## 📚 Resources

- **IFTTT Platform**: https://ifttt.com/
- **Tasker Wiki**: https://tasker.joaoapps.com/
- **AutoApps**: https://joaoapps.com/
- **HA IFTTT Integration**: https://www.home-assistant.io/integrations/ifttt/

---

**Next**: Configure your specific workflows and test thoroughly before relying on them for critical automation!
