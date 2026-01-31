# IFTTT Webhooks Integration Setup Guide
# Home Assistant Unified Integration
# Updated: January 31, 2026

## 📋 Overview

IFTTT (If This Then That) integration allows Home Assistant to:
- **Send events TO IFTTT** (trigger IFTTT applets from HA)
- **Receive webhooks FROM IFTTT** (trigger HA automations from mobile
  apps/services)
- Create powerful mobile automations
- Integrate with 600+ services (Google, Alexa, iOS shortcuts, Android, etc.)

**Integration File**: `integrations/ifttt-webhooks.yaml`



## 🔧 Setup Instructions

### Step 1: Get Your IFTTT Webhook Key

1. **Go to IFTTT Webhooks Settings**
   - Visit: https://ifttt.com/maker_webhooks/settings
   - Sign in to your IFTTT account

2. **Copy Your Webhook Key**
   - You'll see: `https://maker.ifttt.com/use/YOUR_KEY_HERE`
   - Copy the key (looks like: `bX9jK3mN2pQ5rS8tV1wY4z`)

3. **Add to secrets.yaml**
   ```yaml
   ifttt_webhook_key: "your-actual-webhook-key-here"
   ```

### Step 2: Test Your Webhook

Test connection using curl or browser:
```bash
curl -X POST https://maker.ifttt.com/trigger/test/with/key/YOUR_KEY \
  -H "Content-Type: application/json" \
  -d '{"value1":"Hello","value2":"from","value3":"Home Assistant"}'
```

Or visit in browser:
```
https://maker.ifttt.com/trigger/test/with/key/YOUR_KEY
```

You should see: "Congratulations! You've fired the test event"



## 📱 Creating IFTTT Applets

### Applet Types

#### Type 1: Home Assistant → IFTTT (Send Events)

**Example: Send notification when motion detected**

1. In IFTTT:
   - IF: Webhooks → Receive a web request
   - Event Name: `motion_detected`
   - THEN: Notifications → Send notification
   - Message: `{{Value1}} at {{Value2}}`

2. In Home Assistant (already configured):
   ```yaml
   # This automation is in ifttt-webhooks.yaml
   - id: 'ifttt_send_motion'
     alias: "IFTTT: Send Motion Detection"
     trigger:
       - platform: state
         entity_id: binary_sensor.motion_sensor
         to: 'on'
     action:
       - service: ifttt.trigger
         data:
           event: "motion_detected"
           value1: "Motion detected"
           value2: "Front door"
           value3: "{{ now().strftime('%I:%M %p') }}"
   ```

#### Type 2: IFTTT → Home Assistant (Receive Webhooks)

**Example: Mobile button to turn on lights**

1. In IFTTT:
   - IF: Button widget (or Google Assistant, Alexa, etc.)
   - THEN: Webhooks → Make a web request
   - URL: `https://your-domain.com/api/webhook/ifttt_mobile_button`
   - Method: POST
   - Content Type: application/json
   - Body:
     ```json
     {
       "button": "lights_on"
     }
     ```

2. Home Assistant webhook URL format:
   ```
   https://YOUR_HA_URL/api/webhook/ifttt_mobile_button
   ```
     
   Available webhook IDs (already configured):
   - `ifttt_mobile_button` - Mobile button presses
   - `ifttt_notification_action` - Notification actions
   - `ifttt_tasker` - Tasker integration
   - `ifttt_scene` - Scene activation
   - `ifttt_voice` - Voice commands
   - `ifttt_location` - Location triggers



## 🎯 Pre-Configured Automations

### Outgoing (HA → IFTTT)

| Event Name | Trigger | Description |
|------------|---------|-------------|
| `motion_detected` | Motion sensor on | Sends motion alert |
| `battery_low` | Battery < 20% | Low battery warning |
| `temperature_high` | Temp > 80°F | High temperature alert |
| `door_open_alert` | Door open 5+ min | Door left open warning |
| `home_status` | Alarm state change | Security status update |

### Incoming (IFTTT → HA)

| Webhook ID | Purpose | Example Use |
|------------|---------|-------------|
| `ifttt_mobile_button` | Button widget | Quick actions from phone |
| `ifttt_voice` | Voice commands | "Turn on living room lights" |
| `ifttt_location` | Location changes | Auto arm/disarm |
| `ifttt_scene` | Scene activation | Activate movie mode |
| `ifttt_tasker` | Android automation | Tasker profile triggers |



