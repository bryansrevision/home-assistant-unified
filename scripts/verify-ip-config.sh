#!/bin/bash
# Verify IP address configuration

NEW_IP="192.168.1.134"
OLD_IP="192.168.1.201"

echo "🔍 Verifying IP address configuration..."

# Check for old IP references
echo ""
echo "Checking for remaining old IP references ($OLD_IP):"
grep -r "$OLD_IP" . \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude-dir=venv \
    --exclude="*.bak" \
    2>/dev/null | wc -l | xargs -I {} echo "   Found: {} occurrences"

# List files still containing old IP
echo ""
echo "Files still containing old IP:"
grep -r -l "$OLD_IP" . \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude-dir=venv \
    --exclude="*.bak" \
    2>/dev/null || echo "   ✅ None found"

# Verify new IP is present
echo ""
echo "Verifying new IP ($NEW_IP) is configured:"
grep -r "$NEW_IP" . \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude-dir=venv \
    2>/dev/null | wc -l | xargs -I {} echo "   Found: {} occurrences"

echo ""
echo "✅ Verification complete"
