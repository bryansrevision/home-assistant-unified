# 🔧 ADB Configuration & Terminal Control - Ulefone Armor 27T Pro

## High-Level Configuration Prompt for AI Assistants

Use this prompt with ChatGPT, Microsoft Copilot, Claude, or other AI assistants to configure ADB and terminal control:

---

## 📋 Master Configuration Prompt

```
I need to configure Android Debug Bridge (ADB) for remote control and automation of my Ulefone Armor 27T Pro device. Please provide:

1. Complete ADB setup instructions for both Windows and Linux environments
2. Network ADB (wireless) configuration steps
3. Shell scripts for common automation tasks including:
   - Device status checking
   - App installation/management
   - System settings configuration
   - Screenshot capture
   - Log collection
   - Backup/restore operations
4. Integration with Home Assistant via REST API
5. Security best practices for ADB access
6. Turnkey automation scripts for:
   - Daily health checks
   - Remote device control
   - Notification management
   - File synchronization
   - System monitoring

Device Details:
- Model: Ulefone Armor 27T Pro
- Android Version: [Your Android version]
- IP Address: [Device IP on local network]
- Use Case: Home automation integration with Proxmox VE server and Home Assistant

Requirements:
- Scripts should be production-ready and well-documented
- Include error handling and logging
- Provide both interactive and automated execution modes
- Ensure secure authentication methods
- Include integration examples with Home Assistant webhooks
```

---

## 🚀 Quick Start ADB Setup

### Enable Developer Options on Ulefone

```bash
# Step-by-step on device:
Settings → About Phone → Build Number (tap 7 times)
Settings → System → Developer Options → Enable
Settings → Developer Options → USB Debugging → Enable
Settings → Developer Options → Wireless Debugging → Enable
```

### Install ADB Tools

**Windows**:
```powershell
# Download Platform Tools
# https://developer.android.com/studio/releases/platform-tools

# Extract to C:\adb
# Add to PATH:
setx PATH "%PATH%;C:\adb"

# Verify installation
adb version
```

**Linux/Mac**:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install android-tools-adb android-tools-fastboot

# macOS (Homebrew)
brew install android-platform-tools

# Verify installation
adb version
```

---

## 📡 Connect via Network ADB

### Initial USB Setup

```bash
# Connect device via USB first
# Accept RSA fingerprint on device

# Verify connection
adb devices

# Should show:
# List of devices attached
# [serial_number]    device

# Get device IP address
adb shell ip addr show wlan0 | grep inet

# Enable TCP/IP mode on port 5555
adb tcpip 5555

# Disconnect USB cable
# Device is now ready for wireless ADB
```

### Wireless Connection

```bash
# Connect to device over network
# Replace with your device's IP
adb connect 192.168.1.XXX:5555

# Verify connection
adb devices

# Should show:
# 192.168.1.XXX:5555    device

# Test connection
adb shell echo "Connected successfully"
```

### Persistent Wireless ADB Script

```bash
#!/bin/bash
# File: adb-connect-ulefone.sh

DEVICE_IP="192.168.1.XXX"  # Replace with your device IP
ADB_PORT="5555"

echo "Connecting to Ulefone Armor 27T Pro..."

# Connect to device
adb connect ${DEVICE_IP}:${ADB_PORT}

# Wait for connection
sleep 2

# Verify connection
if adb devices | grep -q "${DEVICE_IP}"; then
    echo "✓ Connected successfully to ${DEVICE_IP}"
    
    # Get device info
    echo "Device Information:"
    echo "  Model: $(adb shell getprop ro.product.model)"
    echo "  Android: $(adb shell getprop ro.build.version.release)"
    echo "  Battery: $(adb shell dumpsys battery | grep level | cut -d: -f2 | tr -d ' ')%"
    echo "  WiFi: $(adb shell dumpsys wifi | grep 'Wi-Fi is' | cut -d' ' -f3)"
