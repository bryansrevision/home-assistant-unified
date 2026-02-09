# 📁 Home Assistant Unified - Repository Structure

**Last Updated**: February 6, 2026

This document provides a comprehensive overview of the repository organization.

## 🗂️ Root Directory Structure

```
home-assistant-unified/
├── 📄 README.md                          # Main project overview
├── 📄 QUICKSTART.md                      # 5-minute setup guide
├── 📄 QUICK-REFERENCE.md                 # Quick command reference
├── 📄 DOCUMENTATION-INDEX.md             # Complete documentation index
├── 📄 CONTRIBUTING.md                    # Contribution guidelines
├── 📄 LICENSE                            # MIT License
├── 📄 .env.example                       # Environment template
├── 🔧 Initialize-MCPIntegration.ps1      # PowerShell MCP setup script
│
├── 📂 core/                              # Home Assistant core config
│   ├── configuration.yaml                # Main HA configuration
│   ├── automations.yaml                  # Automation imports
│   ├── scripts.yaml                      # Script definitions
│   └── scenes.yaml                       # Scene configurations
│
├── 📂 automations/                       # Automation definitions (28 files)
│   ├── automation_welcome_home.yaml
│   ├── automation_away_mode.yaml
│   └── ...                               # Synced from HA server
│
├── 📂 mcp-servers/                       # MCP integration
│   ├── ha_mcp_client.py                  # MCP Python client (391 lines)
│   ├── init_mcp_integration.py           # Integration initializer
│   ├── home-assistant-live.yaml          # MCP configuration
│   ├── MCP-LIVE-SERVER-INTEGRATION.md    # MCP documentation
│   └── .integration-status.json          # Current MCP status
│
├── 📂 scripts/                           # Utility scripts
│   ├── align-server.py                   # Server sync tool
│   ├── mcp-quick-connect.py              # Quick MCP test
│   ├── setup/                            # Setup scripts
│   ├── vm101/                            # VM 101 backup system scripts
│   ├── debug_env.py                      # Environment debugger
│   └── test_ha_connection.py             # Connection tester
│
├── 📂 docs/                              # Detailed documentation
│   ├── COMPREHENSIVE-DEPLOYMENT-GUIDE.md # Complete deployment guide
│   ├── COPILOT-DEPLOYMENT-INSTRUCTIONS.md# GitHub Copilot deployment
│   ├── SERVER-UPDATE.md                  # Server update procedures
│   ├── SYNC_GUIDE.md                     # Repository sync guide
│   ├── operations/                       # Operational procedures
│   │   ├── failover-procedure.md         # VM failover instructions
│   │   └── vm101-backup-system.md        # Backup system documentation
│   └── *.md                              # Additional guides
│
├── 📂 integrations/                      # Integration modules
│   ├── android/                          # Android device integration
│   ├── proxmox/                          # Proxmox VE management
│   ├── wearables/                        # Omi wearables integration
│   └── mqtt/                             # MQTT broker configs
│
├── 📂 automation-engine/                 # AI automation engine
│   ├── src/                              # Python/Flask application
│   ├── config/                           # Engine configuration
│   └── requirements.txt                  # Python dependencies
│
├── 📂 services/                          # Docker services
│   ├── docker-compose.yml                # Service orchestration
│   └── ...                               # Service configurations
│
├── 📂 config/                            # Configuration files
│   ├── .env                              # Environment variables (gitignored)
│   ├── .env.example                      # Environment template
│   ├── vm101/                            # VM 101 backup configuration
│   └── *.json                            # Configuration files
│
├── 📂 dashboards/                        # Grafana dashboards
│   └── *.json                            # Dashboard definitions
│
├── 📂 backups/                           # Backups and exports
│   ├── state-exports/                    # HA state snapshots
│   │   ├── baseline.json                 # Baseline state export
│   │   └── state-2026-02-06*.json        # Timestamped exports
│   └── configurations/                   # Config backups
│
├── 📂 logs/                              # Application logs
│   └── *.log                             # Log files (gitignored)
│
└── 📂 archive/                           # Historical documentation
    ├── README.md                         # Archive index
    └── *.md                              # Old deployment reports
```

