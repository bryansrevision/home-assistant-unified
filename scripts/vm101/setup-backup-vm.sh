#!/bin/bash
# VM 101 Backup System Setup Script
# Automates the configuration of HA backup instance

set -e

VM_ID=101
VM_NAME="ha-backup"
VM_IP="192.168.1.201"
PRIMARY_IP="192.168.1.134"

echo "🔧 Setting up VM 101 Backup System"
echo "=================================="

# Download Home Assistant OS
download_ha_os() {
    echo "📥 Downloading Home Assistant OS..."
    HAOS_VERSION="13.1"
    HAOS_URL="https://github.com/home-assistant/operating-system/releases/download/${HAOS_VERSION}/haos_ova-${HAOS_VERSION}.qcow2.xz"
    
    wget -O /tmp/haos.qcow2.xz "$HAOS_URL"
    xz -d /tmp/haos.qcow2.xz
    
    echo "✅ Home Assistant OS downloaded"
}

# Create VM in Proxmox
create_vm() {
    echo "🖥️  Creating VM 101 in Proxmox..."
    
    ssh root@192.168.1.185 << 'EOF'
    # Create VM
    qm create 101 \
        --name ha-backup \
        --memory 8192 \
        --cores 4 \
        --net0 virtio,bridge=vmbr0 \
        --scsihw virtio-scsi-pci
    
    # Import disk
    qm importdisk 101 /tmp/haos.qcow2 local-lvm
    
    # Attach disk
    qm set 101 --scsi0 local-lvm:vm-101-disk-0
    
    # Set boot order
    qm set 101 --boot order=scsi0
    
    # Enable QEMU agent
    qm set 101 --agent enabled=1
    
    echo "✅ VM 101 created successfully"
EOF
}

# Configure network
configure_network() {
    echo "🌐 Configuring network for VM 101..."
    
    # Network will be configured via HA OS initial setup
    # Static IP: 192.168.1.201
    # Gateway: 192.168.1.1
    # DNS: 192.168.1.1, 8.8.8.8
}

# Main execution
main() {
    download_ha_os
    create_vm
    configure_network
    
    echo ""
    echo "✅ VM 101 setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Start VM 101: qm start 101"
    echo "2. Access console: http://192.168.1.201:8123"
    echo "3. Complete initial Home Assistant setup"
    echo "4. Run sync configuration script"
}

main
