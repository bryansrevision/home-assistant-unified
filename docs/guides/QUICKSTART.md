# Quick Start Guide: MQTT Integration & Automated Backups

## Overview
This guide provides a streamlined path to configure MQTT integration and automated backups for your Home Assistant instance at http://192.168.1.134:8123.

## Prerequisites
- [ ] Home Assistant instance running and accessible
- [ ] Docker and Docker Compose installed
- [ ] Git installed and configured
- [ ] GitHub account with access to bryansrevision/HOME-AI-AUTOMATION
- [ ] Home Assistant long-lived access token

## Part 1: MQTT Integration (30 minutes)

### Step 1: Prepare Environment

```bash
# Navigate to homeassistant directory
cd /path/to/proxmox-personal-data-platform/docker-compose/homeassistant

# Copy environment template
cp .env.template .env

# Generate strong MQTT password
openssl rand -base64 32
```

### Step 2: Configure MQTT

Edit `.env` file:
```bash
MQTT_USER=homeassistant
MQTT_PASSWORD=<paste_generated_password>
MQTT_PORT=1883
```

### Step 3: Create Mosquitto Configuration

```bash
# Create directories
mkdir -p data/mosquitto/config data/mosquitto/data data/mosquitto/log

# Create configuration file
cat > data/mosquitto/config/mosquitto.conf << 'EOF'
listener 1883
allow_anonymous false
password_file /mosquitto/config/password.txt
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
log_dest stdout
EOF
```

### Step 4: Create Password File

```bash
# Start Mosquitto temporarily
docker-compose up -d mosquitto

# Create password file
docker exec -it mosquitto mosquitto_passwd -c /mosquitto/config/password.txt homeassistant
# Enter your MQTT password when prompted

# Restart Mosquitto
docker-compose restart mosquitto

# Verify it's running
docker-compose ps mosquitto
docker-compose logs mosquitto --tail 20
```

### Step 5: Test MQTT

```bash
# Subscribe to test topic
mosquitto_sub -h localhost -p 1883 -u homeassistant -P "YOUR_PASSWORD" -t 'test/connection' -v

# In another terminal, publish
mosquitto_pub -h localhost -p 1883 -u homeassistant -P "YOUR_PASSWORD" -t 'test/connection' -m 'Hello MQTT'
```

✅ **Success**: You should see "Hello MQTT" in the subscriber terminal

### Step 6: Add MQTT to Home Assistant

**Via UI (Recommended):**
1. Open http://192.168.1.134:8123
2. Go to **Settings → Devices & Services**
3. Click **+ ADD INTEGRATION**
4. Search for "MQTT" and select it
5. Enter connection details:
   - Broker: `localhost` (if on same host) or `192.168.1.XXX`
   - Port: `1883`
   - Username: `homeassistant`
   - Password: `<your_mqtt_password>`
6. Click **Submit**

✅ **Success**: MQTT integration shows as "Configured"

### Step 7: Verify Integration

```bash
# In Home Assistant, go to Developer Tools → MQTT
# Listen to topic: #
# Click START LISTENING

# Publish test message
mosquitto_pub -h 192.168.1.134 -p 1883 -u homeassistant -P "YOUR_PASSWORD" \
  -t 'homeassistant/test' -m '{"status": "working"}'
```

✅ **Success**: Message appears in Home Assistant Developer Tools

## Part 2: Automated Backups (15 minutes)

### Step 1: Create Long-Lived Access Token

