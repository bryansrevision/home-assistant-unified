# 🔄 Repository Synchronization Guide

**Purpose:** Keep UNIFIED-HOME-ASSISTANT master repo in sync with all source repositories

---

## 📊 Sync Architecture

```
UNIFIED-HOME-ASSISTANT (Master)
        ↕
    ┌───┴───┬───────┬────────┐
    ↓       ↓       ↓        ↓
 HOME-AI  home-   Android  wearables
   -AUTO  assistant Config  -platform
          -config
```

---

## 🎯 Repository Mapping

### Source → Master Mapping

| Source Repo | Source Path | Master Path | Sync Direction |
|-------------|-------------|-------------|----------------|
| **HOME-AI-AUTOMATION** |
| `home_automation/core/` | → | `python/` | Bidirectional |
| `home_automation/integrations/` | → | `integrations/` | Bidirectional |
| `config/` | → | `services/agentstack/` | Bidirectional |
| `docker-compose.yml` | → | `services/docker-compose.yml` | Master→Source |
| **home-assistant-config** |
| `automations/` | → | `automations/` | Bidirectional |
| `mcp-config/` | → | `mcp-config/` | Bidirectional |
| `services/` | → | `services/` | Bidirectional |
| **Home-environment-Android** |
| `configs/home-assistant/` | → | `integrations/mobile-devices/` | Bidirectional |
| `android/` | → | `integrations/mobile-devices/android/` | Bidirectional |
| **wearables-integration-platform** |
| `api_credentials/` | → | `integrations/wearables/` | Bidirectional |
| `docs/OMI_MCP_SETUP.md` | → | `mcp-config/omi-setup.md` | Bidirectional |
| `docs/BEEAI_AGENTSTACK_INTEGRATION.md` | → | `services/agentstack/README.md` | Bidirectional |

---

## 🔧 Manual Sync Process

### Option 1: Full Sync (All Repos)

```bash
cd UNIFIED-HOME-ASSISTANT

# Pull latest from all source repos
./scripts/sync-from-repos.sh --all

# Review changes
git status
git diff

# Commit consolidated changes
git add .
git commit -m "sync: Consolidated updates from all repos"

# Push updates back to source repos
./scripts/sync-to-repos.sh --all
```

### Option 2: Module-Specific Sync

```bash
# Sync only automations
./scripts/sync-from-repos.sh --module automations
./scripts/sync-to-repos.sh --module automations

# Sync only MCP configs
./scripts/sync-from-repos.sh --module mcp-config

# Sync only Python code
./scripts/sync-from-repos.sh --module python
```

### Option 3: Repo-Specific Sync

```bash
# Sync from specific repo
./scripts/sync-from-repos.sh --repo HOME-AI-AUTOMATION
./scripts/sync-from-repos.sh --repo home-assistant-config

# Sync to specific repo
./scripts/sync-to-repos.sh --repo HOME-AI-AUTOMATION
```

---

## 🤖 Automated Sync (GitHub Actions)

### Scheduled Sync Workflow

```yaml
# .github/workflows/sync-repos.yml
name: Sync Repositories

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:       # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Master
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Setup Git
        run: |
          git config --global user.name "Sync Bot"
          git config --global user.email "bot@example.com"
      
      - name: Sync from Source Repos
        run: ./scripts/sync-from-repos.sh --all
        env:
          GITHUB_TOKEN: ${{ secrets.GH_PAT }}
      
      - name: Commit Changes
        run: |
          git add .
          git commit -m "chore: Auto-sync from source repos" || exit 0
          git push
      
      - name: Sync to Source Repos
        run: ./scripts/sync-to-repos.sh --all
        env:
          GITHUB_TOKEN: ${{ secrets.GH_PAT }}
```

---

## 📝 Sync Scripts

### sync-from-repos.sh (Pull Updates)

