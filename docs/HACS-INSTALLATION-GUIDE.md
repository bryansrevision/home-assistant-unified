# 🏪 HACS Installation & Configuration Guide

## 📋 Overview

**HACS (Home Assistant Community Store)** is a custom integration that gives you
access to thousands of community-created custom components, plugins, themes, and
more for Home Assistant.

**Server:** 192.168.1.134:8123  
**HA Version:** 2025.12.5  
**Date:** February 6, 2026



## ✅ Prerequisites

Before installing HACS, ensure you have:

- ✅ Home Assistant Core 2024.6.0 or newer (you have **2025.12.5** ✓)
- ✅ GitHub account (required for HACS authentication)
- ✅ Access to Home Assistant configuration directory
- ✅ SSH or File Editor access to your HA server



## 🚀 Installation Methods

### Method 1: Direct Download (Recommended)

#### Step 1: Download HACS

```bash
# SSH into your Home Assistant server, then:
cd /config
wget -O - https://get.hacs.xyz | bash -
```

**OR via PowerShell (if you have network share access):**

```powershell
# Download HACS to custom_components
$hacsUrl = "https://github.com/hacs/integration/releases/latest/download/hacs.zip"
$configPath = "\\192.168.1.134\config"
$customComponentsPath = "$configPath\custom_components"

# Create custom_components directory if it doesn't exist
New-Item -ItemType Directory -Path "$customComponentsPath\hacs" -Force

# Download and extract HACS
$tempZip = "$env:TEMP\hacs.zip"
Invoke-WebRequest -Uri $hacsUrl -OutFile $tempZip
Expand-Archive -Path $tempZip -DestinationPath "$customComponentsPath\hacs" -Force
Remove-Item $tempZip

Write-Host "✅ HACS downloaded to custom_components/hacs"
```

#### Step 2: Restart Home Assistant

```bash
# Via Home Assistant UI:
# Settings → System → Restart

# Or via CLI:
ha core restart
```

#### Step 3: Add HACS Integration

1. Open Home Assistant: http://192.168.1.134:8123
2. Go to **Settings → Devices & Services**
3. Click **+ Add Integration** (bottom right)
4. Search for **HACS**
5. Click on HACS to start setup

#### Step 4: GitHub Authentication

1. HACS will provide a **Device Activation Code**
2. Click the link or go to: https://github.com/login/device
3. Enter the activation code
4. Authorize HACS to access your GitHub account
5. Return to Home Assistant

#### Step 5: Configure HACS

1. **Select what you want to track:**
   - ☑ Integrations (custom components)
   - ☑ Frontend (Lovelace cards)
   - ☑ Themes
   - ☐ NetDaemon (optional)
   - ☐ AppDaemon (optional)

2. **Accept Terms:**
   - Read and check the boxes
   - Click **Submit**

3. **Wait for HACS to load:**
   - Initial load may take 2-5 minutes
   - HACS indexes all available repositories



### Method 2: Manual Installation

If automated download fails:

#### Step 1: Download from GitHub

1. Go to: https://github.com/hacs/integration/releases/latest
2. Download `hacs.zip`
3. Extract the archive

#### Step 2: Upload to Home Assistant

```powershell
# Copy HACS directory to custom_components
$hacsSource = "C:\Users\Dylan\Downloads\hacs"
$configPath = "\\192.168.1.134\config"

Copy-Item -Path $hacsSource -Destination "$configPath\custom_components\hacs" -Recurse -Force
```

**OR use File Editor add-on:**
1. Open File Editor in Home Assistant
2. Navigate to `/config/custom_components/`
3. Create `hacs` folder
4. Upload all HACS files

#### Step 3: Follow Steps 2-5 from Method 1



## 🔧 Post-Installation Configuration

### Verify Installation

```bash
# Check HACS version in Home Assistant logs
# Settings → System → Logs → Filter by "hacs"
```

### Configure Updates

HACS will automatically check for updates daily. To configure:

1. Open HACS (sidebar)
2. Click **⋮** (three dots) → **Custom repositories** (optional)
3. Click **⋮** → **Configuration**
4. Set preferences:
   - **Enable AppDaemon apps discovery**
   - **Enable NetDaemon apps discovery**
   - **Enable experimental features** (optional)

### Add Custom Repositories (Optional)

If you have specific repositories not in HACS:

1. HACS → **⋮** → **Custom repositories**
2. Add repository URL (e.g., `https://github.com/username/repo`)
3. Select category: Integration, Plugin, Theme, etc.
4. Click **Add**



## 📦 Recommended HACS Integrations

### Essential Custom Cards (Frontend)

Install these via HACS → Frontend:

1. **button-card** - Advanced button customization
   ```
   HACS → Frontend → Explore & Download Repositories → Search "button-card"
   ```

2. **card-mod** - Style any card with CSS
3. **mini-media-player** - Enhanced media player card
4. **auto-entities** - Dynamically populate cards
5. **layout-card** - Advanced layout control
6. **mushroom-cards** - Modern, clean card designs
7. **apexcharts-card** - Advanced charting

### Popular Custom Integrations

Install these via HACS → Integrations:

1. **Alexa Media Player** - Control Alexa devices
2. **Node-RED Companion** - Enhanced Node-RED integration
3. **Pyscript** - Python scripting for automations
4. **Watchman** - Monitor missing entities
5. **HACS-Pyscript** - Python automation
6. **Browser Mod** - Control browser tabs as entities

