# Android Device Setup Guide

## Prerequisites

- Android device running Android 8.0 (Oreo) or higher
- Google Play Store access or F-Droid for open-source alternatives
- Network connectivity (WiFi or mobile data)
- Access to your home network (initially)

## Required Applications

### 1. Home Assistant Companion App

**Installation:**
- Download from [Google Play Store](https://play.google.com/store/apps/details?id=io.homeassistant.companion.android)
- Or from [F-Droid](https://f-droid.org/packages/io.homeassistant.companion.android.minimal/)

**Configuration:**
1. Open the app
2. Tap "Add Server"
3. Enter Home Assistant URL: `http://192.168.1.134:8123`
4. Log in with your Home Assistant credentials
5. Grant necessary permissions:
   - Location (for presence detection)
   - Notifications (for alerts)
   - Battery optimization exemption
   - Background location (optional, for advanced automation)

**Sensor Configuration:**
- Enable device sensors in app settings
- Configure update intervals
- Set up zone detection

### 2. Tailscale VPN Client

**Installation:**
- Download from [Google Play Store](https://play.google.com/store/apps/details?id=com.tailscale.ipn)

**Configuration:**
1. Open Tailscale app
2. Sign in with your Tailscale account
3. Connect to your Tailscale network
4. Verify connection to home network
5. Test access to Home Assistant via Tailscale IP

**Usage:**
- Enable "Always-on VPN" for continuous access
- Use split tunneling if needed
- Configure exit nodes for routing

### 3. MQTT Client (MQTT Dash or IoT MQTT Panel)

**Installation:**
- MQTT Dash: [Google Play Store](https://play.google.com/store/apps/details?id=net.routix.mqttdash)
- IoT MQTT Panel: [Google Play Store](https://play.google.com/store/apps/details?id=snr.lab.iotmqttpanel.prod)

**Configuration:**
1. Open MQTT client app
2. Add new connection:
   - **Broker**: 192.168.1.134
   - **Port**: 1883
   - **Username**: [Your MQTT username]
   - **Password**: [Your MQTT password]
   - **Client ID**: android-[device-name]
3. Test connection
4. Subscribe to topics:
   - `homeassistant/#` (all Home Assistant topics)
   - `zigbee2mqtt/#` (Zigbee device topics)
   - Custom automation topics

**Dashboard Setup:**
- Create tiles for frequently controlled devices
- Set up publish buttons for commands
- Configure widgets for monitoring

### 4. Bitwarden Password Manager

**Installation:**
- Download from [Google Play Store](https://play.google.com/store/apps/details?id=com.x8bit.bitwarden)

**Configuration:**
1. Open Bitwarden app
2. Sign in or create account
3. If self-hosted, enter server URL
4. Enable biometric unlock
5. Store credentials:
   - Home Assistant login
   - MQTT credentials
   - API tokens
   - WiFi passwords

**Auto-fill Setup:**
- Enable Android auto-fill service
- Configure app-specific passwords
- Set up emergency access

## Network Configuration

### Local Network Access

When on your home network (192.168.1.0/24):
- Direct access to all services
- No VPN required
- Optimal performance

**URLs:**
- Home Assistant: `http://192.168.1.134:8123`
- MCP Hub: `http://192.168.1.134:3000`
- AI Automation: `http://192.168.1.134:5000`

### Remote Access via Tailscale

When away from home:
1. Ensure Tailscale VPN is connected
2. Access services via Tailscale IPs or local IPs
3. All traffic encrypted through VPN tunnel

## Home Assistant App Features

### Sensor Data
The Android app provides these sensors to Home Assistant:
- Battery level and charging state
- Location (GPS)
- WiFi connection
- Bluetooth devices nearby
- Step counter
- Light sensor
- Pressure sensor
- Proximity sensor
- Do Not Disturb state
- Interactive mode
- Power save mode

### Actionable Notifications
Set up notifications with action buttons:
```yaml
# Example Home Assistant automation
automation:
  - alias: "Actionable Notification Example"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: 'on'
    action:
      - service: notify.mobile_app_<device_name>
        data:
          message: "Front door opened"
          data:
            actions:
              - action: "LOCK_DOOR"
                title: "Lock Door"
              - action: "VIEW_CAMERA"
                title: "View Camera"
```

### Widgets
Add Home Assistant widgets to your home screen:
- Entity state widgets
- Script/automation triggers
- Scene activation
- Custom widgets

## Advanced Configuration

### WebView Setup
Access full Home Assistant dashboard in app:
1. Open Home Assistant app
2. Navigate to Settings → Companion App
3. Enable WebView debugging (for troubleshooting)
4. Configure custom dashboard URL

### Notification Channels
Configure notification categories:
- Critical alerts
- Information
- Device status
- Automation notifications

### Background Updates
Optimize battery vs. responsiveness:
1. Go to app settings
2. Configure sensor update frequencies
3. Enable background location if needed
4. Set up work profile if using for work/home separation

### Shortcuts
Create Android shortcuts for common actions:
1. Long-press Home Assistant app icon
2. Drag shortcuts to home screen:
   - Toggle lights
   - Activate scenes
   - Run scripts

## Troubleshooting

### Connection Issues
```bash
# Test from Android Terminal Emulator or via PC
ping 192.168.1.134
curl http://192.168.1.134:8123/api/
```

### Home Assistant Not Responding
1. Check WiFi/VPN connection
2. Verify Home Assistant is running
3. Check firewall rules
4. Review app permissions

### MQTT Connection Failed
1. Verify MQTT broker is running
2. Check credentials
3. Test with MQTT client on PC
4. Review MQTT broker logs

### Sensor Data Not Updating
1. Check app battery optimization settings
2. Verify background location permission
3. Review sensor update intervals
4. Check Home Assistant logs

### VPN Not Connecting
1. Verify Tailscale account status
2. Check device authorization
3. Review network connectivity
4. Check Tailscale logs

## Security Best Practices

1. **Enable Authentication**
   - Use strong passwords
   - Enable 2FA where available
   - Use Bitwarden for password management

2. **Limit Permissions**
   - Only grant necessary app permissions
   - Review permissions regularly
   - Disable unused sensors

3. **Use VPN for Remote Access**
   - Never expose Home Assistant directly to internet
   - Always use Tailscale VPN
   - Consider exit nodes for additional security

4. **Keep Apps Updated**
   - Enable automatic updates
   - Review changelogs
   - Test updates on non-critical devices first

5. **Device Security**
   - Enable device encryption
   - Use screen lock
   - Enable remote wipe capability

## Integration Testing

Use the test script to verify connectivity:
```bash
# From your computer, or adapt for Android Terminal
cd scripts/android
./test-connection.sh
```

Expected results:
- ✓ Home Assistant accessible
- ✓ MQTT broker responsive
- ✓ MCP Hub responding
- ✓ AI Automation API available
- ✓ Tailscale VPN connected

## Next Steps

After setup:
1. Configure automations in Home Assistant
2. Set up notification channels
3. Create dashboard layouts
4. Test remote access
5. Configure backup schedules