else
    echo "✗ Connection failed"
    echo "Troubleshooting:"
    echo "  1. Ensure device is on same WiFi network"
    echo "  2. Verify Wireless Debugging is enabled"
    echo "  3. Check device IP: adb shell ip addr show wlan0"
    exit 1
fi
```

---

## 🤖 Turnkey Automation Scripts

### Script 1: Complete Device Setup

```bash
#!/bin/bash
# File: ulefone-turnkey-setup.sh
# Description: Complete automated setup for Ulefone Armor 27T Pro

set -e  # Exit on error

DEVICE_IP="192.168.1.XXX"
HA_WEBHOOK="http://192.168.1.134:8123/api/webhook"

echo "🔧 Ulefone Armor 27T Pro - Turnkey Setup"
echo "========================================"

# Function: Connect to device
connect_device() {
    echo "📡 Connecting to device..."
    adb connect ${DEVICE_IP}:5555
    sleep 2
    
    if ! adb devices | grep -q "${DEVICE_IP}"; then
        echo "❌ Failed to connect"
        exit 1
    fi
    echo "✅ Connected"
}

# Function: Install apps
install_apps() {
    echo "📲 Installing essential apps..."
    
    # Home Assistant Companion
    if [ -f "homeassistant.apk" ]; then
        adb install -r homeassistant.apk
        echo "  ✓ Home Assistant installed"
    fi
    
    # Tasker
    if [ -f "tasker.apk" ]; then
        adb install -r tasker.apk
        echo "  ✓ Tasker installed"
    fi
    
    # Tailscale
    if [ -f "tailscale.apk" ]; then
        adb install -r tailscale.apk
        echo "  ✓ Tailscale installed"
    fi
}

# Function: Configure system settings
configure_settings() {
    echo "⚙️  Configuring system settings..."
    
    # Disable battery optimization for critical apps
    adb shell dumpsys deviceidle whitelist +io.homeassistant.companion.android
    adb shell dumpsys deviceidle whitelist +com.tailscale.ipn
    adb shell dumpsys deviceidle whitelist +net.dinglisch.android.taskerm
    echo "  ✓ Battery optimization disabled"
    
    # Enable location services
    adb shell settings put secure location_mode 3
    echo "  ✓ Location high accuracy enabled"
    
    # Set screen timeout to 5 minutes
    adb shell settings put system screen_off_timeout 300000
    echo "  ✓ Screen timeout set"
    
    # Enable stay awake while charging
    adb shell settings put global stay_on_while_plugged_in 3
    echo "  ✓ Stay awake enabled"
    
    # Disable adaptive brightness
    adb shell settings put system screen_brightness_mode 0
    echo "  ✓ Manual brightness set"
}

# Function: Setup NFC
setup_nfc() {
    echo "🏷️  Configuring NFC..."
    
    # Enable NFC
    adb shell svc nfc enable
    echo "  ✓ NFC enabled"
    
    # Enable NFC beam
    adb shell settings put global nfc_beam_on 1
    echo "  ✓ NFC beam enabled"
}

# Function: Configure network
configure_network() {
    echo "📶 Configuring network..."
    
    # Enable WiFi
    adb shell svc wifi enable
    sleep 2
    
    # Get WiFi status
    WIFI_STATUS=$(adb shell dumpsys wifi | grep "Wi-Fi is" | cut -d' ' -f3)
    echo "  WiFi status: ${WIFI_STATUS}"
    
    # Enable mobile data
    adb shell svc data enable
    echo "  ✓ Mobile data enabled"
}

# Function: Install Home Assistant webhooks
setup_webhooks() {
    echo "🔗 Setting up webhooks..."
    
    # Create webhook test
    adb shell "am broadcast -a android.intent.action.VIEW -d '${HA_WEBHOOK}/adb_setup_complete'"
    echo "  ✓ Webhook test sent"
}

