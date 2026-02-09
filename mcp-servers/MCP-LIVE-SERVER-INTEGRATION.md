# 🌐 Home Assistant Live Server MCP Integration

**Last Updated:** January 31, 2026  
**Status:** ✅ Ready for Deployment



## 📋 Overview

This guide implements **bidirectional Model Context Protocol (MCP) integration**
between the repository and the live Home Assistant server at
`192.168.1.134:8123`.

The integration provides:
- ✅ Real-time state synchronization
- ✅ Automated configuration alignment
- ✅ Service control and automation management
- ✅ Event streaming and monitoring
- ✅ Repository ↔ Server bidirectional sync



## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install required packages
pip install aiohttp pyyaml python-dotenv

# Set environment variable
export HOME_ASSISTANT_TOKEN="your_long_lived_token_here"
```

### 2. Initialize MCP Integration

```bash
# From repository root
cd home-assistant-unified

# Run initialization
python mcp-servers/init_mcp_integration.py

# Expected output:
# ✅ Connected to Home Assistant
# ✅ Credentials verified
# ✅ Configuration verified: 263 entities
# ✅ MCP Integration initialized successfully
```

### 3. Diagnose Server Alignment

```bash
# Check alignment between repo and server
python scripts/align-server.py diagnose

# Output: Detailed diagnostic report with issues and recommendations
```

### 4. Synchronize Server

```bash
# Pull latest automations from server to repo
python scripts/align-server.py sync-pull --type automations

# Push repo automations to server
python scripts/align-server.py sync-push --type automations

# Full bidirectional sync
python scripts/align-server.py sync-push --type all
```



## 📁 Key Files

| File | Purpose |
|------|---------|
| `mcp-servers/home-assistant-live.yaml` | MCP server configuration with all parameters |
| `mcp-servers/ha_mcp_client.py` | Python MCP client library |
| `scripts/align-server.py` | Server alignment and synchronization tool |
| `mcp-servers/init_mcp_integration.py` | MCP integration initialization script |



## 🔧 Configuration

### Environment Variables

Set these in `config/.env`:

```bash
# Home Assistant Server
HOME_ASSISTANT_TOKEN=eyJhbGci...  # Long-lived token from HA
HOME_ASSISTANT_URL=http://192.168.1.134:8123
HA_HOST=192.168.1.134
HA_PORT=8123
HA_PROTOCOL=http

# MQTT Broker (for event routing)
MQTT_BROKER=localhost
MQTT_PORT=1883

# InfluxDB (for metrics)
INFLUXDB_HOST=localhost
INFLUXDB_PORT=8086
INFLUXDB_DB=omi_metrics

# Proxmox Integration
PROXMOX_HOST=192.168.1.185
PROXMOX_PORT=8006
PROXMOX_USER=root@pam
PROXMOX_PASSWORD=your_password
```

### MCP Configuration (`home-assistant-live.yaml`)

Key sections:

```yaml
mcp_servers:
  home_assistant_live:
    connection:
      host: '192.168.1.134'
      port: 8123
      
    entities:
      sync_interval: 5  # seconds
      
    events:
      routing:
        mqtt: true
        influxdb: true
        webhook: true
    
    automations:
      sync_direction: 'bidirectional'
      conflict_strategy: 'repo_wins'
```



## 📊 Architecture

```
┌─────────────────────────────────────────────────┐
│         Home Assistant Server (Live)            │
│         192.168.1.134:8123                      │
│                                                 │
│  • 263+ Entities                                │
│  • Automations                                  │
│  • Scenes & Scripts                             │
│  • Integrations                                 │
└────────────────────┬────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │  MCP Bridge Layer    │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼──────┐         ┌─────▼─────┐
    │  MQTT     │         │ InfluxDB  │
    │  Broker   │         │  Metrics  │
    └──────────┘         └──────────┘
         │
    ┌────▼─────────────────────────────┐
    │   Repository                      │
    │   home-assistant-unified/         │
    │                                   │
    │  • automations/                   │
    │  • core/                          │
    │  • mcp-servers/                   │
    │  • scripts/                       │
    └──────────────────────────────────┘
```



## 🔄 Sync Modes

### Pull (Server → Repository)

Brings latest configurations from server to repo:

```bash
python scripts/align-server.py sync-pull --type all
```

**Use when:**
- Server has manual configuration changes
- You want to capture current server state
- Troubleshooting alignment issues

### Push (Repository → Server)

Pushes repository configurations to server:

```bash
python scripts/align-server.py sync-push --type automations
```

**Use when:**
- You've made changes in the repo
- You want to deploy new automations
- After code review and testing

### Bidirectional

Synchronizes in both directions (server changes win on conflicts):

```bash
python scripts/align-server.py sync-pull --type all
# Make changes
python scripts/align-server.py sync-push --type automations
```



## 📊 Monitoring & Diagnostics

### Health Check

```bash
python scripts/align-server.py health-check
```

Output:
```json
{
  "timestamp": "2026-01-31T10:30:00",
  "server": {
    "connected": true,
    "entities": 263,
    "automations": 42
  }
}
```

### Detailed Diagnosis

```bash
python scripts/align-server.py diagnose --verbose
```

Returns:
- ✅ Configuration alignment status
- ⚠️ Issues and warnings
- 💡 Recommendations for resolution
- 📊 Entity and automation counts

### View Sync Logs

```bash
tail -f logs/ha-sync.log
```



## 🔌 Python API Usage

### Basic Connection

```python
from mcp_servers.ha_mcp_client import HomeAssistantMCPClient, MCPConfig

