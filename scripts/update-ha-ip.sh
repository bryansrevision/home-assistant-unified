#!/bin/bash
# Update Home Assistant IP address across repository
# From: 192.168.1.201 → To: 192.168.1.134

set -e

OLD_IP="192.168.1.201"
NEW_IP="192.168.1.134"

echo "🔧 Updating Home Assistant IP address..."
echo "   From: $OLD_IP"
echo "   To:   $NEW_IP"
echo ""

# Function to update files
update_files() {
    local pattern=$1
    local description=$2
    
    echo "📝 Updating $description..."
    find . -type f $pattern \
        -not -path "./.*" \
        -not -path "*/node_modules/*" \
        -not -path "*/venv/*" \
        -exec grep -l "$OLD_IP" {} \; 2>/dev/null | while read file; do
        echo "   ✓ $file"
        sed -i.bak "s/$OLD_IP/$NEW_IP/g" "$file"
        rm "${file}.bak"
    done
}

# Update YAML files
update_files "\( -name '*.yaml' -o -name '*.yml' \)" "YAML configuration files"

# Update Markdown documentation
update_files "-name '*.md'" "Markdown documentation"

# Update environment files
update_files "\( -name '*.env*' -o -name 'secrets*' \)" "environment and secrets files"

# Update JSON files
update_files "-name '*.json'" "JSON configuration files"

# Update shell scripts
update_files "\( -name '*.sh' -o -name '*.bash' \)" "shell scripts"

# Update Python files
update_files "-name '*.py'" "Python scripts"

echo ""
echo "✅ IP address update complete!"
echo "⚠️  Please review changes with: git diff"
echo "⚠️  Test configuration before committing"