# Function: Create automation scripts on device
deploy_scripts() {
    echo "📜 Deploying automation scripts..."
    
    # Create scripts directory
    adb shell mkdir -p /sdcard/automation
    
    # Push script: Daily health check
    cat > /tmp/daily_health.sh << 'EOF'
#!/system/bin/sh
# Daily health check script

WEBHOOK="http://192.168.1.134:8123/api/webhook/device_health"

BATTERY=$(dumpsys battery | grep level | cut -d: -f2 | tr -d ' ')
TEMP=$(dumpsys battery | grep temperature | cut -d: -f2 | tr -d ' ')
STORAGE=$(df /sdcard | tail -1 | awk '{print $5}')

curl -X POST $WEBHOOK \
  -H "Content-Type: application/json" \
  -d "{\"battery\":$BATTERY,\"temp\":$TEMP,\"storage\":\"$STORAGE\"}"
EOF
    
    adb push /tmp/daily_health.sh /sdcard/automation/
    adb shell chmod +x /sdcard/automation/daily_health.sh
    echo "  ✓ Health check script deployed"
}

# Function: Backup device data
backup_device() {
    echo "💾 Creating device backup..."
    
    BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p ${BACKUP_DIR}
    
    # Backup apps and data
    adb backup -f ${BACKUP_DIR}/ulefone_backup.ab -all -apk -shared
    echo "  ✓ Backup created: ${BACKUP_DIR}"
}

# Function: Test all features
test_features() {
    echo "🧪 Testing features..."
    
    # Test notifications
    adb shell am broadcast -a android.intent.action.VIEW \
        -d "homeassistant://navigate/lovelace"
    echo "  ✓ Notification test"
    
    # Test IR blaster (if available)
    if adb shell pm list features | grep -q "android.hardware.consumerir"; then
        echo "  ✓ IR blaster available"
    fi
    
    # Test NFC
    if adb shell pm list features | grep -q "android.hardware.nfc"; then
        echo "  ✓ NFC available"
    fi
    
    # Test sensors
    adb shell dumpsys sensorservice | grep -i "accelerometer"
    echo "  ✓ Sensors active"
}

# Main execution
main() {
    connect_device
    install_apps
    configure_settings
    setup_nfc
    configure_network
    setup_webhooks
    deploy_scripts
    backup_device
    test_features
    
    echo ""
    echo "✅ Turnkey setup complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Open Home Assistant app and login"
    echo "  2. Grant all requested permissions"
    echo "  3. Configure Tailscale VPN"
    echo "  4. Test automation scripts"
    echo ""
    echo "Device is ready for production use! 🚀"
}

# Run main function
main
```

### Script 2: Daily Health Monitor

```bash
#!/bin/bash
# File: ulefone-health-monitor.sh
# Description: Monitor device health and report to Home Assistant

DEVICE_IP="192.168.1.XXX"
HA_WEBHOOK="http://192.168.1.134:8123/api/webhook/ulefone_health"

# Connect to device
adb connect ${DEVICE_IP}:5555 2>/dev/null
sleep 1

# Collect metrics
BATTERY_LEVEL=$(adb shell dumpsys battery | grep level | cut -d: -f2 | tr -d ' ')
BATTERY_TEMP=$(adb shell dumpsys battery | grep temperature | cut -d: -f2 | tr -d ' ')
BATTERY_HEALTH=$(adb shell dumpsys battery | grep health | cut -d: -f2 | tr -d ' ')
CHARGING=$(adb shell dumpsys battery | grep "AC powered" | cut -d: -f2 | tr -d ' ')

CPU_TEMP=$(adb shell cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo "0")
MEMORY_FREE=$(adb shell cat /proc/meminfo | grep MemAvailable | awk '{print $2}')
STORAGE_FREE=$(adb shell df /sdcard | tail -1 | awk '{print $4}')

UPTIME=$(adb shell cat /proc/uptime | cut -d' ' -f1)
WIFI_SSID=$(adb shell dumpsys wifi | grep "mWifiInfo SSID:" | cut -d: -f2 | tr -d ' ')

