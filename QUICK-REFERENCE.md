# 🚀 Home Assistant MCP Integration - Quick Reference Card

**Print or bookmark this page for easy access to common commands**



## 📍 Installation & Setup

### 1. Configure Credentials
```bash
# Edit environment file
notepad config/.env

# Add to file:
HOME_ASSISTANT_TOKEN=eyJhbGci...  # Get from HA settings
HA_HOST=192.168.1.134
HA_PORT=8123
```

**Where to get token:**
1. Go to http://192.168.1.134:8123
2. Profile (bottom left) → Long-Lived Access Tokens
3. Create New Token → Name it "MCP Integration"
4. Copy token to HOME_ASSISTANT_TOKEN

### 2. Run Setup (Windows)
```powershell
# PowerShell
.\Initialize-MCPIntegration.ps1 -FullSync

# Output should show:
# ✅ Python found
# ✅ Repository structure verified
# ✅ Home Assistant token configured
# ✅ Dependencies installed
# ✅ MCP integration initialized successfully
```

### 3. Verify Setup
```bash
# Test connection
python scripts/align-server.py health-check

# Should show:
# "connected": true
# "entities": 263
# "automations": 42
```



## 🔄 Common Operations

### Pull Changes from Server
```bash
# Get latest automations from server
python scripts/align-server.py sync-pull --type automations

# Get all configurations
python scripts/align-server.py sync-pull --type all

# Get only state snapshot
python scripts/align-server.py sync-pull --type states
```

### Push Changes to Server
```bash
# Deploy your automations
python scripts/align-server.py sync-push --type automations

# Deploy all changes
python scripts/align-server.py sync-push --type all

# Deploy configuration
python scripts/align-server.py sync-push --type config
```

### Check Status
```bash
# Quick health check
python scripts/align-server.py health-check

# Detailed diagnosis
python scripts/align-server.py diagnose --verbose

# View integration status
cat mcp-servers/.integration-status.json
```



## 📝 Workflow Examples

### Deploy New Automation

```bash
# 1. Create automation file
cat > automations/my-automation.yaml << 'EOF'
alias: My Automation
trigger:
  platform: time
  at: "10:00:00"
action:
  service: light.turn_on
  entity_id: light.living_room
EOF

# 2. Deploy to server
python scripts/align-server.py sync-push --type automations

# 3. Verify
python scripts/align-server.py health-check

# 4. Commit to git
git add automations/
git commit -m "Add: My Automation"
git push
```

### Daily Maintenance

```bash
# Morning: Get latest
python scripts/align-server.py sync-pull --type automations

# During day: Make changes
# Edit automations, configs, etc.

# Evening: Deploy changes
python scripts/align-server.py sync-push --type automations

# Commit
git add -A
git commit -m "Update: Daily changes $(date +%Y-%m-%d)"
git push
```

### Troubleshoot Problem

```bash
# 1. Check status
python scripts/align-server.py health-check

# 2. Run diagnostics
python scripts/align-server.py diagnose --verbose

# 3. View logs
tail -50 logs/ha-sync.log

# 4. Review recent changes
git log --oneline -10

# 5. If needed, revert changes
git revert HEAD
python scripts/align-server.py sync-push --type all
```



## 🔧 Configuration Files

### .env (Environment Variables)
```
Location: config/.env
Purpose: Credentials and connection settings
Key vars: HOME_ASSISTANT_TOKEN, HA_HOST, HA_PORT, MQTT_*, INFLUXDB_*
```

### home-assistant-live.yaml (MCP Configuration)
```
Location: mcp-servers/home-assistant-live.yaml
Purpose: MCP connection and sync settings
Sections: connection, entities, events, automations, health_check
```

### ha_mcp_client.py (MCP Client Library)
```
Location: mcp-servers/ha_mcp_client.py
Purpose: Python async client for Home Assistant
Classes: MCPConfig, EntityState, HomeAssistantMCPClient
```



## 📊 Directory Structure

```
home-assistant-unified/
├── config/
│   └── .env                    # Your credentials (UPDATE THIS)
├── mcp-servers/
│   ├── home-assistant-live.yaml
│   ├── ha_mcp_client.py
│   ├── init_mcp_integration.py
│   ├── MCP-LIVE-SERVER-INTEGRATION.md
│   └── .integration-status.json
├── scripts/
│   └── align-server.py         # Main sync tool
├── automations/                # Your automations
├── core/                       # Core configuration
├── logs/                       # Log files (auto-created)
└── backups/                    # Backup exports (auto-created)
```



## 🆘 Troubleshooting Quick Fixes

### Connection Failed
```bash
# 1. Test server is running
curl http://192.168.1.134:8123

# 2. Test token is valid
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://192.168.1.134:8123/api/

# 3. Check firewall
# Windows: Check if port 8123 is open
# Router: Check port forwarding if needed
```

