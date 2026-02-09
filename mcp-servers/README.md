# MCP Servers

This directory contains the Model Context Protocol (MCP) integration for Home Assistant.

## Overview

The MCP integration provides real-time bidirectional synchronization between this repository and a live Home Assistant server at `http://192.168.1.134:8123`.

## Key Files

### Active Configuration
- **home-assistant-live.yaml** - **PRIMARY** MCP server configuration for live Home Assistant integration

### Integration Scripts
- **ha_mcp_client.py** - Python MCP client library (391 lines)
- **init_mcp_integration.py** - MCP integration initialization script
- **mcp-quick-connect.py** - Quick connection testing utility

### Documentation
- **MCP-LIVE-SERVER-INTEGRATION.md** - Complete MCP integration guide and documentation
- **ha-mcp-setup.md** - MCP setup instructions

### Status & Monitoring
- **.integration-status.json** - Current integration status (auto-generated)

## Other Configuration Files

### Legacy/Alternative Configs
These configurations serve specific purposes but are not the primary live config:

- **ha-mcp-config.yaml** - Legacy MCP configuration (401 lines)
- **omi-mcp-config.yaml** - Omi wearables MCP configuration (462 lines)
- **proxmox-ha-mcp.yaml** - Proxmox-specific MCP bridge (36 lines)
- **proxmox-mcp-config.yaml** - Proxmox MCP configuration (14 lines)

**Note:** `home-assistant-live.yaml` is the active configuration used by the live server integration.

## Quick Start

### Initialize MCP Integration
```bash
python mcp-servers/init_mcp_integration.py
```

### Test Connection
```bash
python mcp-servers/mcp-quick-connect.py
```

### Check Status
```bash
cat mcp-servers/.integration-status.json
```

## Documentation

For complete setup and usage instructions, see:
- [MCP-LIVE-SERVER-INTEGRATION.md](MCP-LIVE-SERVER-INTEGRATION.md) - Full integration guide
- [ha-mcp-setup.md](ha-mcp-setup.md) - Setup instructions

## Related

- **Server Sync Tool**: [../scripts/align-server.py](../scripts/align-server.py)
- **Environment Config**: [../config/.env](../config/.env)
- **Core HA Config**: [../core/configuration.yaml](../core/configuration.yaml)

## Connection Details

| Parameter | Value |
|-----------|-------|
| **Server** | http://192.168.1.134:8123 |
| **Protocol** | HTTP with Bearer Token |
| **Auth** | HOME_ASSISTANT_TOKEN environment variable |
| **Entities** | 307 entities across 21 domains |
| **Sync** | Bidirectional (pull/push automations, state) |

## See Also

- Main README: [../README.md](../README.md)
- Quick Start: [../QUICKSTART.md](../QUICKSTART.md)
- Documentation Index: [../DOCUMENTATION-INDEX.md](../DOCUMENTATION-INDEX.md)