# Send to Home Assistant
curl -X POST ${HA_WEBHOOK} \
  -H "Content-Type: application/json" \
  -d "{
    \"device\": \"ulefone_armor_27t_pro\",
    \"timestamp\": \"$(date -Iseconds)\",
    \"battery\": {
      \"level\": ${BATTERY_LEVEL},
      \"temperature\": $((${BATTERY_TEMP}/10)),
      \"health\": ${BATTERY_HEALTH},
      \"charging\": ${CHARGING}
    },
    \"system\": {
      \"cpu_temp\": $((${CPU_TEMP}/1000)),
      \"memory_free_kb\": ${MEMORY_FREE},
      \"storage_free_kb\": ${STORAGE_FREE},
      \"uptime_seconds\": ${UPTIME}
    },
    \"network\": {
      \"wifi_ssid\": \"${WIFI_SSID}\"
    }
  }"

echo "Health report sent to Home Assistant"
```

### Script 3: Remote Control Interface

```bash
#!/bin/bash
# File: ulefone-remote-control.sh
# Description: Interactive remote control menu

DEVICE_IP="192.168.1.XXX"

# Connect
adb connect ${DEVICE_IP}:5555
sleep 1

# Menu function
show_menu() {
    clear
    echo "╔════════════════════════════════════════╗"
    echo "║  Ulefone Armor 27T Pro Remote Control  ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    echo "Device: ${DEVICE_IP}"
    echo "Status: $(adb devices | grep ${DEVICE_IP} | awk '{print $2}')"
    echo ""
    echo "1)  Take Screenshot"
    echo "2)  Reboot Device"
    echo "3)  Install APK"
    echo "4)  Pull Logs"
    echo "5)  Send Notification"
    echo "6)  Toggle WiFi"
    echo "7)  Toggle Airplane Mode"
    echo "8)  Lock Screen"
    echo "9)  Unlock Screen"
    echo "10) Launch Home Assistant"
    echo "11) System Information"
    echo "12) File Browser"
    echo "0)  Exit"
    echo ""
    echo -n "Select option: "
}

# Functions for each menu item
take_screenshot() {
    echo "Taking screenshot..."
    adb shell screencap /sdcard/screenshot.png
    adb pull /sdcard/screenshot.png ./screenshot_$(date +%Y%m%d_%H%M%S).png
    echo "Screenshot saved"
}

reboot_device() {
    echo "Rebooting device..."
    adb reboot
}

install_apk() {
    echo -n "Enter APK path: "
    read APK_PATH
    adb install -r ${APK_PATH}
}

pull_logs() {
    echo "Pulling logs..."
    adb logcat -d > ulefone_logs_$(date +%Y%m%d_%H%M%S).txt
    echo "Logs saved"
}

send_notification() {
    echo -n "Enter notification title: "
    read TITLE
    echo -n "Enter notification message: "
    read MESSAGE
    
    adb shell am broadcast \
        -a android.intent.action.VIEW \
        -d "notification://?title=${TITLE}&message=${MESSAGE}"
}

toggle_wifi() {
    STATUS=$(adb shell settings get global wifi_on)
    if [ "$STATUS" = "1" ]; then
        adb shell svc wifi disable
        echo "WiFi disabled"
    else
        adb shell svc wifi enable
        echo "WiFi enabled"
    fi
}

toggle_airplane() {
    STATUS=$(adb shell settings get global airplane_mode_on)
    if [ "$STATUS" = "1" ]; then
        adb shell settings put global airplane_mode_on 0
        adb shell am broadcast -a android.intent.action.AIRPLANE_MODE
        echo "Airplane mode disabled"
    else
        adb shell settings put global airplane_mode_on 1
        adb shell am broadcast -a android.intent.action.AIRPLANE_MODE
        echo "Airplane mode enabled"
    fi
}

lock_screen() {
    adb shell input keyevent 26
    echo "Screen locked"
}

unlock_screen() {
    adb shell input keyevent 82
    echo "Screen unlocked"
}

launch_homeassistant() {
    adb shell am start -n io.homeassistant.companion.android/.onboarding.OnboardingActivity
    echo "Home Assistant launched"
}

