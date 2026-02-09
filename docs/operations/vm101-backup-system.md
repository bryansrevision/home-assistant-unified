# VM 101 Backup System Documentation

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Proxmox VE Host                          │
│                  (192.168.1.185:8006)                       │
│                                                             │
│  ┌──────────────────────┐      ┌─────────────────────────┐│
│  │   VM 102 (Primary)   │      │   VM 101 (Backup)       ││
│  │  192.168.1.134:8123  │◄────►│  192.168.1.201:8123     ││
│  │                      │ Sync │                         ││
│  │  - Home Assistant OS │      │  - Home Assistant OS    ││
│  │  - 263 entities      │      │  - Mirror config        ││
│  │  - Production        │      │  - Hot standby          ││
│  └──────────────────────┘      └─────────────────────────┘│
│           │                              │                  │
│           │ Hourly Backup                │ Health Check     │
│           ▼                              ▼ Every 5 min      │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         Automated Sync & Monitoring                  │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Sync Schedule

| Frequency | Type | Description |
|-----------|------|-------------|
| Every hour | Incremental | Configuration sync |
| Daily 2 AM | Full backup | Complete system backup |
| Every 5 min | Health check | Monitor both VMs |
| Weekly | Snapshot | Proxmox VM snapshots |

## Recovery Time Objectives (RTO)

- **Detection**: < 5 minutes (automated monitoring)
- **Failover Decision**: < 15 minutes (manual)
- **Service Restoration**: < 30 minutes (total)
- **Data Loss**: < 1 hour (hourly sync)

## Maintenance Procedures

### Weekly Tasks
- Review backup logs
- Verify VM 101 health
- Test backup restoration (monthly)

### Monthly Tasks
- Full disaster recovery test
- Review and update documentation
- Verify snapshot retention

### Quarterly Tasks
- Review and optimize sync frequency
- Update failover procedures
- Capacity planning review