## 🎯 Key Files & Their Purpose

### Essential Documentation (Root)

| File | Purpose | Audience |
|------|---------|----------|
| `README.md` | Project overview, features, quick start | All users |
| `QUICKSTART.md` | 5-minute setup guide | New users |
| `QUICK-REFERENCE.md` | Command cheat sheet | Active users |
| `DOCUMENTATION-INDEX.md` | Complete documentation map | All users |
| `CONTRIBUTING.md` | Contribution guidelines | Contributors |

### MCP Integration

| File | Purpose | Type |
|------|---------|------|
| `ha_mcp_client.py` | Python MCP client library | Code |
| `init_mcp_integration.py` | MCP initialization script | Script |
| `home-assistant-live.yaml` | MCP server configuration | Config |
| `MCP-LIVE-SERVER-INTEGRATION.md` | MCP documentation | Docs |

### Scripts & Tools

| File | Purpose | Usage |
|------|---------|-------|
| `align-server.py` | Sync with HA server | `python scripts/align-server.py sync-pull` |
| `mcp-quick-connect.py` | Quick MCP connection test | `python scripts/mcp-quick-connect.py` |
| `Initialize-MCPIntegration.ps1` | PowerShell setup | `.\Initialize-MCPIntegration.ps1` |

### Configuration

| File | Purpose | Location |
|------|---------|----------|
| `.env` | Environment variables | `config/.env` (gitignored) |
| `.env.example` | Environment template | Root / config/ |
| `configuration.yaml` | Main HA config | `core/configuration.yaml` |

## 📊 Directory Purposes

### `/automations/` - Automation Definitions

- **Count**: 29 YAML files
- **Synced**: Yes (bidirectional with HA server)
- **Categories**:
  - Presence detection (welcome_home, away_mode)
  - Energy management (peak hours, device scheduling)
  - Entertainment (movie mode, music control)
  - Security (motion detection while away)
  - Routines (morning briefing, nightly report)

### `/mcp-servers/` - MCP Integration

- **Purpose**: Model Context Protocol server integration
- **Key Component**: Live bidirectional sync with HA server
- **Status**: Initialized and connected (192.168.1.134:8123)
- **Entities**: 307 entities across 21 domains

### `/scripts/` - Automation & Utilities

- **Setup scripts**: Initial configuration and deployment
- **Sync tools**: `align-server.py` for server synchronization
- **Debug tools**: Environment debugging and connection testing
- **Health checks**: Status verification and diagnostics
- **VM 101 scripts**: High-availability backup system management

### `/docs/` - Detailed Guides

- **Deployment**: Comprehensive deployment procedures
- **Integration**: MCP, Proxmox, Android, wearables setup
- **Operations**: VM 101 backup system, failover procedures, sync procedures, troubleshooting, maintenance

### `/integrations/` - Platform Integrations