system_info() {
    echo ""
    echo "System Information:"
    echo "  Model: $(adb shell getprop ro.product.model)"
    echo "  Android: $(adb shell getprop ro.build.version.release)"
    echo "  SDK: $(adb shell getprop ro.build.version.sdk)"
    echo "  Serial: $(adb shell getprop ro.serialno)"
    echo "  Build: $(adb shell getprop ro.build.display.id)"
    echo "  Battery: $(adb shell dumpsys battery | grep level | cut -d: -f2)%"
    echo "  Uptime: $(adb shell uptime)"
    echo ""
    read -p "Press Enter to continue..."
}

file_browser() {
    echo -n "Enter path (default /sdcard): "
    read PATH
    PATH=${PATH:-/sdcard}
    adb shell ls -la ${PATH}
    read -p "Press Enter to continue..."
}

# Main loop
while true; do
    show_menu
    read OPTION
    
    case $OPTION in
        1) take_screenshot ;;
        2) reboot_device ;;
        3) install_apk ;;
        4) pull_logs ;;
        5) send_notification ;;
        6) toggle_wifi ;;
        7) toggle_airplane ;;
        8) lock_screen ;;
        9) unlock_screen ;;
        10) launch_homeassistant ;;
        11) system_info ;;
        12) file_browser ;;
        0) echo "Goodbye!"; exit 0 ;;
        *) echo "Invalid option" ;;
    esac
    
    sleep 2
done
```

### Script 4: Home Assistant Integration

```bash
#!/bin/bash
# File: ulefone-ha-integration.sh
# Description: Integrate device status with Home Assistant

DEVICE_IP="192.168.1.XXX"
HA_URL="http://192.168.1.134:8123"
HA_TOKEN="YOUR_LONG_LIVED_TOKEN"

# Function: Update sensor in HA
update_ha_sensor() {
    local entity_id=$1
    local state=$2
    local attributes=$3
    
    curl -X POST "${HA_URL}/api/states/${entity_id}" \
        -H "Authorization: ******
        -H "Content-Type: application/json" \
        -d "{
            \"state\": \"${state}\",
            \"attributes\": ${attributes}
        }"
}

# Connect to device
adb connect ${DEVICE_IP}:5555 >/dev/null 2>&1

# Collect and update battery sensor
BATTERY=$(adb shell dumpsys battery | grep level | cut -d: -f2 | tr -d ' ')
update_ha_sensor "sensor.ulefone_battery" "${BATTERY}" \
    '{"unit_of_measurement":"%","device_class":"battery"}'

# Update charging sensor
CHARGING=$(adb shell dumpsys battery | grep "AC powered" | cut -d: -f2 | tr -d ' ')
if [ "${CHARGING}" = "true" ]; then
    CHARGE_STATE="charging"
else
    CHARGE_STATE="not_charging"
fi
update_ha_sensor "binary_sensor.ulefone_charging" "${CHARGE_STATE}" '{}'

# Update WiFi sensor
WIFI_SSID=$(adb shell dumpsys wifi | grep "mWifiInfo SSID:" | cut -d: -f2 | tr -d ' ' | tr -d '"')
update_ha_sensor "sensor.ulefone_wifi" "${WIFI_SSID}" '{"icon":"mdi:wifi"}'

echo "Home Assistant sensors updated"
```

---

## 🔐 Security Configuration

### Secure ADB Access

```bash
#!/bin/bash
# File: secure-adb-setup.sh

# Generate new RSA key pair
adb kill-server
rm ~/.android/adbkey*
adb start-server

# Connect and authorize
adb connect 192.168.1.XXX:5555

echo "Check device screen and accept RSA fingerprint"
echo "Waiting for authorization..."
sleep 5

# Verify secure connection
if adb devices | grep -q "device"; then
    echo "✓ Secure connection established"
    
    # Backup key
    cp ~/.android/adbkey ~/.android/adbkey.backup
    cp ~/.android/adbkey.pub ~/.android/adbkey.pub.backup
    
    echo "Keys backed up to ~/.android/"
