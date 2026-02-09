#!/bin/bash
# ============================================================================
# Deploy configuration to Home Assistant VM
# Pulls latest from GitHub and reloads configuration
# ============================================================================

set -e

CONFIG_DIR="/config"
REPO_URL="https://github.com/bryansrevision/home-assistant-unified.git"
BRANCH="master"

echo "=========================================="
echo "  Home Assistant Deployment Script"
echo "=========================================="

cd "$CONFIG_DIR"

# Check if git repo exists
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git remote add origin "$REPO_URL"
fi

# Stash any local changes
echo "Stashing local changes..."
git stash --include-untracked 2>/dev/null || true

# Pull latest
echo "Pulling latest from $BRANCH..."
git fetch origin "$BRANCH"
git reset --hard "origin/$BRANCH"

# Restore secrets (not in repo)
if [ -f "/config/.secrets.yaml.backup" ]; then
    echo "Restoring secrets..."
    cp /config/.secrets.yaml.backup /config/secrets.yaml
fi

echo ""
echo "Deployment complete!"
echo "Restart Home Assistant to apply changes:"
echo "  ha core restart"
echo ""
echo "Or reload specific components:"
echo "  curl -X POST http://localhost:8123/api/services/homeassistant/reload_core_config"
