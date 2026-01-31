# Third-Party Service Integrations Setup Guide
# Generated: January 31, 2026
# Home Assistant Unified Integration

This document provides setup instructions for all third-party service integrations added to your Home Assistant configuration.

## 📋 Table of Contents

1. [Amazon Alexa](#amazon-alexa)
2. [Google Home / Assistant](#google-home--assistant)
3. [Samsung SmartThings](#samsung-smartthings)
4. [Apple HomeKit / iOS](#apple-homekit--ios)
5. [Android (Tasker & Join)](#android-tasker--join)
6. [Required Secrets](#required-secrets)
7. [Testing & Verification](#testing--verification)

---

## 🔊 Amazon Alexa

### Integration Files
- **Configuration**: `integrations/alexa-integration.yaml`
- **Features**: Alexa Media Player, Smart Home Skill, Flash Briefings, TTS notifications

### Setup Steps

1. **Install Alexa Media Player Custom Component**
   ```bash
   # Via HACS (recommended)
   1. Open HACS in Home Assistant
   2. Go to Integrations
   3. Search for "Alexa Media Player"
   4. Click Install
   5. Restart Home Assistant
   ```

2. **Configure Alexa Media Player**
   - Add to `secrets.yaml`:
     ```yaml
     alexa_email: "your-amazon-email@example.com"
     alexa_password: "your-amazon-password"
     ```
   - Restart Home Assistant
   - Complete 2FA verification when prompted

3. **Setup Smart Home Skill**
   - Go to Amazon Alexa Developer Console: https://developer.amazon.com/alexa/console/ask
   - Create new Smart Home Skill
   - Get Client ID and Secret, add to `secrets.yaml`:
     ```yaml
     alexa_client_id: "amzn1.application-oa2-client.xxxxx"
     alexa_client_secret: "xxxxxxxxxxxxxxxxxxxxx"
     ```
   - Link skill to Home Assistant via OAuth

4. **Discover Devices**
   - Open Alexa app on phone
   - Go to Devices > Discover
   - Say: "Alexa, discover devices"

### Available Scripts
- `script.alexa_welcome_home` - Welcome home announcement
- `script.alexa_goodnight` - Goodnight routine with sleep sounds

### Notification Services
- `notify.alexa_media` - Single device notification
- `notify.alexa_announce_all` - Announce to all Alexa devices

---

## 🏠 Google Home / Assistant

### Integration Files
- **Configuration**: `integrations/google-home-integration.yaml`
- **Features**: Google Assistant, Chromecast/Cast, Calendar, TTS, Device Tracking

### Setup Steps

1. **Create Google Cloud Project**
   - Go to: https://console.cloud.google.com
   - Create new project: "Home Assistant"
   - Enable APIs:
     - Google Assistant API
     - HomeGraph API
     - Google Calendar API

2. **Setup Service Account**
   - In Google Cloud Console > IAM & Admin > Service Accounts
   - Create service account
   - Download JSON key file
   - Save as: `config/google_service_account.json`

3. **Configure Google Assistant Action**
   - Go to: https://console.actions.google.com
   - Create new project linked to Cloud project
   - Setup Smart Home action
   - Add fulfillment URL: `https://your-domain/api/google_assistant`
   - Add to `secrets.yaml`:
     ```yaml
     google_assistant_project_id: "your-project-id"
     ```

4. **Setup Google Calendar**
   - Enable Google Calendar API in Cloud Console
   - Create OAuth credentials
   - Add to `secrets.yaml`:
     ```yaml
     google_calendar_client_id: "xxxxx.apps.googleusercontent.com"
     google_calendar_client_secret: "xxxxxxxxxxxxxxxxx"
     google_calendar_personal_id: "your-email@gmail.com"
     ```

5. **Chromecast Discovery**
   - Add device IPs to `secrets.yaml`:
     ```yaml
     chromecast_living_room_ip: "192.168.1.210"
     google_home_kitchen_ip: "192.168.1.212"
     ```
   - Or enable auto-discovery (mDNS)

6. **Link Google Home App**
   - Open Google Home app
   - Add device > Works with Google > Search "Home Assistant"
   - Link account and authorize

### Available Scripts
- `script.google_home_welcome` - Welcome home announcement
- `script.google_home_bedtime` - Bedtime announcement

### Notification Services
- `notify.google_home_tts` - Kitchen Google Home TTS
- `notify.google_nest_hub_tts` - Nest Hub TTS
- `notify.google_home_announce_all` - Announce to all devices

---

## 📱 Samsung SmartThings

### Integration Files
- **Configuration**: `integrations/smartthings-integration.yaml`
- **Features**: SmartThings devices, Samsung TVs, Webhook automation

### Setup Steps

1. **Get SmartThings Personal Access Token**
   - Go to: https://account.smartthings.com/tokens
   - Click "Generate new token"
   - Enable all permissions
   - Copy token, add to `secrets.yaml`:
     ```yaml
     smartthings_access_token: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
     ```

2. **Setup Webhook**
   - In Home Assistant, go to Configuration > Automations
   - Create webhook: `smartthings_events`
   - Add webhook URL to `secrets.yaml`:
     ```yaml
     smartthings_webhook_url: "https://your-domain/api/webhook/smartthings_events"
     ```

3. **Configure SmartThings Hub**
   - In SmartThings app, go to Hub settings
   - Enable "Allow External Control"
   - Add Home Assistant as trusted device

4. **Setup Samsung TV**
   - Enable "Device Connect Manager" on Samsung TV
   - Get TV IP address
   - Add to `secrets.yaml`:
     ```yaml
     samsung_tv_living_room_ip: "192.168.1.220"
     samsung_tv_mac: "AA:BB:CC:DD:EE:FF"
     ```
   - First connection will show pairing code on TV

5. **Discover Devices**
   - Restart Home Assistant
   - Go to Configuration > Integrations
   - SmartThings devices should auto-discover

### Available Scripts
- `script.smartthings_all_lights_on` - Turn on all SmartThings lights
- `script.smartthings_all_lights_off` - Turn off all lights
- `script.smartthings_lock_all` - Lock all SmartThings locks

---

## 🍎 Apple HomeKit / iOS

### Integration Files
- **Configuration**: `integrations/apple-homekit-integration.yaml`
- **Features**: HomeKit Bridge, iCloud tracking, iOS app, Apple Watch, Siri Shortcuts

### Setup Steps

1. **Enable HomeKit Bridge**
   - Configuration already in `apple-homekit-integration.yaml`
   - After restart, check Home Assistant logs for pairing code
   - Open Apple Home app on iOS device
   - Add Accessory > More Options > Enter code manually
   - Enter 8-digit pairing code from logs

2. **Setup iCloud Integration**
   - Add to `secrets.yaml`:
     ```yaml
     icloud_username: "your-apple-id@icloud.com"
     icloud_password: "your-app-specific-password"
     ```
   - Generate app-specific password:
     1. Go to: https://appleid.apple.com
     2. Sign in > Security > App-Specific Passwords
     3. Generate new password
     4. Use this instead of main password

3. **Setup iOS Mobile App**
   - Install Home Assistant Companion from App Store
   - Open app, sign in to your Home Assistant instance
   - Grant location permissions for device tracking
   - Enable notifications

4. **Configure Apple Watch**
   - Install Home Assistant Watch app from App Store
   - Open on watch, sign in
   - Add complications for quick access

5. **Setup Siri Shortcuts**
   - Scripts are already configured:
     - `script.siri_good_morning`
     - `script.siri_goodnight`
     - `script.siri_im_home`
     - `script.siri_leaving_home`
   - In iOS Shortcuts app:
     1. Create New Shortcut
     2. Add "Call Home Assistant Script"
     3. Select script name
     4. Add to Siri: "Hey Siri, [trigger phrase]"

6. **Apple TV / HomePod**
   - Add device IPs to `secrets.yaml`:
     ```yaml
     apple_tv_living_room_ip: "192.168.1.230"
     homepod_living_room_ip: "192.168.1.232"
     ```
   - Pairing credentials will be requested on first connect

### Notification Services
- `notify.mobile_app_iphone` - iOS device notification
- `notify.mobile_app_ipad` - iPad notification
- `notify.ios_critical` - Critical alert (bypasses DND)

---

## 🤖 Android (Tasker & Join)

### Integration Files
- **Tasker**: `integrations/tasker-profiles.yaml` ✅ Already configured
- **Join**: `integrations/join-integration.yaml` ✅ Already configured

### Tasker Setup

Already configured with input booleans:
- `input_boolean.tasker_profile_active`
- `input_boolean.tasker_geofencing_enabled`
- `input_boolean.tasker_night_mode`
- `input_boolean.tasker_work_mode`

### Join Setup

1. **Get Join API Key**
   - Install Join app from Play Store
   - Open Join settings > Join API
   - Copy API key
   - In Home Assistant:
     1. Go to Configuration > Helpers
     2. Find "Join API Key" input text
     3. Enter your API key

2. **Configure Target Devices**
   - In Join app, note device names
   - Update `input_select.join_target_device` options if needed

### Available Services
- `rest_command.join_send_notification` - Send notification to Join device
- `rest_command.join_execute_command` - Execute Tasker command via Join

---

## 🔐 Required Secrets

Create or update `config/secrets.yaml` with all credentials. Reference template at: `config/secrets.yaml.template`

### Minimum Required for Each Service:

**Alexa:**
```yaml
alexa_email: "your-email@example.com"
alexa_password: "your-password"
```

**Google:**
```yaml
google_assistant_project_id: "your-project-id"
```

**SmartThings:**
```yaml
smartthings_access_token: "your-token"
```

**Apple:**
```yaml
icloud_username: "your-apple-id@icloud.com"
icloud_password: "app-specific-password"
```

---

## ✅ Testing & Verification

### After Configuration:

1. **Check Configuration**
   ```bash
   # In Home Assistant UI:
   Developer Tools > YAML > Check Configuration
   ```

2. **Restart Home Assistant**
   ```bash
   Configuration > Server Controls > Restart
   ```

3. **Verify Integrations Loaded**
   ```bash
   # Check logs for errors:
   Configuration > Logs
   
   # Look for:
   # - "Alexa Media Player initialized"
   # - "Google Assistant setup completed"
   # - "SmartThings connected"
   # - "HomeKit bridge started"
   ```

4. **Test Voice Assistants**
   - **Alexa**: "Alexa, turn on living room lights"
   - **Google**: "Hey Google, set temperature to 72"
   - **Siri**: "Hey Siri, I'm home"

5. **Test Notifications**
   ```yaml
   # Developer Tools > Services
   # Test each notify service:
   service: notify.alexa_media
   data:
     message: "Test notification from Home Assistant"
     target: media_player.alexa_living_room
   ```

### Common Issues:

**Alexa 2FA Loop**
- Clear browser cache, try incognito
- Use different browser
- Check Amazon account security settings

**Google Assistant "Couldn't update device"**
- Verify HomeGraph API is enabled
- Check service account permissions
- Unlink and relink account in Google Home app

**SmartThings devices not appearing**
- Verify Personal Access Token has all permissions
- Check SmartThings hub is online
- Force refresh: Developer Tools > Services > `homeassistant.reload_config_entry`

**HomeKit "Unable to Add Accessory"**
- Verify Home Assistant is on same network as iOS device
- Check firewall isn't blocking port 51827
- Try resetting HomeKit: delete integration, restart, re-add

---

## 📚 Additional Resources

- **Alexa Media Player**: https://github.com/custom-components/alexa_media_player
- **Google Assistant**: https://www.home-assistant.io/integrations/google_assistant/
- **SmartThings**: https://www.home-assistant.io/integrations/smartthings/
- **HomeKit**: https://www.home-assistant.io/integrations/homekit/
- **iOS Companion**: https://companion.home-assistant.io/

---

## 🎯 Quick Start Checklist

- [ ] Copy `secrets.yaml.template` to `secrets.yaml`
- [ ] Fill in all required credentials
- [ ] Check YAML configuration validity
- [ ] Restart Home Assistant
- [ ] Check logs for errors
- [ ] Test Alexa device discovery
- [ ] Link Google Assistant account
- [ ] Setup SmartThings Personal Access Token
- [ ] Pair HomeKit bridge with iOS
- [ ] Configure Join API key
- [ ] Test voice commands
- [ ] Test notifications
- [ ] Setup Siri shortcuts
- [ ] Configure automations

---

**Last Updated**: January 31, 2026  
**Integration Version**: 1.0.0  
**Home Assistant Version**: 2025.12.5
