# 🚀 UNIFIED HOME ASSISTANT - Quick Start Guide

Get your complete Home Automation ecosystem running in 5 minutes!

---

## ⚡ Prerequisites

- **Docker & Docker Compose** installed
- **Home Assistant** instance running (192.168.1.134:8123)
- **Omi wearable** (optional) for wearables integration
- **Proxmox VE** (optional) for infrastructure monitoring

---

## 📋 Step 1: Clone & Configure (2 minutes)

```bash
cd c:/Users/Dylan/Dev/environments/Windows/HomeAssistant-Workspace/UNIFIED-HOME-ASSISTANT

# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

### Required Environment Variables

```bash
# Home Assistant
HOME_ASSISTANT_URL=http://192.168.1.134:8123
HOME_ASSISTANT_TOKEN=your_long_lived_token_here

# Omi Wearables (if using)
OMI_MCP_API_TOKEN=your_omi_token_here

# AI Providers
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here  # Optional
GROK_API_KEY=your_grok_key_here      # Optional

# Infrastructure (if using Proxmox)
PROXMOX_HOST=192.168.1.185
PROXMOX_TOKEN=your_proxmox_token_here

# GitHub (for repository sync)
GITHUB_TOKEN=your_github_pat_here

# Database & Monitoring
INFLUXDB_USER=admin
INFLUXDB_PASSWORD=secure_password_here
INFLUXDB_TOKEN=your_influx_token_here
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
```

---

## 🐳 Step 2: Deploy Services (1 minute)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

---

## ✅ Step 3: Verify Setup (2 minutes)

### Check Services

```bash
# MQTT Broker
docker exec unified-mosquitto mosquitto_sub -t '$SYS/#' -C 1

# InfluxDB
curl http://localhost:8086/health

# Grafana
open http://localhost:3000
# Login: admin / admin (change on first login)

# Home Automation API
curl http://localhost:8000/health

# MCP Hub
curl http://localhost:8080/health
```

### Test Home Assistant Connection

```bash
# Test HA API
curl -H "Authorization: Bearer YOUR_HA_TOKEN" \
     http://192.168.1.134:8123/api/

# Should return: {"message": "API running."}
```

### Test Omi Wearables (if configured)

```bash
# Check Omi MCP connection
curl -H "Authorization: Bearer YOUR_OMI_TOKEN" \
     https://api.omi.me/v1/health
```

---

## 🔄 Step 4: Sync Repositories (optional)

If you want to sync with source repositories:

```bash
# Pull latest from all repos
./scripts/sync-from-repos.sh --all

# Review changes
git status

# Commit if needed
git commit -am "sync: Initial sync from source repos"
```

---

## 📊 Step 5: Access Dashboards

### Grafana Dashboards
- **URL:** http://localhost:3000
- **Login:** admin / admin
- **Dashboards:**
  - Home Automation Overview
  - Omi Wearables Metrics
  - Proxmox Infrastructure
  - System Health

### Home Automation API
- **URL:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Endpoints:**
  - `/api/homeassistant/states` - Get all HA entities
  - `/api/remote/devices` - List remote devices
  - `/api/mobile/devices` - List mobile devices
  - `/api/ai/status` - AI provider status

---

## 🤖 Step 6: Test Automations

### Trigger Test Automation

```bash
# Send test MQTT message
docker exec unified-mosquitto mosquitto_pub \
  -t 'ha/omi/events/memory_created' \
  -m '{"memory_id":"test123","content":"Test memory"}'

# Check InfluxDB for data
curl -G 'http://localhost:8086/query' \
  --data-urlencode "db=home_automation" \
  --data-urlencode "q=SELECT * FROM omi_events LIMIT 10"
```

### View Automation Logs

```bash
# HA API logs
docker-compose logs -f ha-api

# MCP Hub logs
docker-compose logs -f mcp-hub

# AgentStack logs
docker-compose logs -f agentstack
```

---

## 📱 Step 7: Configure Integrations

### Mobile Devices

1. Install Home Assistant Companion App on Android
2. Configure in app: Settings → Companion App → Server → http://192.168.1.134:8123
3. Add device in `integrations/mobile-devices/configs/`

### Omi Wearables

1. Open Omi mobile app
2. Go to Settings → Developer → MCP
3. Copy API Token
4. Add to `.env`: `OMI_MCP_API_TOKEN=your_token`
5. Restart services: `docker-compose restart mcp-hub`

### Proxmox

1. Create API token in Proxmox
2. Add to `.env`: `PROXMOX_TOKEN=username@pam!tokenid=secret`
3. Restart services: `docker-compose restart mcp-hub`

---

## 🛠️ Troubleshooting

### Services Won't Start

```bash
# Check Docker
docker ps

# Check logs
docker-compose logs

# Restart specific service
docker-compose restart mosquitto
```

### MQTT Connection Failed

```bash
# Test MQTT
docker exec unified-mosquitto mosquitto_sub -t '#' -v

# Check config
cat ./services/mqtt/config/mosquitto.conf
```

### Home Assistant Connection Failed

```bash
# Verify HA is running
curl http://192.168.1.134:8123

# Check token
echo $HOME_ASSISTANT_TOKEN

# Test API
curl -H "Authorization: Bearer $HOME_ASSISTANT_TOKEN" \
     http://192.168.1.134:8123/api/
```

### InfluxDB Not Accepting Data

```bash
# Check InfluxDB health
curl http://localhost:8086/health

# View logs
docker-compose logs influxdb

# Recreate database
docker-compose down influxdb
docker volume rm unified_influxdb_data
docker-compose up -d influxdb
```

---

## 🎯 Next Steps

1. ✅ **Customize Automations** - Edit `automations/unified-automations.yaml`
2. ✅ **Add Dashboards** - Create Grafana dashboards
3. ✅ **Configure Alerts** - Set up notification services
4. ✅ **Sync Repos** - Run `./scripts/sync-from-repos.sh --all`
5. ✅ **Backup** - Configure automated backups

---

## 📚 Documentation

- [Full README](./README.md) - Complete documentation
- [Sync Guide](./SYNC_GUIDE.md) - Repository synchronization
- [API Reference](./docs/API_REFERENCE.md) - API documentation
- [Architecture](./docs/ARCHITECTURE.md) - System design

---

## 🆘 Getting Help

- Check [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)
- Review logs: `docker-compose logs -f`
- Check service health: `docker-compose ps`
- Verify .env configuration

---

**🎉 You're all set! Your unified Home Assistant ecosystem is running!**

Access your dashboards:
- **Grafana:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Home Assistant:** http://192.168.1.134:8123
