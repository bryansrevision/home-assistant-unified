



# Quick Start Guide - Home Assistant MCP Integration

## 🚀 Quick Setup (5 minutes)

### Step 1: Clone Repositories


```bash
cd home-assistant-config
git clone https://github.com/bryansrevision/wearables-integration-platform.git wearables
git clone https://github.com/bryansrevision/HOME-AI-AUTOMATION.git automation
```


### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials:
# - OMI_MCP_API_TOKEN (from Omi app: Settings → Developer → MCP)
# - HOME_ASSISTANT_TOKEN (create in Home Assistant)
# - MQTT credentials
# - API keys for AI services
```


### Step 3: Start Services

```bash
docker-compose up -d

```

### Step 4: Verify Connection

```bash
# Test Omi MCP
curl -H "Authorization: Bearer $OMI_MCP_API_TOKEN" https://api.omi.me/v1/health

# Test Home Assistant
curl -H "Authorization: Bearer $HOME_ASSISTANT_TOKEN" http://homeassistant:8123/api/

# Test MQTT
mosquitto_sub -h mosquitto -u $MQTT_USER -P $MQTT_PASSWORD -t '$SYS/broker/uptime' --one
```

---

## 📋 Service Endpo<http://localhost:8123>
<http://localhost:3000>
| Service        | <http://localhost:8001> | Port | Purpose                 |
| -------------- | <http://localhost:3100> | ---- | ----------------------- |
| Home Assistant | <http://localhost:8086>3> | 8123 | Main automation hub     |
| Grafana        | <http://localhost:3000> | 3000 | Dashboards & monitoring |
| Omi Webhook    | <http://localhost:8001> | 8001 | Webhook receiver        |
| AgentStack     | <http://localhost:3100> | 3100 | AI agent UI             |
| InfluxDB       | <http://localhost:8086> | 8086 | Time-series database    |
| MQTT           | localhost             | 1883 | Message broker          |

---

## 🔑 Key Environment Variables

```yaml
# Required for Omi Integration
OMI_MCP_API_TOKEN: Bearer token from Omi app
OMI_WEBHOOK_SECRET: Secure webhook secret

# Required for Home Assistant
HOME_ASSISTANT_TOKEN: Long-lived token
HOME_ASSISTANT_URL: http://homeassistant:8123

# Required for MQTT
MQTT_BROKER: mosquitto (or IP address)
MQTT_PORT: 1883
MQTT_USER: homeassistant
MQTT_PASSWORD: strong_password

# Required for AI
OPENAI_API_KEY: For memory analysis
```

---

## 📊 MCP Server Architecture

```
┌─────────────────────────────────┐
│  Omi Wearable Device            │
│  (Recording memories)           │
└────────────┬────────────────────┘
             │ SSE Event Stream
             ▼
┌─────────────────────────────────┐
│  Omi.me MCP Server              │
│  (api.omi.me/v1/mcp/sse)       │
└────────────┬────────────────────┘
             │ Webhook Events
             ▼
┌─────────────────────────────────┐
│  FastAPI Webhook Service        │
│  (Receives & processes events)  │
└────────────┬────────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
┌────────┐ ┌────────────┐ ┌──────────┐
│ MQTT   │ │ InfluxDB   │ │ AI Agent │
│ Topics │ │ Storage    │ │ Analysis │
└────────┘ └────────────┘ └──────────┘
    │        │              │
    └────────┼──────────────┘
             ▼
    ┌─────────────────────────┐
    │ Home Assistant Core     │
    │ (Automation Engine)     │
    └────────────┬────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
    ┌────────┐      ┌──────────┐
    │ Lights │      │ Routines │
    │ Locks  │      │ Tasks    │
    │ Scenes │      │ Alerts   │
    └────────┘      └──────────┘
```

---


## 🎯 Common Tasks

### Add Omi Memory Event Trigger

```yaml
# In Home Assistant automations.yaml
- alias: "Process Omi Memory"
  trigger:
    platform: mqtt
    topic: "ha/omi/events/memory_created"

  action:
    service: python_script.process_omi_memory