### Token Expired/Invalid
```bash
# 1. Generate new token in Home Assistant settings
# 2. Update config/.env:
HOME_ASSISTANT_TOKEN=your_new_token_here

# 3. Reinitialize
python mcp-servers/init_mcp_integration.py

# 4. Test
python scripts/align-server.py health-check
```

### Sync Conflicts
```bash
# 1. See what differs
git diff automations/

# 2. Review server state
python scripts/align-server.py sync-pull --type automations
git diff

# 3. Resolve manually or use strategy
# Edit conflicts in automations/
# Then push:
python scripts/align-server.py sync-push --type automations
```

### MQTT Not Working
```bash
# Check if broker is running
docker ps | grep mqtt

# If not running
docker-compose up -d ha-mqtt

# Test connection
mosquitto_sub -h localhost -t "test"

# In another terminal
mosquitto_pub -h localhost -t "test" -m "hello"
```



## 📚 Documentation Links

| Document | Use When |
|----------|----------|
| [MCP Integration Guide](./mcp-servers/MCP-LIVE-SERVER-INTEGRATION.md) | Need detailed setup/usage info |
| [Server Update Guide](./SERVER-UPDATE.md) | Planning deployment |
| [Deployment Summary](./DEPLOYMENT_COMPLETE.md) | Want complete overview |
| [README](./README.md) | New to the project |
| [SYNC_GUIDE](./SYNC_GUIDE.md) | Need to sync with source repos |



## ⚡ Power User Tips

### Create Alias (Linux/Mac)
```bash
# Add to ~/.bashrc or ~/.zshrc
alias ha-sync-pull='python scripts/align-server.py sync-pull --type all'
alias ha-sync-push='python scripts/align-server.py sync-push --type automations'
alias ha-health='python scripts/align-server.py health-check'
alias ha-diagnose='python scripts/align-server.py diagnose --verbose'

# Then use:
ha-health
ha-diagnose
ha-sync-pull
```

### Create Batch Files (Windows)
```batch
# Create ha-sync-pull.bat
@echo off
python scripts\align-server.py sync-pull --type all

# Create ha-health.bat
@echo off
python scripts\align-server.py health-check

# Create ha-diagnose.bat
@echo off
python scripts\align-server.py diagnose --verbose
```

### Watch Logs in Real-Time
```bash
# Linux/Mac
tail -f logs/ha-sync.log

# PowerShell
Get-Content logs/ha-sync.log -Wait -Tail 50
```

### Backup Everything
```bash
# Export full state
python scripts/align-server.py sync-pull --type states

# Commit and push
git add backups/
git commit -m "Backup: Full state $(date +%Y-%m-%d-%H%M%S)"
git push
```



## 🎯 Success Indicators

You know it's working when:

✅ `health-check` shows `"connected": true`  
✅ Entity count matches: `"entities": 263` (or your count)  
✅ Sync operations complete without errors  
✅ Git commits with automation changes  
✅ No errors in `logs/ha-sync.log`  
✅ Integration status shows no issues  



## 📞 When Something Goes Wrong

### Step 1: Gather Information
```bash
# Health check
python scripts/align-server.py health-check

# Full diagnosis
python scripts/align-server.py diagnose --verbose

# Show logs
tail -100 logs/ha-sync.log > debug.txt
cat mcp-servers/.integration-status.json > status.txt
```

### Step 2: Check Documentation
- Read:
  [MCP-LIVE-SERVER-INTEGRATION.md](./mcp-servers/MCP-LIVE-SERVER-INTEGRATION.md)
- Section: "🛠️ Troubleshooting"

### Step 3: Common Fixes
1. Token issue → Regenerate token
2. Network issue → Check firewall/connectivity
3. Config issue → Review .env and YAML files
4. Data issue → Perform fresh sync

### Step 4: Emergency Restore
```bash
# If everything is broken:
git revert HEAD
python scripts/align-server.py sync-push --type all
python scripts/align-server.py health-check
```



## 📋 Checklist for New Users

- [ ] Read README.md
- [ ] Generate Home Assistant token
- [ ] Update config/.env
- [ ] Run Initialize-MCPIntegration.ps1
- [ ] Verify with health-check
- [ ] Do first sync-pull
- [ ] Review changes with git diff
- [ ] Commit baseline
- [ ] Read MCP Integration Guide
- [ ] Test with sync-push
- [ ] Set up monitoring
- [ ] Bookmark this card



## 🎉 Ready to Go!

You now have everything needed to manage Home Assistant from code. Remember:

✅ **Always pull before you push**  
✅ **Review changes before committing**  
✅ **Keep backups of critical automations**  
✅ **Monitor logs for issues**  
✅ **Rotate tokens every 90 days**  

Happy automating! 🤖
