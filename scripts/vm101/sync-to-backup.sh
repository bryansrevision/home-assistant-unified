#!/bin/bash
# Automated Configuration Sync from VM 102 to VM 101
# Ensures backup system mirrors primary configuration

set -e

PRIMARY_IP="192.168.1.134"
BACKUP_IP="192.168.1.201"
PRIMARY_TOKEN="${HA_PRIMARY_TOKEN}"
BACKUP_TOKEN="${HA_BACKUP_TOKEN}"

echo "🔄 Syncing VM 102 → VM 101"

# Create backup on primary
create_primary_backup() {
    echo "📦 Creating backup on VM 102..."
    
    curl -X POST \
        -H "Authorization: Bearer ${PRIMARY_TOKEN}" \
        -H "Content-Type: application/json" \
        http://${PRIMARY_IP}:8123/api/services/backup/create \
        -d '{
            "name": "sync_backup_'$(date +%Y%m%d_%H%M%S)'"
        }'
    
    sleep 10  # Wait for backup to complete
}

# Get latest backup
get_latest_backup() {
    echo "🔍 Getting latest backup..."
    
    BACKUP_ID=$(curl -s \
        -H "Authorization: Bearer ${PRIMARY_TOKEN}" \
        http://${PRIMARY_IP}:8123/api/backup/info | \
        jq -r '.backups | sort_by(.date) | last | .slug')
    
    echo "Latest backup: ${BACKUP_ID}"
}

# Download backup
download_backup() {
    echo "⬇️  Downloading backup from VM 102..."
    
    curl -o /tmp/ha-backup.tar \
        -H "Authorization: Bearer ${PRIMARY_TOKEN}" \
        http://${PRIMARY_IP}:8123/api/backup/download/${BACKUP_ID}
}

# Upload to backup VM
upload_to_backup() {
    echo "⬆️  Uploading backup to VM 101..."
    
    curl -X POST \
        -H "Authorization: Bearer ${BACKUP_TOKEN}" \
        -F "file=@/tmp/ha-backup.tar" \
        http://${BACKUP_IP}:8123/api/backup/upload
}

# Restore on backup VM (optional - for testing)
restore_backup() {
    echo "🔧 Restoring backup on VM 101..."
    
    curl -X POST \
        -H "Authorization: Bearer ${BACKUP_TOKEN}" \
        -H "Content-Type: application/json" \
        http://${BACKUP_IP}:8123/api/backup/restore/${BACKUP_ID}
}

# Main execution
main() {
    create_primary_backup
    get_latest_backup
    download_backup
    upload_to_backup
    
    echo ""
    echo "✅ Sync complete!"
    echo "Backup ID: ${BACKUP_ID}"
    echo ""
    echo "To restore on VM 101, run:"
    echo "  ./scripts/vm101/restore-backup.sh ${BACKUP_ID}"
}

main
