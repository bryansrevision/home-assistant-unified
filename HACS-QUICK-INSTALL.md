# 🏪 HACS Installation - Step-by-Step Guide for 192.168.1.134

## ✅ Easiest Method: Terminal & SSH Add-on (Web UI)

Since network shares and SSH aren't accessible, use Home Assistant's built-in
Terminal add-on:

### Step 1: Access Home Assistant

Open your browser to: **http://192.168.1.134:8123**

### Step 2: Open Terminal & SSH Add-on

1. Click **Settings** (bottom left)
2. Click **Add-ons**
3. Click **Add-on Store** (bottom right)
4. Search for **"Terminal & SSH"**
5. Click **Terminal & SSH** add-on
6. Click **Install** (if not already installed)
7. After installation, click **Start**
8. Click **Open Web UI**

### Step 3: Run HACS Installation Command

In the Terminal window that opens, paste this command:

```bash
cd /config
wget -O - https://get.hacs.xyz | bash -
```

Press **Enter** and wait for installation to complete (10-30 seconds).

You should see:
```
✅ HACS installation complete
```

### Step 4: Restart Home Assistant

1. Close the Terminal
2. Go to **Settings → System → Restart**
3. Click **Restart** and confirm
4. Wait 30-60 seconds for restart

### Step 5: Add HACS Integration

After restart:

1. Go to **Settings → Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for **"HACS"**
4. Click **HACS** to start setup

### Step 6: Authenticate with GitHub

1. HACS will display a **device activation code** (8 characters)
2. Click the link or manually go to: **https://github.com/login/device**
3. Login to GitHub if needed
4. Enter the activation code
5. Click **Authorize hacs**
6. Return to Home Assistant

### Step 7: Configure HACS

1. Check the boxes:
   - ☑ **Integrations**
   - ☑ **Frontend**
   - ☑ **Themes**
2. Read and accept the terms
3. Click **Submit**

HACS will now load (takes 2-5 minutes on first run).



## 🎯 Alternative: Use Python Script with MCP

If Terminal add-on isn't available, run this from your PC:

```powershell
cd "C:\Users\Dylan\Dev\.WorkSpace\HomeAssistant\home-assistant-unified"
python scripts/install-hacs-via-api.py
```

This will guide you through installation using Home Assistant's API.



## 📦 After Installation: Install Recommended Components

### Essential Frontend Cards

1. Open **HACS** (in sidebar)
2. Click **Frontend**
3. Click **Explore & Download Repositories**
4. Install these cards:
   - **button-card** - Custom button designs
   - **card-mod** - Style any card
   - **mini-media-player** - Enhanced media controls
   - **auto-entities** - Dynamic entity lists
   - **mushroom-cards** - Modern card designs

### Popular Integrations

1. **HACS → Integrations → Explore & Download Repositories**
2. Install:
   - **Alexa Media Player** - Control Alexa devices
   - **Browser Mod** - Control browser tabs
   - **Watchman** - Monitor missing entities



## 🔍 Verify Installation

Run from your PC to check HACS status:

```powershell
cd "C:\Users\Dylan\Dev\.WorkSpace\HomeAssistant\home-assistant-unified"
python scripts/check-hacs.py
```

You should see:
```
✅ HACS IS INSTALLED!
   Found X HACS-related entities
```



## 🐛 Troubleshooting

### Issue: Can't Find Terminal & SSH Add-on

**Solution:**
- Your HA might use "SSH & Web Terminal" (different name)
- Or install "Studio Code Server" add-on which has built-in terminal

### Issue: wget command not found

**Solution:** Use this alternative command:
```bash
cd /config
curl -sfSL https://get.hacs.xyz | bash -
```

### Issue: Permission Denied

**Solution:**
```bash
cd /config
sudo wget -O - https://get.hacs.xyz | sudo bash -
```

### Issue: HACS Not Showing After Restart

**Solutions:**
1. Clear browser cache (Ctrl + Shift + R)
2. Check logs: Settings → System → Logs, filter "hacs"
3. Verify files: Terminal → `ls /config/custom_components/hacs`



## 📱 Quick Access Links

- **Home Assistant:** http://192.168.1.134:8123
- **GitHub Device Login:** https://github.com/login/device
- **HACS Docs:** https://hacs.xyz/
- **HACS Troubleshooting:** https://hacs.xyz/docs/issues



## ⚡ One-Line Installation (Copy-Paste)

If you have Terminal & SSH add-on open:

```bash
cd /config && wget -O - https://get.hacs.xyz | bash - && echo "✅ HACS installed! Now restart Home Assistant."
```



**Need help?** Check the full guide:
[docs/HACS-INSTALLATION-GUIDE.md](./HACS-INSTALLATION-GUIDE.md)

**Last Updated:** February 6, 2026