```bash
#!/bin/bash
# Pull latest changes from source repositories into UNIFIED master

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNIFIED_ROOT="$(dirname "$SCRIPT_DIR")"
WORKSPACE_ROOT="$(dirname "$UNIFIED_ROOT")"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔄 Syncing from source repositories...${NC}"

# Function to sync a specific repo
sync_repo() {
    local repo_name=$1
    local source_path="${WORKSPACE_ROOT}/${repo_name}"
    
    if [ ! -d "$source_path" ]; then
        echo -e "${RED}✗ Repository not found: ${repo_name}${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}→ Syncing from ${repo_name}${NC}"
    
    case $repo_name in
        "HOME-AI-AUTOMATION")
            rsync -av --delete \
                "${source_path}/home_automation/core/" \
                "${UNIFIED_ROOT}/python/core/"
            rsync -av --delete \
                "${source_path}/home_automation/integrations/" \
                "${UNIFIED_ROOT}/integrations/"
            ;;
        
        "home-assistant-config"|"CodeSpace-Workspace-Template/home-assistant-config")
            local ha_config_path="${WORKSPACE_ROOT}/CodeSpace-Workspace-Template/home-assistant-config"
            rsync -av --delete \
                "${ha_config_path}/automations/" \
                "${UNIFIED_ROOT}/automations/"
            rsync -av --delete \
                "${ha_config_path}/mcp-config/" \
                "${UNIFIED_ROOT}/mcp-config/"
            ;;
        
        "Home-environment---Android-Config-and-Integration-")
            rsync -av --delete \
                "${source_path}/configs/home-assistant/" \
                "${UNIFIED_ROOT}/integrations/mobile-devices/configs/"
            ;;
        
        "wearables-integration-platform")
            rsync -av --delete \
                "${source_path}/api_credentials/" \
                "${UNIFIED_ROOT}/integrations/wearables/"
            cp "${source_path}/docs/OMI_MCP_SETUP.md" \
                "${UNIFIED_ROOT}/docs/omi-setup.md"
            ;;
    esac
    
    echo -e "${GREEN}✓ Synced ${repo_name}${NC}"
}

# Parse arguments
if [ "$1" == "--all" ]; then
    sync_repo "HOME-AI-AUTOMATION"
    sync_repo "CodeSpace-Workspace-Template/home-assistant-config"
    sync_repo "Home-environment---Android-Config-and-Integration-"
    sync_repo "wearables-integration-platform"
elif [ "$1" == "--repo" ] && [ -n "$2" ]; then
    sync_repo "$2"
else
    echo "Usage: $0 --all | --repo <repo-name>"
    exit 1
fi

echo -e "${GREEN}✓ Sync complete!${NC}"
```

### sync-to-repos.sh (Push Updates)

```bash
#!/bin/bash
# Push changes from UNIFIED master back to source repositories

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNIFIED_ROOT="$(dirname "$SCRIPT_DIR")"
WORKSPACE_ROOT="$(dirname "$UNIFIED_ROOT")"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}📤 Pushing to source repositories...${NC}"

push_to_repo() {
    local repo_name=$1
    local target_path="${WORKSPACE_ROOT}/${repo_name}"
    
    if [ ! -d "$target_path" ]; then
        echo "✗ Repository not found: ${repo_name}"
        return 1
    fi
    
    echo -e "${YELLOW}← Pushing to ${repo_name}${NC}"
    
    case $repo_name in
        "HOME-AI-AUTOMATION")
            rsync -av --delete \
                "${UNIFIED_ROOT}/python/core/" \
                "${target_path}/home_automation/core/"
            rsync -av --delete \
                "${UNIFIED_ROOT}/integrations/" \
                "${target_path}/home_automation/integrations/"
            ;;
        
        "CodeSpace-Workspace-Template/home-assistant-config")
            rsync -av --delete \
                "${UNIFIED_ROOT}/automations/" \
                "${target_path}/automations/"
            rsync -av --delete \
                "${UNIFIED_ROOT}/mcp-config/" \
                "${target_path}/mcp-config/"
            ;;
    esac
    
    # Commit and push
    cd "$target_path"
    if [ -n "$(git status --porcelain)" ]; then
        git add .
        git commit -m "sync: Update from UNIFIED-HOME-ASSISTANT master"
        git push
        echo -e "${GREEN}✓ Pushed to ${repo_name}${NC}"
    else
        echo "No changes to push"
    fi
}

# Parse arguments
if [ "$1" == "--all" ]; then
    push_to_repo "HOME-AI-AUTOMATION"
    push_to_repo "CodeSpace-Workspace-Template/home-assistant-config"
    push_to_repo "Home-environment---Android-Config-and-Integration-"
    push_to_repo "wearables-integration-platform"
elif [ "$1" == "--repo" ] && [ -n "$2" ]; then
    push_to_repo "$2"
else
    echo "Usage: $0 --all | --repo <repo-name>"
    exit 1
fi

echo -e "${GREEN}✓ Push complete!${NC}"
```