config = MCPConfig.from_env()
async with HomeAssistantMCPClient(config) as client:
    # Get all states
    states = await client.get_all_states()
    
    # Call service
    await client.call_service('light', 'turn_on', 
                             entity_id='light.living_room')
    
    # Export state
    await client.export_state()
```

### Automation Sync

```python
from mcp_servers.ha_mcp_client import SyncDirection

async with HomeAssistantMCPClient(config) as client:
    # Pull automations from server
    await client.sync_automations(SyncDirection.SERVER_TO_REPO)
    
    # Push automations to server
    await client.sync_automations(SyncDirection.REPO_TO_SERVER)
```

### Event Monitoring

```python
async def on_event(event):
    print(f"Event: {event}")

client.register_event_callback(on_event)
await client.listen_for_events()
```



## 🛠️ Troubleshooting

### Connection Failed

```bash
# Check if server is running
curl -i http://192.168.1.134:8123/api/

# Verify token is valid
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://192.168.1.134:8123/api/
```

**Solutions:**
1. Verify Home Assistant is running
2. Check network connectivity
3. Validate token is correct and not expired
4. Check firewall rules

### Token Issues

```bash
# Generate new long-lived token in Home Assistant:
# Settings → Developer Tools → Create Long-Lived Access Token

# Update environment
export HOME_ASSISTANT_TOKEN="your_new_token"
```

### Sync Conflicts

When conflicts occur, the system uses the configured strategy:

```yaml
# In home-assistant-live.yaml
automations:
  conflict_strategy: 'repo_wins'  # server_wins, repo_wins, or manual
```

To resolve manually:

1. **Pull and review:**
   ```bash
   python scripts/align-server.py sync-pull --type automations
   git diff
   ```

2. **Resolve conflicts** in repository

3. **Push resolved version:**
   ```bash
   python scripts/align-server.py sync-push --type automations
   ```

### MCP Integration Fails

1. Check MCP server logs:
   ```bash
   tail -f logs/mcp-server.log
   ```

2. Verify configuration:
   ```bash
   python mcp-servers/init_mcp_integration.py --verbose
   ```

3. Review integration status:
   ```bash
   cat mcp-servers/.integration-status.json
   ```



## 📈 Performance Tuning

### Sync Interval

Adjust in `home-assistant-live.yaml`:

```yaml
entities:
  sync_interval: 5  # Lower = more frequent, higher = less load
```

### Event Throttling

```yaml
connection_pool:
  request_queue:
    max_size: 1000  # Adjust based on load
```

### Retention Policies

```yaml
state_export:
  retention_days: 30  # Keep 30 days of exports
```



## 🔐 Security

### Token Management

- ✅ Token stored in `config/.env` (not in git)
- ✅ Never commit `.env` to repository
- ✅ Rotate tokens every 90 days
- ✅ Use different tokens for different environments

### Network Security

For production deployment:

```yaml
security:
  ssl:
    enabled: true
    verify_certificate: true
  rate_limit:
    enabled: true
    requests_per_second: 10
  ip_whitelist:
    enabled: true
    ips:
      - '192.168.1.0/24'
```



## 📝 Common Tasks

### Deploy New Automation

```bash
# 1. Create automation in repo
cat > automations/my-automation.yaml << EOF
alias: My New Automation
trigger:
  platform: time
  at: "10:00:00"
action:
  service: light.turn_on
  entity_id: light.living_room
EOF

# 2. Sync to server
python scripts/align-server.py sync-push --type automations

# 3. Verify
python scripts/align-server.py health-check

# 4. Commit to git
git add automations/
git commit -m "Add: My New Automation"
```

### Capture Server State

```bash
# Export current server configuration
python scripts/align-server.py sync-pull --type all

# Backup to git
git add -A
git commit -m "Backup: Server state export"
```

### Emergency Restore

```bash
# Restore from latest backup
git checkout HEAD -- automations/ core/ integrations/

# Push to server
python scripts/align-server.py sync-push --type all
```



## 🎯 Next Steps

1. ✅ **Run initialization:**
   ```bash
   python mcp-servers/init_mcp_integration.py
   ```

2. ✅ **Test connection:**
   ```bash
   python scripts/align-server.py health-check
   ```

3. ✅ **Perform initial sync:**
   ```bash
   python scripts/align-server.py sync-pull --type all
   ```

4. ✅ **Commit baseline:**
   ```bash
   git add -A
   git commit -m "Initial: MCP integration setup"
   git push origin master
   ```



## 📞 Support

For issues or questions:

1. Check logs: `logs/ha-sync.log`
2. Run diagnosis: `python scripts/align-server.py diagnose --verbose`
3. Review MCP configuration: `mcp-servers/home-assistant-live.yaml`
4. Check integration status: `mcp-servers/.integration-status.json`



**🎉 MCP Integration Ready for Production Deployment!**
