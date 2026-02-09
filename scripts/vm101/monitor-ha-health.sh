#!/bin/bash
# Monitor health of both VM 102 and VM 101
# Sends alerts if primary fails

PRIMARY_IP="192.168.1.134"
BACKUP_IP="192.168.1.201"

check_vm_health() {
    local vm_name=$1
    local vm_ip=$2
    
    echo "Checking ${vm_name} (${vm_ip})..."
    
    # Check if Home Assistant is responding
    if curl -s -f -m 5 "http://${vm_ip}:8123/api/" > /dev/null 2>&1; then
        echo "  ✅ ${vm_name} is healthy"
        return 0
    else
        echo "  ❌ ${vm_name} is DOWN"
        return 1
    fi
}

send_alert() {
    local message=$1
    
    # Send notification via multiple channels
    
    # IFTTT webhook
    curl -X POST "https://maker.ifttt.com/trigger/ha_alert/with/key/${IFTTT_KEY}" \
        -d "value1=${message}"
    
    # Optional: Send email, SMS, etc.
}

main() {
    echo "🏥 Home Assistant Health Check"
    echo "=============================="
    
    primary_status=0
    backup_status=0
    
    check_vm_health "VM 102 (Primary)" "$PRIMARY_IP" || primary_status=1
    check_vm_health "VM 101 (Backup)" "$BACKUP_IP" || backup_status=1
    
    if [ $primary_status -eq 1 ]; then
        send_alert "⚠️ CRITICAL: Primary HA (VM 102) is DOWN!"
        echo ""
        echo "🚨 PRIMARY DOWN - Consider manual failover to VM 101"
    fi
    
    if [ $backup_status -eq 1 ]; then
        send_alert "⚠️ WARNING: Backup HA (VM 101) is DOWN"
    fi
    
    if [ $primary_status -eq 0 ] && [ $backup_status -eq 0 ]; then
        echo ""
        echo "✅ All systems operational"
    fi
}

main