- **android/**: Native Android app and device configs
- **proxmox/**: VM/LXC management scripts
- **wearables/**: Omi Device Kit 2 integration
- **mqtt/**: MQTT broker configurations

### `/automation-engine/` - AI Engine

- **Technology**: Python/Flask application
- **Purpose**: AI-powered automation processing
- **Features**: Natural language control, scene management
- **Providers**: OpenAI, Gemini, Grok support

### `/backups/` - State & Configuration Backups

- **State Exports**: Timestamped HA state snapshots
- **Baseline**: Reference state for comparison
- **Frequency**: On-demand and automated
- **Format**: JSON with full entity states

### `/archive/` - Historical Records

- **Purpose**: Keep historical documentation for reference
- **Contents**: Old deployment reports, integration notes
- **Archived**: February 6, 2026
- **Reason**: Documentation consolidation

## 🔄 File Organization Principles

### 1. **Root Directory** - Essential Only

- Keep only essential documentation (README, QUICKSTART, etc.)
- Move detailed guides to `docs/`
- Archive historical documents to `archive/`

### 2. **Configuration Separation**

- Environment variables: `config/.env` (gitignored)
- HA core config: `core/` directory
- Service configs: `services/` directory

### 3. **Logical Grouping**

- Related files in dedicated directories
- Clear naming conventions (automation_*, script_*, etc.)
- Consistent file extensions

### 4. **Version Control**

- `.gitignore` for sensitive files (.env, logs, **pycache**)
- Track configuration templates (.env.example)
- Commit automation syncs regularly

## 📝 File Naming Conventions

### Automations

Format: `automation_[category]_[name].yaml`

- Examples:
  - `automation_presence_welcome_home.yaml`
  - `automation_energy_peak_hours_notification.yaml`
  - `automation_entertainment_movie_mode_on.yaml`

### Scripts

Format: `[purpose]-[action].py` or `[purpose]_[action].py`

- Examples:
  - `align-server.py`
  - `mcp-quick-connect.py`
  - `init_mcp_integration.py`

### Documentation

Format: `[TOPIC]-[TYPE].md` or `[TOPIC].md`

- Examples:
  - `MCP-LIVE-SERVER-INTEGRATION.md`
  - `COMPREHENSIVE-DEPLOYMENT-GUIDE.md`
  - `REPOSITORY-STRUCTURE.md` (this file)

### Configuration

Format: `[service]-[type].[ext]`

- Examples:
  - `home-assistant-live.yaml`
  - `.env.example`
  - `docker-compose.yml`

## 🔍 Finding Files

### By Purpose

**Want to deploy?** → `docs/COMPREHENSIVE-DEPLOYMENT-GUIDE.md`

**Want to sync with server?** → `scripts/align-server.py` or
`QUICK-REFERENCE.md`

**Want to understand MCP?** → `mcp-servers/MCP-LIVE-SERVER-INTEGRATION.md`

**Want to add automation?** → `automations/` (add YAML, then sync to server)

**Want to configure integrations?** → `integrations/[platform]/` directories

**Want historical context?** → `archive/README.md`

### By Type

| Type | Location |
|------|----------|
| Python scripts | `scripts/`, `mcp-servers/`, `automation-engine/src/` |
| Configuration | `config/`, `core/`, `services/` |
| Documentation | Root (essential), `docs/` (detailed), `archive/` (historical) |
| Automations | `automations/` |
| Dashboards | `dashboards/` |
| Backups | `backups/` |

## 🚀 Navigation Quick Links

**Getting Started:**

- [Main README](README.md) - Start here
- [Quick Start Guide](QUICKSTART.md) - 5-minute setup
- [Quick Reference](QUICK-REFERENCE.md) - Command cheat sheet

**Detailed Guides:**

- [Deployment Guide](docs/COMPREHENSIVE-DEPLOYMENT-GUIDE.md)
- [MCP Integration](mcp-servers/MCP-LIVE-SERVER-INTEGRATION.md)
- [Sync Guide](docs/SYNC_GUIDE.md)
- [Server Updates](docs/SERVER-UPDATE.md)

**Development:**

- [Contributing Guidelines](CONTRIBUTING.md)
- [MCP Client Source](mcp-servers/ha_mcp_client.py)
- [Automation Engine](automation-engine/)

**Operations:**

- [Align Server Script](scripts/align-server.py)
- [MCP Quick Connect](scripts/mcp-quick-connect.py)
- [Integration Status](mcp-servers/.integration-status.json)

## 📚 Documentation Index

For a complete list of all documentation files, see
[DOCUMENTATION-INDEX.md](DOCUMENTATION-INDEX.md).

**Repository Structure Version**: 2.0  
**Last Reorganization**: February 6, 2026  
**Maintainer**: bryansrevision
