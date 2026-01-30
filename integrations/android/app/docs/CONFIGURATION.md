# Sample Configuration Templates for HomeAI

## Home Assistant Configuration

Add to your configuration.yaml to enable HomeAI integration:

```yaml
# Enable REST API (usually enabled by default)
api:

# Optional: Create automations that HomeAI can trigger
automation:
  - alias: "HomeAI - Good Night"
    trigger:
      - platform: event
        event_type: homeai_scene
        event_data:
          scene: good_night
    action:
      - service: light.turn_off
        target:
          entity_id: all
      - service: lock.lock
        target:
          entity_id: all

  - alias: "HomeAI - Good Morning"
    trigger:
      - platform: event
        event_type: homeai_scene
        event_data:
          scene: good_morning
    action:
      - service: light.turn_on
        target:
          entity_id: light.bedroom
        data:
          brightness_pct: 50
      - service: climate.set_temperature
        target:
          entity_id: climate.thermostat
        data:
          temperature: 72
```

## MQTT Broker Setup (Mosquitto)

/etc/mosquitto/mosquitto.conf:

```conf
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd

# For WebSocket support (optional)
listener 9001
protocol websockets
```

## Tasmota Device Configuration

Configure your Tasmota devices to report to your MQTT broker:

```
MqttHost 192.168.1.100
MqttPort 1883
MqttUser homeai
MqttPassword your_password
Topic tasmota_%06X
FullTopic %prefix%/%topic%/
```

## Zigbee2MQTT Configuration

/opt/zigbee2mqtt/data/configuration.yaml:

```yaml
mqtt:
  base_topic: zigbee2mqtt
  server: mqtt://localhost:1883
  user: homeai
  password: your_password

homeassistant: false

frontend:
  port: 8080

advanced:
  log_level: info
```

## SmartThings Personal Access Token Scopes

When creating a Personal Access Token, select these scopes:
- Devices: Read, Write, Execute
- Locations: Read
- Scenes: Read, Execute
- Installed Apps: Read

## OpenAI API Setup

1. Go to https://platform.openai.com/api-keys
2. Create a new secret key
3. Recommended: Set usage limits to control costs
4. The app uses GPT-4 Turbo for best results

## Network Requirements

Ensure your Android device can reach:
- Home Assistant: Port 8123 (HTTP) or 443 (HTTPS)
- MQTT Broker: Port 1883 (TCP) or 8883 (TLS)
- SmartThings API: api.smartthings.com (HTTPS)
- OpenAI API: api.openai.com (HTTPS)

For local network access, ensure your phone is on the same network as your home automation devices.