```

### Extract Action Items

```yaml
- alias: "Extract Tasks from Conversation"
  trigger:
    platform: mqtt
    topic: "ha/omi/events/conversation_ended"
  action:

    service: todo.add_item
    target:
      entity_id: todo.home_assistant_tasks
```

### Monitor Health Metrics

```yaml
- alias: "Track Health from Wearable"
  trigger:
    platform: mqtt
    topic: "ha/omi/events/transcript_received"
  action:
    service: influxdb.write_points
    data:
      measurement: omi_health

```

---

## 🧪 Testing & Debugging

### View Service Logs

```bash
# All services
docker-compose logs -f


# Specific service
docker-compose logs -f omi-webhook
docker-compose logs -f homeassistant
docker-compose logs -f mosquitto
```

### Test MQTT Publishing


```bash
# Subscribe to all topics
mosquitto_sub -h mosquitto -v -t '#'

# Publish test message
mosquitto_pub -h mosquitto -t "test/topic" -m "test message"
```

### Check InfluxDB Data

```bash
# Connect to InfluxDB CLI
docker exec -it influxdb influx


# List databases
> show databases

# Query data
> use omi_metrics
> select * from omi_memory limit 5
```

### Test Omi MCP Connection

```bash
# Check server status
curl -H "Authorization: Bearer $OMI_MCP_API_TOKEN" \
  https://api.omi.me/v1/health


# Get memories (example)
curl -H "Authorization: Bearer $OMI_MCP_API_TOKEN" \
  https://api.omi.me/v1/memories?limit=5
```

---

## 🔧 Proxmox Integration

### Access Proxmox API

```bash
# From Management Hub
PROXMOX_TOKEN=$PROXMOX_TOKEN

PROXMOX_HOST=192.168.1.185


# Get cluster status
curl -s -H "Authorization: PVEAPIToken=${PROXMOX_TOKEN}" \
  "https://${PROXMOX_HOST}:8006/api2/json/cluster/status" | jq .

# List VMs
curl -s -H "Authorization: PVEAPIToken=${PROXMOX_TOKEN}" \
  "https://${PROXMOX_HOST}:8006/api2/json/nodes" | jq .

```

### Monitor via Home Assistant

Metrics from Proxmox are collected and displayed in:


- **Grafana**: Proxmox Infrastructure Dashboard
- **Home Assistant**: sensor.proxmox_cpu_usage, sensor.proxmox_memory_usage

---

## ⚠️ Important Notes


### Security

- Never commit `.env` to git
- Rotate tokens regularly (90-day rotation recommended)
- Use strong MQTT passwords
- Enable HTTPS in production

### Performance

- Monitor InfluxDB storage growth
- Set retention policies (default 30 days)
- Optimize Grafana dashboard queries
- Rate limit webhooks

### Troubleshooting

1. Check logs first: `docker-compose logs -f`
2. Verify environment variables: `env | grep OMI_`
3. Test connectivity: `curl` commands above

4. Check firewall rules for external services

---

## 📚 Resources

- [Omi.me Documentation](https://docs.omi.me)
- [Home Assistant Docs](https://www.home-assistant.io/docs/)
- [MQTT Overview](https://mqtt.org/faq)
- [InfluxDB Guide](https://docs.influxdata.com/)
- [Grafana Docs](https://grafana.com/docs/)

---

## 🆘 Support

For issues:

1. Check troubleshooting section in README.md
2. Review service logs
3. Consult GitHub issues in referenced repositories
4. Check Home Assistant community forums

---

## ✅ Verification Checklist

- [ ] All environment variables configured
- [ ] Omi MCP API token verified
- [ ] Home Assistant token generated
- [ ] Docker services running
- [ ] MQTT broker connected
- [ ] InfluxDB storing data
- [ ] Grafana dashboards loading
- [ ] Home Assistant automations loaded
- [ ] Webhook service receiving events
- [ ] AI agents processing memories
