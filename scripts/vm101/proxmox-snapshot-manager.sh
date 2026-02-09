#!/bin/bash
# Manage Proxmox snapshots for both VMs

PROXMOX_HOST="192.168.1.185"
PROXMOX_USER="root@pam"
VM_102_ID=102
VM_101_ID=101

# Create snapshot
create_snapshot() {
    local vm_id=$1
    local snap_name
    snap_name="auto_$(date +%Y%m%d_%H%M%S)"
    
    echo "📸 Creating snapshot for VM ${vm_id}: ${snap_name}"
    
    ssh "${PROXMOX_USER}@${PROXMOX_HOST}" \
        "qm snapshot ${vm_id} ${snap_name} --description 'Automated snapshot'"
}

# List snapshots
list_snapshots() {
    local vm_id=$1
    
    echo "Snapshots for VM ${vm_id}:"
    ssh "${PROXMOX_USER}@${PROXMOX_HOST}" \
        "qm listsnapshot ${vm_id}"
}

# Delete old snapshots (keep last 7)
cleanup_snapshots() {
    local vm_id=$1
    
    echo "🗑️  Cleaning up old snapshots for VM ${vm_id}"
    
    ssh "${PROXMOX_USER}@${PROXMOX_HOST}" bash -s << EOF
    snapshots=\$(qm listsnapshot ${vm_id} | grep -o 'auto_[0-9_]*' | sort | head -n -7)
    for snap in \$snapshots; do
        echo "Deleting: \$snap"
        qm delsnapshot ${vm_id} \$snap
    done
EOF
}

# Main execution
main() {
    echo "🔄 Proxmox Snapshot Manager"
    echo "==========================="
    
    # Create snapshots for both VMs
    create_snapshot "$VM_102_ID"
    create_snapshot "$VM_101_ID"
    
    # Cleanup old snapshots
    cleanup_snapshots "$VM_102_ID"
    cleanup_snapshots "$VM_101_ID"
    
    echo ""
    echo "✅ Snapshot management complete"
}

main
