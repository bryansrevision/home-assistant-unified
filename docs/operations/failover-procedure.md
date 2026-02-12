# VM 101 Failover Procedure

## When to Failover
- VM 102 hardware failure
- VM 102 corruption or boot failure
- Emergency maintenance on VM 102
- Testing disaster recovery

## Pre-Failover Checklist
- [ ] Verify VM 101 is running and healthy
- [ ] Verify latest backup is on VM 101
- [ ] Document reason for failover
- [ ] Notify relevant parties

## Failover Steps

### 1. Stop VM 102 (if possible)
```bash
ssh root@192.168.1.185 "qm stop 102"
```

### 2. Update DNS/Router
Point `homeassistant.local` to 192.168.1.201 or update router:
- Update DHCP reservation
- Update local DNS entries

### 3. Update Client Configurations
Update all devices/services to use: `http://192.168.1.201:8123`

### 4. Verify Services
```bash
# Check all integrations (unauthenticated)
curl http://192.168.1.201:8123/api/

# Config endpoint requires a valid Home Assistant token:
# curl -H "Authorization: Bearer <HOME_ASSISTANT_TOKEN>" http://192.168.1.201:8123/api/config
# Test automation engine
curl http://192.168.1.201:5000/api/health

# Verify MQTT
mosquitto_sub -h 192.168.1.201 -t "homeassistant/#"
```

### 5. Monitor Logs
```bash
# SSH to VM 101
ssh root@192.168.1.201

# Follow logs
ha logs
```

## Failback to VM 102

### When VM 102 is restored:
1. Stop all client traffic to VM 101
2. Create backup on VM 101
3. Restore backup to VM 102
4. Start VM 102
5. Verify all services on VM 102
6. Update DNS/Router back to 192.168.1.134
7. Resume sync schedule