---

## 🔍 Conflict Resolution

### If Conflicts Occur:

1. **Review conflicting files**
   ```bash
   git status
   git diff
   ```

2. **Choose resolution strategy**
   - Keep master version: `git checkout --ours <file>`
   - Keep source version: `git checkout --theirs <file>`
   - Manual merge: Edit files directly

3. **Complete merge**
   ```bash
   git add <resolved-files>
   git commit -m "resolve: Merge conflicts from sync"
   ```

---

## ⚙️ Best Practices

### 1. Always Pull Before Push
```bash
./scripts/sync-from-repos.sh --all
# Review changes
./scripts/sync-to-repos.sh --all
```

### 2. Test After Sync
```bash
# Run tests
pytest tests/

# Validate automations
yamllint automations/

# Check MCP configs
python scripts/validate-mcp-config.py
```

### 3. Commit Message Format
```
sync: <action> from/to <repo>

Examples:
- sync: Pull automation updates from home-assistant-config
- sync: Push Python modules to HOME-AI-AUTOMATION  
- sync: Bidirectional sync of MCP configurations
```

### 4. Use Branches for Major Changes
```bash
git checkout -b sync/major-automation-update
./scripts/sync-from-repos.sh --all
# Review and test
git push origin sync/major-automation-update
# Create PR for review
```

---

## 📅 Sync Schedule

### Recommended Schedule:
- **Manual Sync**: After major changes in any repo
- **Automated Sync**: Every 6 hours (via GitHub Actions)
- **Full Review**: Weekly manual review of sync status
- **Backup**: Before each sync operation

---

## 🛠️ Troubleshooting

### Issue: Rsync Permission Denied
```bash
# Fix permissions
chmod -R u+rw "${UNIFIED_ROOT}"
```

### Issue: Git Merge Conflicts
```bash
# Abort and restart
git merge --abort
./scripts/sync-from-repos.sh --repo <specific-repo>
```

### Issue: Missing Files After Sync
```bash
# Check sync logs
./scripts/sync-from-repos.sh --all --verbose

# Verify source files exist
ls -la "${WORKSPACE_ROOT}/<repo>/<path>"
```

---

## 📊 Sync Status Dashboard

Track sync status in [STATUS.md](./STATUS.md):

```markdown
## Last Sync Status

| Repository | Last Sync | Status | Files Updated |
|------------|-----------|--------|---------------|
| HOME-AI-AUTOMATION | 2026-01-30 14:23 | ✅ Success | 15 |
| home-assistant-config | 2026-01-30 14:23 | ✅ Success | 8 |
| Android-Config | 2026-01-30 14:24 | ✅ Success | 3 |
| wearables-platform | 2026-01-30 14:24 | ✅ Success | 5 |
```

---

**For automated setup, run:** `./scripts/setup-sync.sh`