### Installation Command Example

```bash
# After selecting a component in HACS:
# 1. Click "Download"
# 2. Select version (latest recommended)
# 3. Restart Home Assistant (if required)
# 4. Add integration via Settings → Devices & Services (for integrations)
```



## 🔍 Using HACS

### Browsing Repositories

```
HACS Sidebar → Integrations/Frontend/Themes
→ Explore & Download Repositories
→ Search or browse categories
```

### Installing a Component

1. Open HACS → **Integrations** (or Frontend/Themes)
2. Click **Explore & Download Repositories** (bottom right)
3. Search for component (e.g., "Alexa Media Player")
4. Click on the component
5. Click **Download**
6. Select version (usually latest)
7. Click **Download** again
8. **Restart Home Assistant** (if prompted)

### Updating Components

```
HACS → Updates tab
→ Click "Update" on any component
→ Restart if required
```



## 🔐 Security Best Practices

### GitHub Personal Access Token (Optional)

For better API rate limits:

1. Go to: https://github.com/settings/tokens/new
2. Set name: "HACS Home Assistant"
3. Set expiration: 90 days (or longer)
4. Select scopes:
   - ☑ `public_repo`
   - ☑ `read:user`
5. Generate token
6. Copy token

**Add to HACS:**
```
HACS → ⋮ → Configuration → GitHub Personal Access Token
→ Paste token → Save
```

### Backup Before Installing

```powershell
# Backup Home Assistant config before major changes
$backupPath = "C:\Users\Dylan\Dev\.WorkSpace\HomeAssistant\backups"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

# Copy current config
robocopy "\\192.168.1.134\config" "$backupPath\ha-backup-$timestamp" /E /Z /R:3

Write-Host "✅ Backup saved to: $backupPath\ha-backup-$timestamp"
```



## 🐛 Troubleshooting

### Issue: HACS Not Showing in Integrations

**Solution:**
```bash
# 1. Check custom_components/hacs exists
ls /config/custom_components/hacs

# 2. Check permissions
chmod -R 755 /config/custom_components/hacs

# 3. Clear browser cache (Ctrl+F5)

# 4. Restart Home Assistant completely
ha core restart
```

### Issue: GitHub Rate Limit Exceeded

**Solution:**
- Add a GitHub Personal Access Token (see Security section)
- Wait for rate limit to reset (usually 1 hour)

### Issue: "Integration not found" After Install

**Solution:**
1. Ensure you restarted Home Assistant
2. Check Home Assistant logs: Settings → System → Logs
3. Verify files are in correct location:
   ```
   /config/custom_components/hacs/
   ```

### Issue: HACS Shows "Update Failed"

**Solution:**
```bash
# Remove and reinstall HACS
rm -rf /config/custom_components/hacs

# Download again
cd /config
wget -O - https://get.hacs.xyz | bash -

# Restart HA
ha core restart
```



## 📝 Quick Reference

### HACS Directory Structure

```
/config/
├── custom_components/
│   └── hacs/
│       ├── __init__.py
│       ├── manifest.json
│       ├── ...
└── www/
    └── community/          # HACS frontend components installed here
        ├── button-card/
        ├── mini-media-player/
        └── ...
```

### HACS Commands via MCP

```python
# Create a script to check HACS installation
# File: scripts/check-hacs.py

import asyncio
from ha_mcp_client import HomeAssistantMCPClient, MCPConfig
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-servers"))

async def check_hacs():
    config = MCPConfig.from_env()
    async with HomeAssistantMCPClient(config) as client:
        # Get all integrations
        integrations = await client.call_service(
            "system_log", "get_config", {}
        )
        
        # Check if HACS is loaded
        states = await client.get_all_states()
        hacs_entities = [s for s in states if "hacs" in s["entity_id"]]
        
        if hacs_entities:
            print("✅ HACS is installed and running")
            print(f"   Found {len(hacs_entities)} HACS-related entities")
        else:
            print("❌ HACS not detected")
            print("   Run installation steps to add HACS")

if __name__ == "__main__":
    asyncio.run(check_hacs())
```

### Run Check

```powershell
cd "C:\Users\Dylan\Dev\.WorkSpace\HomeAssistant\home-assistant-unified"
python scripts/check-hacs.py
```



## 🔗 Resources

- **HACS Official Documentation:** https://hacs.xyz/
- **HACS GitHub:** https://github.com/hacs/integration
- **HACS Discord:** https://discord.gg/apgchf8
- **Frontend Repository Browser:** https://hacs.xyz/docs/categories/plugin
- **Integration Repository Browser:**
  https://hacs.xyz/docs/categories/integration



## ✅ Next Steps

After HACS installation:

1. ☐ Install recommended custom cards (button-card, card-mod, etc.)
2. ☐ Install Alexa Media Player (if using Alexa)
3. ☐ Browse HACS → Integrations for devices/services you use
4. ☐ Install themes from HACS → Themes
5. ☐ Set up automatic backups before installing new components
6. ☐ Configure GitHub Personal Access Token for better rate limits



**Installation support:** If issues arise, check Home Assistant logs and HACS
Discord.

**Last Updated:** February 6, 2026
