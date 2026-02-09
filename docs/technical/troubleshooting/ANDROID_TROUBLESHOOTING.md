# 🔧 Android Integration Troubleshooting Guide

## Table of Contents
- [Connection Issues](#connection-issues)
- [Location & Presence Detection](#location--presence-detection)
- [Notification Problems](#notification-problems)
- [Battery Drain Issues](#battery-drain-issues)
- [Widget & Quick Settings](#widget--quick-settings)
- [Automation Issues](#automation-issues)
- [Tailscale VPN Problems](#tailscale-vpn-problems)
- [Sensor Issues](#sensor-issues)
- [Performance Problems](#performance-problems)
- [Advanced Troubleshooting](#advanced-troubleshooting)

---

## Connection Issues

### ❌ Cannot Connect to Home Assistant

**Symptoms**: App shows "Connection error" or "Cannot reach server"

**Solutions**:

1. **Check Network Connectivity**
   ```
   - Verify WiFi is connected
   - Try opening http://192.168.1.134:8123 in a browser
   - Ping Home Assistant: Settings > Network > Ping 192.168.1.134
   ```

2. **Verify Home Assistant URL**
   ```
   - Local URL: http://192.168.1.134:8123 (not https)
   - External URL: If using Nabu Casa or DuckDNS
   - No trailing slash: ✅ http://192.168.1.134:8123 ❌ http://192.168.1.134:8123/
   ```

3. **Check Home Assistant Status**
   ```bash
   # SSH into Home Assistant server
   ha core info
   # Should show "running"
   ```

4. **Firewall Issues**
   ```
   - Check router firewall
   - Ensure port 8123 is not blocked
   - Temporarily disable firewall to test
   ```

5. **Reset App Connection**
   ```
   1. Open HA Companion app
   2. App Configuration > Reset
   3. Reconnect to server
   4. Re-authorize
   ```

### ❌ Connection Works on WiFi but Not Mobile Data

**Symptoms**: App works at home, fails when away

**Solutions**:

1. **Enable External Access**
   - Option 1: Use Tailscale VPN (recommended)
   - Option 2: Configure Nabu Casa Cloud
   - Option 3: Setup port forwarding (less secure)

2. **Verify External URL**
   ```
   HA Companion App > App Configuration > Connection
   - Internal URL: http://192.168.1.134:8123
   - External URL: http://your-tailscale-ip:8123
   ```

3. **Test Tailscale Connection**
   ```
   1. Disconnect from WiFi
   2. Ensure Tailscale is connected
   3. Open Tailscale app and verify IP
   4. Try accessing HA via Tailscale IP
   ```

### ❌ Connection Drops Frequently

**Symptoms**: App disconnects randomly

**Solutions**:

1. **Disable Battery Optimization**
   ```
   Settings > Apps > Home Assistant > Battery
   Select "Unrestricted" or "Don't optimize"
   ```

2. **Enable Background Data**
   ```
   Settings > Apps > Home Assistant > Mobile data & WiFi
   Enable "Background data"
   Enable "Unrestricted data usage"
   ```

3. **Check WiFi Sleep Settings**
   ```
   Settings > WiFi > Advanced
   Set "Keep WiFi on during sleep" to "Always"
   ```

---

## Location & Presence Detection

### ❌ Location Not Updating

**Symptoms**: Device tracker shows old location or "unavailable"

**Solutions**:

1. **Enable Location Permissions**
   ```
   Settings > Apps > Home Assistant > Permissions > Location
   Select "Allow all the time" (not "While using app")
   ```

2. **Disable Battery Optimization for Location**
   ```
   Settings > Location > App permissions > Home Assistant
   Set to "Allow all the time"
   Battery > Unrestricted
   ```

3. **Enable High Accuracy Mode**
   ```
   Settings > Location > Mode
   Select "High accuracy" (GPS, WiFi, Bluetooth, mobile networks)
   ```

4. **Force Location Update**
   ```
   Open HA Companion app
   App Configuration > Sensors
   Tap "Location" sensor
   Tap "Update Now"
   ```

5. **Check Location Sensor Settings**
   ```
   HA Companion App > App Configuration > Sensors
   Ensure these are enabled:
   ✓ Location
   ✓ Geocoded Location
   ✓ Zone
   ```

### ❌ Geofencing Not Triggering

**Symptoms**: Automations don't trigger when arriving/leaving

**Solutions**:

1. **Verify Zone Configuration**
   ```yaml
   # In Home Assistant
   Configuration > Areas & Zones
   - Check latitude/longitude are correct
   - Verify radius is appropriate (100m minimum)
   - Ensure "Passive" is OFF for active zones
   ```

2. **Check Automation Conditions**
   ```yaml
   # Example automation should have:
   trigger:
     - platform: state
       entity_id: device_tracker.mobile_app_your_device
       to: 'home'  # or 'not_home'
   ```

3. **Increase Zone Radius**
   ```
   If false negatives, increase zone radius to 150-200m
   GPS accuracy varies, larger radius helps
   ```

4. **Add Delay to Prevent False Triggers**
   ```yaml
   trigger:
     - platform: state
       entity_id: device_tracker.mobile_app_your_device
       to: 'not_home'
       for:
         minutes: 3  # Wait 3 minutes before triggering
   ```

### ❌ False Location Triggers

**Symptoms**: Automation triggers when you haven't left home

**Solutions**:

1. **Add Confirmation Delay**
   ```yaml
   condition:
     - condition: state
       entity_id: device_tracker.mobile_app_your_device
       state: 'not_home'
       for:
         minutes: 5
   ```

2. **Use Multiple Presence Indicators**
   ```yaml
   condition:
     - condition: and
       conditions:
         - condition: state
           entity_id: device_tracker.mobile_app_your_device
           state: 'not_home'
         - condition: state
           entity_id: sensor.mobile_app_your_device_wifi_connection
           state: 'not_home_wifi'
   ```

3. **Adjust GPS Accuracy Threshold**
   ```
   HA Companion App > App Configuration > Sensors > Location
   Increase "Minimum accuracy" to filter bad GPS readings
   ```

---

## Notification Problems

### ❌ Not Receiving Notifications

**Symptoms**: No notifications appear on Android

**Solutions**:

1. **Enable Notifications**
   ```
   Settings > Apps > Home Assistant > Notifications
   Ensure "Show notifications" is ON
   Check all notification channels are enabled
   ```

2. **Check Do Not Disturb**
   ```
   Settings > Sound > Do Not Disturb
   Either disable DND or add Home Assistant to exceptions
   ```

3. **Battery Optimization (Again)**
   ```
   This is the #1 cause of notification issues
   Settings > Apps > Home Assistant > Battery
   Set to "Unrestricted"
   ```

4. **Test Notification**
   ```yaml
   # In Home Assistant Developer Tools > Services
   service: notify.mobile_app_your_device
   data:
     message: "Test notification"
     title: "Test"
   ```

5. **Check Notification Channels**
   ```
   HA Companion App > App Configuration > Notifications
   Ensure channels are configured and enabled
   ```

### ❌ Notifications Delayed

**Symptoms**: Notifications arrive minutes/hours late

**Solutions**:

1. **Use High Priority**
   ```yaml
   data:
     priority: high
     ttl: 0  # No expiration
   ```

2. **Check Network**
   ```
   - Poor mobile signal delays push notifications
   - WiFi connection issues
   - Try switching between WiFi and mobile data
   ```

3. **Clear App Cache**
   ```
   Settings > Apps > Home Assistant > Storage
   Clear cache (NOT clear data)
   ```

4. **Reinstall Google Play Services**
   ```
   Settings > Apps > Google Play Services
   Uninstall updates > Reinstall
   ```

### ❌ Actionable Notifications Not Working

**Symptoms**: Buttons in notifications don't respond

**Solutions**:

1. **Create Event Handler Automation**
   ```yaml
   automation:
     - alias: "Handle Notification Action"
       trigger:
         - platform: event
           event_type: mobile_app_notification_action
           event_data:
             action: "YOUR_ACTION_NAME"
       action:
         - service: light.turn_on  # Your action here
   ```

2. **Check Action Names**
   ```yaml
   # Action names must match exactly (case-sensitive)
   Notification: action: "LOCK_DOOR"
   Automation: action: "LOCK_DOOR"  # Must match
   ```

3. **Use Unique Action IDs**
   ```yaml
   actions:
     - action: "LOCK_FRONT_DOOR"  # Unique
       title: "Lock Door"
   ```

---

## Battery Drain Issues

### ❌ Home Assistant App Draining Battery

**Symptoms**: Excessive battery usage by HA app

**Solutions**:

1. **Reduce Location Update Frequency**
   ```
   HA Companion App > App Configuration > Sensors > Location
   Increase update interval:
   - Normal: 60 seconds
   - Battery saver: 300 seconds (5 minutes)
   ```

2. **Disable Unnecessary Sensors**
   ```
   HA Companion App > App Configuration > Sensors
   Disable sensors you don't need:
   - Light sensor
   - Pressure sensor
   - Proximity sensor
   - Step sensors
   ```

3. **Reduce Widget Updates**
   ```
   Remove dashboard widgets (they update frequently)
   Use button widgets instead (update on demand)
   ```

4. **Use WiFi-Based Presence Detection**
   ```yaml
   # More battery-efficient than GPS
   trigger:
     - platform: state
       entity_id: sensor.mobile_app_your_device_wifi_connection
       to: 'Your_SSID'
   ```

5. **Check Background App Refresh**
   ```
   Settings > Apps > Home Assistant > Battery
   If battery drain is critical, use "Optimized"
   But this may delay notifications
   ```

### ❌ Location Services Draining Battery

**Solutions**:

1. **Use Zone-Based Updates**
   ```
   HA Companion App > App Configuration > Sensors > Location
   Enable "Zone-based tracking"
   Updates only near zone boundaries
   ```

2. **Increase Accuracy Threshold**
   ```
   Higher threshold = fewer updates = less battery
   Set "Minimum accuracy" to 100m
   ```

3. **Disable "Always" Location**
   ```
   If battery is critical:
   Settings > Apps > Home Assistant > Permissions > Location
   Set to "While using app" (but presence detection won't work)
   ```

---

## Widget & Quick Settings

### ❌ Widgets Not Updating

**Symptoms**: Widget shows old/stale data

**Solutions**:

1. **Check Battery Optimization**
   ```
   This is usually the culprit
   Settings > Apps > Home Assistant > Battery > Unrestricted
   ```

2. **Reduce Update Interval**
   ```
   Long-press widget > Widget settings
   Reduce refresh interval if too high
   ```

3. **Remove and Re-add Widget**
   ```
   1. Long-press widget
   2. Drag to "Remove"
   3. Re-add widget from widget menu
   4. Reconfigure
   ```

4. **Clear App Cache**
   ```
   Settings > Apps > Home Assistant > Storage > Clear cache
   ```

### ❌ Quick Settings Tile Not Working

**Symptoms**: Tile doesn't respond to taps

**Solutions**:

1. **Reconfigure Tile**
   ```
   HA Companion App > App Configuration > Manage Tiles
   Reconfigure Template Tile 1 or 2
   Verify service call is correct
   ```

2. **Check Entity ID**
   ```
   Ensure entity_id in tile config exists in HA
   Developer Tools > States > Search for entity
   ```

3. **Verify Permissions**
   ```
   Settings > Apps > Home Assistant > Permissions
   Ensure all required permissions are granted
   ```

---

## Automation Issues

### ❌ Automation Not Triggering

**Symptoms**: Expected automation doesn't run

**Solutions**:

1. **Check Automation State**
   ```
   Home Assistant > Configuration > Automations
   Ensure automation is enabled (toggle switch)
   ```

2. **Verify Trigger**
   ```yaml
   # Check entity ID is correct
   trigger:
     - platform: state
       entity_id: device_tracker.mobile_app_your_device  # Correct?
       to: 'home'
   ```

3. **Check Conditions**
   ```yaml
   # Conditions may be blocking automation
   # Temporarily remove conditions to test
   ```

4. **Enable Automation Tracing**
   ```
   Configuration > Automations > [Your Automation] > Traces
   Shows why automation didn't trigger
   ```

5. **Check Logs**
   ```
   Configuration > Logs
   Filter by "automation"
   Look for errors
   ```

### ❌ Automation Triggers Too Often

**Symptoms**: Automation runs repeatedly

**Solutions**:

1. **Add Time Constraint**
   ```yaml
   mode: single  # Prevent concurrent runs
   ```

2. **Add Cooldown**
   ```yaml
   condition:
     - condition: template
       value_template: >
         {{ (as_timestamp(now()) - as_timestamp(state_attr('automation.your_automation', 'last_triggered'))) > 300 }}
   ```

3. **Add State Duration**
   ```yaml
   trigger:
     - platform: state
       entity_id: device_tracker.mobile_app_your_device
       to: 'home'
       for:
         minutes: 2  # Must be in state for 2 minutes
   ```

---

## Tailscale VPN Problems

### ❌ Tailscale Not Connecting

**Symptoms**: Tailscale shows "Not connected"

**Solutions**:

1. **Check Account**
   ```
   Ensure you're signed in
   Tailscale app > Account > Sign out > Sign in
   ```

2. **Grant VPN Permission**
   ```
   When prompted, tap "OK" to allow VPN
   If missed: Tailscale app > Connect > Grant permission
   ```

3. **Check Network Settings**
   ```
   Settings > Network & Internet > VPN
   Ensure Tailscale VPN is listed and active
   ```

4. **Disable Battery Optimization**
   ```
   Settings > Apps > Tailscale > Battery > Unrestricted
   ```

### ❌ Cannot Access HA via Tailscale

**Symptoms**: Tailscale connected but can't reach HA

**Solutions**:

1. **Verify Tailscale IP**
   ```
   Open Tailscale app
   Note your HA server's Tailscale IP (100.x.x.x)
   ```

2. **Test Connection**
   ```
   Open browser
   Try: http://100.x.x.x:8123 (use actual Tailscale IP)
   ```

3. **Check Tailscale on HA Server**
   ```bash
   # SSH into HA server
   tailscale status
   # Should show "connected"
   ```

4. **Update External URL in HA App**
   ```
   HA Companion App > App Configuration > Connection
   External URL: http://<ha-tailscale-ip>:8123
   ```

---

## Sensor Issues

### ❌ Sensors Not Updating

**Symptoms**: Sensor values are stale or unavailable

**Solutions**:

1. **Enable Sensor**
   ```
   HA Companion App > App Configuration > Sensors
   Find sensor and toggle ON
   ```

2. **Force Update**
   ```
   HA Companion App > App Configuration > Sensors
   Tap sensor > "Update Now"
   ```

3. **Check Permissions**
   ```
   Settings > Apps > Home Assistant > Permissions
   Grant required permissions for sensor type
   ```

4. **Battery Optimization (Yet Again)**
   ```
   Sensors won't update in background if app is optimized
   Settings > Battery > Battery optimization > Home Assistant > Don't optimize
   ```

### ❌ Activity Sensor Not Working

**Symptoms**: Activity shows "unknown" or doesn't update

**Solutions**:

1. **Enable Physical Activity Permission**
   ```
   Settings > Apps > Home Assistant > Permissions
   Enable "Physical activity" or "Body sensors"
   ```

2. **Enable Google Fit or Health Connect**
   ```
   Activity detection requires Google Fit (older) or Health Connect (newer)
   Install and enable
   ```

---

## Performance Problems

### ❌ App is Slow or Laggy

**Solutions**:

1. **Clear Cache**
   ```
   Settings > Apps > Home Assistant > Storage > Clear cache
   ```

2. **Reduce Dashboard Complexity**
   ```
   Use simpler dashboards with fewer cards
   Avoid heavy custom cards
   ```

3. **Update App**
   ```
   Play Store > Home Assistant > Update
   ```

4. **Check Network Speed**
   ```
   Slow WiFi/mobile connection = slow app
   Test: speedtest.net
   ```

### ❌ App Crashes

**Solutions**:

1. **Clear Cache and Data**
   ```
   Settings > Apps > Home Assistant > Storage
   Clear cache (try this first)
   If still crashing, clear data (will need to reconfigure)
   ```

2. **Update Android System WebView**
   ```
   Play Store > Android System WebView > Update
   ```

3. **Reinstall App**
   ```
   1. Export settings if possible
   2. Uninstall app
   3. Reinstall from Play Store
   4. Reconfigure
   ```

---

## Advanced Troubleshooting

### Debug Logs

1. **Enable Debug Logging in HA App**
   ```
   App Configuration > Debugging
   Enable "Debug logs"
   Reproduce issue
   Share logs via "Share logs" button
   ```

2. **Check Home Assistant Logs**
   ```
   Configuration > Logs
   Look for errors related to mobile_app
   ```

3. **Check Android System Logs**
   ```
   Install "LogCat Reader" app
   Filter by "homeassistant"
   Look for crashes or errors
   ```

### Network Debugging

1. **Test Local Network**
   ```bash
   # From Android terminal (Termux)
   ping 192.168.1.134
   curl http://192.168.1.134:8123
   ```

2. **Test External Network**
   ```bash
   # Disconnect WiFi, use mobile data
   curl http://your-external-url:8123
   ```

3. **Check Firewall**
   ```
   Temporarily disable router firewall
   If it works, add HA to firewall exceptions
   ```

### Factory Reset (Last Resort)

1. **Backup Current Config**
   ```
   HA Companion App > App Configuration
   Screenshot all settings
   Note all sensor configurations
   ```

2. **Uninstall App**
   ```
   Settings > Apps > Home Assistant > Uninstall
   ```

3. **Clear All Data**
   ```
   Settings > Storage > Free up space
   Clear cache and data for Home Assistant
   ```

4. **Reinstall and Reconfigure**
   ```
   Play Store > Home Assistant > Install
   Follow setup guide from scratch
   ```

---

## Common Error Messages

### "Server version not supported"
- **Cause**: HA app requires newer Home Assistant version
- **Fix**: Update Home Assistant to latest version

### "Authentication failed"
- **Cause**: Invalid credentials or token expired
- **Fix**: Logout and login again, create new long-lived token

### "Cannot connect to internal URL"
- **Cause**: Wrong IP or HA not running
- **Fix**: Verify IP is correct, check HA is running

### "SSL handshake failed"
- **Cause**: Self-signed certificate issues
- **Fix**: Use http:// instead of https:// for local access

### "Request timeout"
- **Cause**: Network too slow or HA overloaded
- **Fix**: Check network connection, restart HA

---

## Getting More Help

### Community Resources
- **Home Assistant Community Forum**: https://community.home-assistant.io/
- **Home Assistant Discord**: https://discord.gg/home-assistant
- **Reddit**: r/homeassistant

### Official Documentation
- **HA Companion Docs**: https://companion.home-assistant.io/
- **Troubleshooting Guide**: https://companion.home-assistant.io/docs/troubleshooting/

### Report Bugs
- **GitHub Issues**: https://github.com/home-assistant/android/issues
- Include debug logs and steps to reproduce

---

## Prevention Tips

✅ **Always do this:**
- Disable battery optimization for Home Assistant
- Keep app updated
- Use stable WiFi connection
- Regular HA backups
- Test automations after changes

❌ **Avoid doing this:**
- Enabling aggressive battery saver
- Using task killers or app cleaners
- Clearing app data without backup
- Too many widgets (battery drain)
- Untested automation changes

---

**Remember**: 80% of Android integration issues are caused by battery optimization. Check that first! 🔋