else
    echo "✗ Authorization failed"
fi
```

---

## 📊 Monitoring Dashboard Script

```python
#!/usr/bin/env python3
# File: ulefone-dashboard.py
# Description: Real-time monitoring dashboard

import subprocess
import time
import json
import requests
from datetime import datetime

DEVICE_IP = "192.168.1.XXX"
HA_WEBHOOK = "http://192.168.1.134:8123/api/webhook/ulefone_monitor"

def adb_command(cmd):
    """Execute ADB command and return output"""
    try:
        result = subprocess.run(
            f"adb -s {DEVICE_IP}:5555 {cmd}",
            shell=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def get_device_metrics():
    """Collect all device metrics"""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "battery_level": adb_command("shell dumpsys battery | grep level | cut -d: -f2"),
        "battery_temp": adb_command("shell dumpsys battery | grep temperature | cut -d: -f2"),
        "cpu_usage": adb_command("shell top -n 1 | grep 'CPU'"),
        "memory_info": adb_command("shell cat /proc/meminfo | grep MemAvailable"),
        "storage_free": adb_command("shell df /sdcard | tail -1"),
        "wifi_ssid": adb_command("shell dumpsys wifi | grep 'mWifiInfo SSID'"),
        "location": adb_command("shell dumpsys location | grep 'last location'"),
    }
    return metrics

def send_to_homeassistant(metrics):
    """Send metrics to Home Assistant"""
    try:
        response = requests.post(HA_WEBHOOK, json=metrics)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send to HA: {e}")
        return False

def main():
    """Main monitoring loop"""
    print("Starting Ulefone monitoring dashboard...")
    print(f"Device: {DEVICE_IP}")
    print("Press Ctrl+C to stop\n")
    
    while True:
        try:
            metrics = get_device_metrics()
            
            # Display locally
            print(f"\n=== {metrics['timestamp']} ===")
            print(f"Battery: {metrics['battery_level']}%")
            print(f"Temperature: {int(metrics['battery_temp'])/10}°C")
            print(f"WiFi: {metrics['wifi_ssid']}")
            
            # Send to HA
            if send_to_homeassistant(metrics):
                print("✓ Sent to Home Assistant")
            
            time.sleep(60)  # Update every minute
            
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
```

---

## 🚀 Quick Commands Reference

```bash
# Essential commands
adb devices                          # List connected devices
adb connect IP:5555                  # Connect wirelessly
adb disconnect                       # Disconnect all
adb shell                           # Open shell
adb reboot                          # Reboot device

# File operations
adb push local.txt /sdcard/         # Upload file
adb pull /sdcard/file.txt ./        # Download file
adb shell ls /sdcard/               # List files

# App management
adb install app.apk                 # Install app
adb install -r app.apk              # Reinstall app
adb uninstall com.package.name      # Uninstall app
adb shell pm list packages          # List all packages

# System control
adb shell input text "Hello"        # Type text
adb shell input tap 500 1000        # Tap coordinates
adb shell input swipe 300 500 300 1000  # Swipe
adb shell screencap /sdcard/s.png   # Screenshot
adb shell screenrecord /sdcard/v.mp4  # Record screen

# System info
adb shell getprop                   # All properties
adb shell dumpsys battery           # Battery info
adb shell dumpsys wifi              # WiFi info
adb logcat                          # View logs
```

---

## 📝 Cron Job Setup

```bash
# Edit crontab
crontab -e

# Add monitoring jobs
*/5 * * * * /path/to/ulefone-health-monitor.sh
0 8 * * * /path/to/ulefone-daily-report.sh
0 */4 * * * /path/to/ulefone-backup.sh
```

---

## ✅ Post-Setup Checklist

- [ ] ADB installed and working
- [ ] Device connected via network
- [ ] All automation scripts deployed
- [ ] Home Assistant integration tested
- [ ] Security keys backed up
- [ ] Monitoring dashboard running
- [ ] Cron jobs configured
- [ ] Emergency access documented

**Device is now fully configured and integrated! 🎉**