## 🛠️ Usage Examples

### Example 1: Send Custom Event from HA

```yaml
# In your automation
action:
  - service: ifttt.trigger
    data:
      event: "my_custom_event"
      value1: "First value"
      value2: "Second value"
      value3: "Third value"
```

### Example 2: Use the Script

```yaml
# Call the pre-built script
action:
  - service: script.ifttt_send_custom_event
    data:
      event_name: "doorbell_pressed"
      value1: "Front door"
      value2: "{{ now().strftime('%I:%M %p') }}"
      value3: "Motion detected"
```

### Example 3: Emergency Notification

```yaml
action:
  - service: script.ifttt_emergency_notify
    data:
      message: "Smoke alarm triggered in kitchen"
```

### Example 4: Voice Command via IFTTT

Create IFTTT applet:
- IF: Google Assistant → Say phrase "Turn on $"
- THEN: Webhooks → POST to `https://your-ha.com/api/webhook/ifttt_voice`
  ```json
  {
    "command": "turn on {{TextField}}",
    "area": "{{TextField}}"
  }
  ```



## 📊 Available Services

### Main IFTTT Service

```yaml
service: ifttt.trigger
data:
  event: event_name
  value1: "First value"
  value2: "Second value"
  value3: "Third value"
```

### REST Commands

```yaml
# Custom event
service: rest_command.ifttt_trigger_event
data:
  event: "my_event"
  value1: "Hello"
  value2: "World"
  value3: "Test"

# Notification
service: rest_command.ifttt_notify
data:
  title: "Alert"
  message: "Something happened"
  priority: "high"

# Location update
service: rest_command.ifttt_location_update
data:
  location: "Home"
  latitude: "40.7128"
  longitude: "-74.0060"

# Home status
service: rest_command.ifttt_home_status
data:
  status: "Armed"
  details: "Away mode active"
  timestamp: "{{ now().isoformat() }}"
```

### Scripts

```yaml
# Send custom event
service: script.ifttt_send_custom_event
data:
  event_name: "my_event"
  value1: "Value 1"
  value2: "Value 2"
  value3: "Value 3"

# Emergency notification
service: script.ifttt_emergency_notify
data:
  message: "Emergency situation"
```



## 🔐 Security Best Practices

1. **Use HTTPS**: Always use HTTPS for webhook URLs
2. **Secret Webhook IDs**: Use unique, hard-to-guess webhook IDs
3. **Firewall**: Consider IP whitelisting for IFTTT webhooks
4. **Rate Limiting**: Enable rate limiting in HA configuration
5. **Authentication**: IFTTT webhooks require your HA URL but use webhook IDs
   for security

### IFTTT IP Addresses

IFTTT webhooks come from these IP ranges:
```
54.89.24.120
54.89.157.237
54.164.94.166
54.165.154.45
54.209.38.96
54.210.139.167
```



## 🧪 Testing

### Test Outgoing Events (HA → IFTTT)

1. **Developer Tools > Services**
   ```yaml
   service: ifttt.trigger
   data:
     event: "test"
     value1: "Hello"
     value2: "from"
     value3: "Home Assistant"
   ```

2. **Check IFTTT Activity**
   - Go to: https://ifttt.com/activity
   - You should see your test event

### Test Incoming Webhooks (IFTTT → HA)

1. **Using curl**:
   ```bash
   curl -X POST https://your-ha.com/api/webhook/ifttt_mobile_button \
     -H "Content-Type: application/json" \
     -d '{"button":"lights_on"}'
   ```

2. **Check HA Logs**:
   ```yaml
   # Check: Configuration > Logs
   # Look for: "IFTTT: Mobile Button Event"
   ```

3. **Check Input Text**:
   ```yaml
   # Check: Developer Tools > States
   # Entity: input_text.ifttt_last_event
   # Should show: "mobile_button_lights_on"
   ```



## 📱 Popular IFTTT Applet Ideas

### Google Assistant Integration
```
IF: Google Assistant → Say phrase "I'm home"
THEN: Webhooks → POST to ifttt_location webhook
Body: {"location": "home"}
```

### iOS Shortcuts
```
IF: iOS Shortcuts → Run shortcut
THEN: Webhooks → POST to ifttt_scene webhook
Body: {"scene_name": "movie_mode"}
```