1. Open Home Assistant
2. Click your profile (bottom left)
3. Scroll to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Name: "Automated Backups"
6. **Copy the token immediately** (you won't see it again!)

### Step 2: Add GitHub Secret

1. Go to https://github.com/bryansrevision/HOME-AI-AUTOMATION
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `HA_TOKEN`
5. Value: `<paste_your_token>`
6. Click **Add secret**

### Step 3: Test Backup Locally (Optional)

```bash
cd /path/to/HOME-AI-AUTOMATION

# Set environment variables
export HA_URL="http://192.168.1.134:8123"
export HA_TOKEN="your_token_here"

# Run validation test
python scripts/test_backup_setup.py

# If all tests pass, run actual backup
python scripts/ha_backup.py --test-connection
python scripts/ha_backup.py
```

✅ **Success**: Backup file created in `backups/` directory

### Step 4: Enable GitHub Actions

The workflow is already committed. To verify:

1. Go to https://github.com/bryansrevision/HOME-AI-AUTOMATION/actions
2. Find "Home Assistant Automated Backup" workflow
3. Click **Run workflow** to test manually
4. Select branch: `main`
5. (Optional) Enter custom backup name
6. Click **Run workflow**

✅ **Success**: Workflow completes successfully, backup available in artifacts

### Step 5: Verify Scheduled Runs

The workflow runs automatically daily at 2 AM UTC. To verify:

1. Check `.github/workflows/ha-backup.yml` is present
2. View Actions tab for scheduled runs
3. Next run will appear in Actions tab after 2 AM UTC

## Part 3: Optional - Zigbee2MQTT (45 minutes)

### Prerequisites
- Zigbee USB coordinator (CC2531, CC2652, ConBee II, etc.)
- Zigbee devices to pair

### Quick Setup

```bash
# 1. Identify USB device
ls -la /dev/tty*
# Look for /dev/ttyUSB0 or /dev/ttyACM0

# 2. Update .env
echo "ZIGBEE_DEVICE=/dev/ttyUSB0" >> .env

# 3. Uncomment Zigbee2MQTT in docker-compose.yml
# Edit docker-compose.yml and uncomment the zigbee2mqtt service

# 4. Create configuration
mkdir -p data/zigbee2mqtt
cat > data/zigbee2mqtt/configuration.yaml << 'EOF'
homeassistant: true
mqtt:
  base_topic: zigbee2mqtt
  server: mqtt://mosquitto:1883
  user: homeassistant
  password: YOUR_MQTT_PASSWORD
serial:
  port: /dev/ttyUSB0
  adapter: auto
frontend:
  port: 8080
advanced:
  log_level: info
  channel: 11
EOF

# 5. Start Zigbee2MQTT
docker-compose up -d zigbee2mqtt

# 6. Access web UI
# Open http://192.168.1.134:8080
```

✅ **Success**: Zigbee2MQTT web interface accessible, coordinator connected

### Pairing Devices

1. Open Zigbee2MQTT UI: http://192.168.1.134:8080
2. Click "Permit join (All)"
3. Put device in pairing mode (see device manual)
4. Wait for device to appear in UI
5. Rename device with friendly name
6. Device auto-discovers in Home Assistant

## Verification Checklist

### MQTT Integration
- [ ] Mosquitto broker running (`docker-compose ps mosquitto`)
- [ ] No errors in logs (`docker-compose logs mosquitto`)
- [ ] Authentication working (mosquitto_pub/sub tests pass)
- [ ] Home Assistant MQTT integration configured
- [ ] Test messages sent/received successfully
- [ ] MQTT Developer Tools showing activity

### Automated Backups
- [ ] GitHub Secret `HA_TOKEN` configured
- [ ] Validation script passes all tests
- [ ] Manual backup creation works
- [ ] GitHub Actions workflow exists
- [ ] Manual workflow run succeeds
- [ ] Backup artifacts uploaded
- [ ] Metadata committed to repository

### Zigbee2MQTT (Optional)
- [ ] USB coordinator detected
- [ ] Zigbee2MQTT container running
- [ ] Web UI accessible
- [ ] Coordinator firmware detected
- [ ] Connected to MQTT broker
- [ ] Devices can be paired
- [ ] Devices appear in Home Assistant

## Troubleshooting

### MQTT Connection Issues
```bash
# Check Mosquitto is running
docker-compose ps mosquitto

# Check logs
docker-compose logs mosquitto --tail 50

# Test connectivity
nc -zv localhost 1883

# Restart if needed
docker-compose restart mosquitto
```

### Backup Script Errors
```bash
# Check HA is accessible
curl -H "Authorization: Bearer $HA_TOKEN" http://192.168.1.134:8123/api/

# Test connection
python scripts/ha_backup.py --test-connection

# Check logs
cat ha_backup.log
```

### Zigbee2MQTT Issues
```bash
# Check container status
docker-compose ps zigbee2mqtt

# Check logs
docker-compose logs zigbee2mqtt --tail 50

# Verify USB device
ls -la /dev/ttyUSB0

# Restart
docker-compose restart zigbee2mqtt
```

## Documentation Links

### Detailed Guides
- **MQTT Setup**: [IMPLEMENTATION_GUIDE_MQTT.md](https://github.com/bryansrevision/proxmox-personal-data-platform/blob/main/docker-compose/homeassistant/IMPLEMENTATION_GUIDE_MQTT.md)
- **Zigbee2MQTT**: [ZIGBEE2MQTT_SETUP.md](https://github.com/bryansrevision/proxmox-personal-data-platform/blob/main/docker-compose/homeassistant/ZIGBEE2MQTT_SETUP.md)
- **Testing Guide**: [TESTING_GUIDE.md](https://github.com/bryansrevision/proxmox-personal-data-platform/blob/main/docker-compose/homeassistant/TESTING_GUIDE.md)
- **Backup System**: [README_BACKUP.md](https://github.com/bryansrevision/HOME-AI-AUTOMATION/blob/main/scripts/README_BACKUP.md)
- **Implementation Summary**: [IMPLEMENTATION_SUMMARY.md](https://github.com/bryansrevision/HOME-AI-AUTOMATION/blob/main/IMPLEMENTATION_SUMMARY.md)

### External Resources
- [Home Assistant MQTT Integration](https://www.home-assistant.io/integrations/mqtt/)
- [Mosquitto Documentation](https://mosquitto.org/documentation/)
- [Zigbee2MQTT Documentation](https://www.zigbee2mqtt.io/)
- [Home Assistant Backup API](https://developers.home-assistant.io/docs/api/supervisor/endpoints/#backups)

## Support

### GitHub Repositories
- [HOME-AI-AUTOMATION](https://github.com/bryansrevision/HOME-AI-AUTOMATION) - Backup automation
- [proxmox-personal-data-platform](https://github.com/bryansrevision/proxmox-personal-data-platform) - MQTT setup

### Issues & Questions
- Create issues in respective repositories
- Check existing documentation first
- Include logs and error messages
- Describe steps to reproduce

## Next Steps

After completing this guide:

1. **Monitor System**
   - Check backup logs daily for first week
   - Monitor MQTT broker performance
   - Watch for device connectivity issues

2. **Expand Integration**
   - Add more MQTT devices (ESPHome, Tasmota)
   - Create automations using MQTT sensors
   - Set up Zigbee devices (if applicable)

3. **Security Hardening**
   - Enable TLS/SSL for MQTT (production)
   - Configure firewall rules
   - Implement MQTT ACLs
   - Regular token rotation

4. **Backup Strategy**
   - Test backup restoration
   - Consider off-site backup storage
   - Document restore procedures
   - Set up backup monitoring/alerts

## Estimated Time to Complete

- **MQTT Integration**: 30 minutes
- **Automated Backups**: 15 minutes
- **Zigbee2MQTT** (optional): 45 minutes
- **Testing & Verification**: 15 minutes

**Total**: ~1-2 hours for complete setup

---

**Last Updated**: 2024-01-24
**Maintained By**: bryansrevision
**Status**: Production Ready ✅
