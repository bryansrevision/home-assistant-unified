# Automation Scripts

This directory contains utility scripts for managing and synchronizing the Home Assistant Unified system.

## Key Scripts

### Server Synchronization
- **align-server.py** - Main server synchronization tool
  - Sync automations, entities, and state with live HA server
  - Run diagnostics and health checks
  - Pull/push changes bidirectionally
  
  Usage:
  ```bash
  python scripts/align-server.py sync-pull --type all
  python scripts/align-server.py sync-push --type automations
  python scripts/align-server.py diagnose --verbose
  python scripts/align-server.py health-check
  ```

### MCP Integration
- **mcp-quick-connect.py** - Quick MCP connection testing
- See [../mcp-servers/](../mcp-servers/) for full MCP integration scripts

### Testing & Debugging
- **test_ha_connection.py** - Test Home Assistant API connection
- **debug_env.py** - Debug environment variables and configuration
- **compare-ha-repo.py** - Compare repository state with live server

### VM Management
Located in subdirectories:
- **vm101/** - VM 101 backup system scripts
- **setup/** - Initial setup and configuration scripts
- **maintenance/** - Maintenance and update scripts

## Quick Reference

### Common Tasks

**Sync from server:**
```bash
python scripts/align-server.py sync-pull --type all
```

**Push automations to server:**
```bash
python scripts/align-server.py sync-push --type automations
```

**Check health:**
```bash
python scripts/align-server.py health-check
```

**Test connection:**
```bash
python scripts/test_ha_connection.py
```

**Run diagnostics:**
```bash
python scripts/align-server.py diagnose --verbose
```

## Configuration

Scripts use environment variables from `config/.env`:
- `HOME_ASSISTANT_TOKEN` - API authentication token
- `HA_HOST` - Home Assistant host (192.168.1.134:8123)
- Other service-specific variables

## Related Documentation

- **MCP Integration**: [../mcp-servers/MCP-LIVE-SERVER-INTEGRATION.md](../mcp-servers/MCP-LIVE-SERVER-INTEGRATION.md)
- **Server Update Guide**: [../docs/SERVER-UPDATE.md](../docs/SERVER-UPDATE.md)
- **Sync Guide**: [../docs/SYNC_GUIDE.md](../docs/SYNC_GUIDE.md)
- **Quick Reference**: [../QUICK-REFERENCE.md](../QUICK-REFERENCE.md)

## VM Scripts

### VM 101 Backup System
Located in `vm101/` subdirectory:
- Automated backup scripts for high-availability
- Health monitoring
- Failover procedures

See [../docs/operations/vm101-backup-system.md](../docs/operations/vm101-backup-system.md) for details.

## See Also

- Main README: [../README.md](../README.md)
- Documentation Index: [../DOCUMENTATION-INDEX.md](../DOCUMENTATION-INDEX.md)