### Android Widget Button
```
IF: Android Widget → Button pressed
THEN: Webhooks → POST to ifttt_mobile_button webhook
Body: {"button": "goodnight"}
```

### Location-Based
```
IF: Location → Enter area (Home)
THEN: Webhooks → POST to ifttt_location webhook
Body: {"location": "home", "latitude": "40.7128", "longitude": "-74.0060"}
```

### Email to Action
```
IF: Email → Receive email tagged "#homeassistant"
THEN: Webhooks → POST to ifttt_voice webhook
Body: {"command": "{{Subject}}"}
```

### RSS Feed to Notification
```
IF: RSS Feed → New feed item
THEN: Webhooks → POST to your HA notification webhook
Body: {"title": "{{EntryTitle}}", "message": "{{EntryContent}}"}
```



## 🔧 Configuration Options

### Input Booleans

Control IFTTT features:
```yaml
input_boolean.ifttt_tasker_enabled       # Enable/disable Tasker integration
input_boolean.ifttt_voice_enabled        # Enable/disable voice commands
input_boolean.ifttt_location_enabled     # Enable/disable location tracking
input_boolean.ifttt_notifications_enabled # Enable/disable notifications
```

### Input Select

Mode control:
```yaml
input_select.ifttt_mode
  - enabled   # Fully operational
  - disabled  # All automations stopped
  - test      # Test mode (logged but not executed)
```

### Sensors

Monitor status:
```yaml
sensor.ifttt_integration_status    # Active/Testing/Disabled
sensor.ifttt_last_event_time      # Timestamp of last event
input_text.ifttt_last_event       # Name of last triggered event
```



## ❌ Troubleshooting

### Problem: "Event not received"

**Check:**
1. Webhook key is correct in secrets.yaml
2. Event name matches in HA and IFTTT exactly
3. IFTTT applet is turned ON
4. Check IFTTT activity page for errors

**Solution:**
```bash
# Test with curl
curl -X POST https://maker.ifttt.com/trigger/test/with/key/YOUR_KEY
```

### Problem: "Webhook not triggering HA"

**Check:**
1. Home Assistant is accessible externally (use DuckDNS/Nabu Casa)
2. Webhook URL is correct: `https://your-ha.com/api/webhook/ifttt_mobile_button`
3. HTTPS is used (HTTP won't work with IFTTT)
4. Webhook ID exists in configuration

**Solution:**
```yaml
# Check logs: Configuration > Logs
# Enable debug logging:
logger:
  logs:
    homeassistant.components.webhook: debug
    homeassistant.components.ifttt: debug
```

### Problem: "Webhook returns 404"

**Cause:** Webhook ID doesn't exist in configuration

**Solution:**
```yaml
# Add webhook automation:
automation:
  - id: 'your_webhook_id'
    alias: "Your Webhook"
    trigger:
      - platform: webhook
        webhook_id: ifttt_your_id
    action:
      - service: notify.mobile_app
        data:
          message: "Webhook received!"
```

### Problem: "Events delayed"

**Cause:** IFTTT free tier has delays (up to 1 hour)

**Solution:**
- Upgrade to IFTTT Pro ($5/month) for instant triggers
- Or use direct webhooks without IFTTT as middleman



## 📚 Additional Resources

- **IFTTT Platform**: https://ifttt.com
- **IFTTT Webhooks**: https://ifttt.com/maker_webhooks
- **IFTTT Documentation**: https://help.ifttt.com
- **Home Assistant IFTTT Docs**:
  https://www.home-assistant.io/integrations/ifttt/
- **Webhook Integration**: https://www.home-assistant.io/integrations/webhook/



## ✅ Quick Start Checklist

- [ ] Get IFTTT webhook key
- [ ] Add key to secrets.yaml
- [ ] Test webhook with curl
- [ ] Create first IFTTT applet (HA → IFTTT)
- [ ] Test outgoing event
- [ ] Create webhook applet (IFTTT → HA)
- [ ] Setup external access (DuckDNS/Nabu Casa)
- [ ] Test incoming webhook
- [ ] Enable desired input_booleans
- [ ] Create custom automations
- [ ] Setup mobile widgets
- [ ] Test voice commands
- [ ] Configure location triggers



**Last Updated**: January 31, 2026  
**Integration Version**: 2.0  
**Home Assistant Version**: 2025.12.5
