# Home Assistant Configuration Workspace

Unified Home Assistant configuration workspace integrating:
- **Wearables Integration Platform** (Omi.me MCP Server)
- **Home AI Automation** (AI-powered automations)
- **Home Environment Integration** (Android/Proxmox)

## Structure

```
home-assistant-config/
├── mcp-config/              # MCP Server configurations
│   ├── omi-mcp-config.yaml  # Omi.me MCP server config
│   ├── ha-mcp-setup.md      # Home Assistant MCP setup
│   └── proxmox-ha-mcp.yaml  # Proxmox Home Assistant bridge
├── services/                # Service configurations
│   ├── mosquitto.yaml       # MQTT broker config
│   ├── influxdb.yaml        # Time-series database
│   ├── grafana.yaml         # Monitoring dashboards
│   └── agentstack.yaml      # Bee AI AgentStack config
├── automations/             # Home Assistant automations
│   ├── wearables.yaml       # Omi wearables triggers
│   ├── ai-agents.yaml       # AI-powered automations
│   └── schedules.yaml       # Scheduled automations
├── templates/               # YAML configuration templates
│   ├── integration.yaml.tmpl
│   └── service.yaml.tmpl
└── README.md                # This file
```

## Quick Start

### 1. Clone Existing Repositories
```bash
git clone https://github.com/bryansrevision/wearables-integration-platform.git wearables
git clone https://github.com/bryansrevision/HOME-AI-AUTOMATION.git automation
```

### 2. Configure MCP Servers

Set up environment variables in `.env`:
```bash
# OMI MCP Configuration
OMI_MCP_API_TOKEN=your_token_from_omi_app
OMI_MCP_BASE_URL=https://api.omi.me/v1
OMI_MCP_SERVER_URL=https://api.omi.me/v1/mcp/sse

# Proxmox Integration
PROXMOX_HOST=192.168.1.185
PROXMOX_PORT=8006
PROXMOX_TOKEN=your_api_token

# Home Assistant
HOME_ASSISTANT_URL=http://homeassistant:8123
HOME_ASSISTANT_TOKEN=your_long_lived_token

# GitHub MCP
GITHUB_TOKEN=your_github_token
```

### 3. Initialize Services
```bash
# Start Docker services
docker-compose -f wearables/docker-compose.yml up -d

# Initialize Home Assistant configuration
./scripts/init-ha-config.sh
```

### 4. Connect to Home Assistant
```bash
# Test MCP connection
python scripts/test-mcp-connection.py

# Verify automations loaded
./scripts/verify-automations.sh
```

## Configuration Highlights

### Omi.me MCP Integration
- **Real-time event streaming** from Omi Dev Kit 2 wearables
- **Memory processing** using Bee AI AgentStack
- **Automatic triggers** for Home Assistant automations
- **Event types**: memory_created, conversation_ended, transcript_received

### AI-Powered Automations
- **Memory Analyzer**: Extracts action items from conversations
- **Health Monitor**: Tracks wellness from wearable data
- **Task Manager**: Creates automations from detected tasks
- **Sentiment Detection**: Triggers automations based on mood

### Proxmox Integration
- **VM Management**: Automated resource allocation
- **Monitoring**: Real-time metrics collection
- **Backup Integration**: Scheduled snapshots and backups
- **Network Management**: Virtual network configuration

## Services Architecture

```
┌─────────────────┐
│  Omi Wearable   │
│    Dev Kit 2    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Omi.me MCP Server (api.omi.me) │
│  SSE Event Streaming            │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Webhook Service (FastAPI)      │
│  - OMI Memory Processing        │
│  - MQTT Publishing              │
│  - InfluxDB Storage             │
└────────┬────────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────────────┐
│ MQTT   │ │  InfluxDB        │
│        │ │  Time-Series DB  │
└────┬───┘ └──────────┬───────┘
     │                │
     └────────┬───────┘
              ▼
      ┌──────────────────────┐
      │  Home Assistant      │
      │  Automations Engine  │
      └──────────────────────┘
              ▼
      ┌──────────────────────┐
      │  Smart Home Devices  │
      │  (Lights, Locks, etc)│
      └──────────────────────┘
```

## Environment Variables

See `.env.example` for complete list. Key variables:

- `OMI_MCP_API_TOKEN`: Authentication for Omi.me MCP Server
- `PROXMOX_TOKEN`: Proxmox API authentication
- `HOME_ASSISTANT_TOKEN`: Long-lived Home Assistant token
- `WEBHOOK_SECRET`: Webhook security token
- `MQTT_BROKER`: MQTT broker hostname
- `INFLUXDB_DB`: InfluxDB database name

## Data Flow

### From Wearable to Automation
1. Omi device records memory/conversation
2. MCP server sends SSE event
3. Webhook service processes event
4. AI Agent analyzes content
5. Action items/insights extracted
6. MQTT topic published
7. Home Assistant receives update
8. Automation triggered

### From Proxmox to Home Assistant
1. Proxmox resource metrics collected
2. InfluxDB stores time-series data
3. Grafana displays dashboards
4. Home Assistant queries via REST API
5. Conditional automations triggered

## Monitoring & Debugging

### View Logs
```bash
# Webhook service logs
docker logs omi_webhook

# Home Assistant logs
docker logs homeassistant

# MQTT traffic
mosquitto_sub -v -t '#'
```

### Check Health
```bash
# Test MCP connection
./scripts/test-mcp-connection.py

# Verify MQTT publishing
./scripts/verify-mqtt.sh

# Check Home Assistant automations
./scripts/verify-automations.sh

# Proxmox connectivity
curl -s https://192.168.1.185:8006/api2/json/version -k
```

## Troubleshooting

### MCP Connection Issues
- Verify `OMI_MCP_API_TOKEN` is valid (from Omi app: Settings → Developer → MCP)
- Check firewall allows HTTPS to api.omi.me
- Review webhook service logs for SSE connection errors
- Ensure environment variables loaded: `env | grep OMI_`

### MQTT Not Publishing
- Verify Mosquitto container running: `docker ps | grep mosquitto`
- Check Mosquitto logs: `docker logs mosquitto`
- Test manual publish: `mosquitto_pub -t test/topic -m "test message"`

### Home Assistant Not Triggering
- Verify automations loaded: Home Assistant UI → Settings → Automations
- Check MQTT integration configured
- Review Home Assistant logs for errors
- Test MQTT trigger manually

## Security Best Practices

⚠️ **Never commit sensitive data**
- Keep `.env` in `.gitignore` (already configured)
- Use secrets manager for tokens (Bitwarden integration available)
- Rotate tokens regularly (90-day rotation recommended)
- Use strong webhook secrets: `python -c "import secrets; print(secrets.token_urlsafe(48))"`

## Resources

- [Omi.me MCP Documentation](https://docs.omi.me/mcp)
- [Home Assistant Documentation](https://www.home-assistant.io/docs/)
- [MQTT Protocol Guide](https://mqtt.org/)
- [Proxmox API Docs](https://pve.proxmox.com/pve-docs/api-viewer/)

## Support

For issues or questions:
1. Check troubleshooting section
2. Review service logs
3. Create issue on GitHub repository
4. Consult Home Assistant community forums
