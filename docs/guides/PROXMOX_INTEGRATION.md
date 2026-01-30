# Proxmox VE Integration Guide

## Overview

This guide covers the setup and configuration of Proxmox VE integration with the HOME-AI-AUTOMATION system. The integration allows you to monitor and control Proxmox VE virtual machines and containers directly from Home Assistant and the automation system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Authentication Setup](#authentication-setup)
3. [Configuration](#configuration)
4. [API Endpoints](#api-endpoints)
5. [Home Assistant Integration](#home-assistant-integration)
6. [Webhook Setup](#webhook-setup)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Proxmox VE server running on your network
- Administrative access to Proxmox VE
- Network connectivity between HOME-AI-AUTOMATION and Proxmox VE
- Home Assistant (optional, for enhanced integration)

---

## Authentication Setup

### Method 1: API Token (Recommended)

API tokens provide secure, granular access control without exposing your root password.

**Steps:**

1. **Log into Proxmox VE Web Interface**
   - Navigate to `https://your-proxmox-host:8006`

2. **Create API Token**
   - Go to: `Datacenter` → `Permissions` → `API Tokens`
   - Click `Add`
   - Fill in:
     - **User**: `root@pam` (or your user)
     - **Token ID**: `homeautomation` (or any name)
     - **Privilege Separation**: Uncheck if you want full permissions
   - Click `Add`
   - **Important**: Copy the token secret immediately (shown only once)

3. **Set Permissions** (if privilege separation is enabled)
   - Go to: `Datacenter` → `Permissions`
   - Add permissions for your token:
     - **Path**: `/`
     - **User**: `root@pam!homeautomation`
     - **Role**: `Administrator` (or `VM.Audit` for read-only)

4. **Configure in `.env`**
   ```bash
   PROXMOX_HOST=192.168.1.100
   PROXMOX_PORT=8006
   PROXMOX_VERIFY_SSL=false
   PROXMOX_TOKEN_ID=root@pam!homeautomation
   PROXMOX_TOKEN_SECRET=your-token-secret-here
   PROXMOX_NODE=pve
   ```

### Method 2: Username/Password

Less secure but simpler for testing.

**Configuration:**
```bash
PROXMOX_HOST=192.168.1.100
PROXMOX_PORT=8006
PROXMOX_VERIFY_SSL=false
PROXMOX_USERNAME=root@pam
PROXMOX_PASSWORD=your-password
PROXMOX_NODE=pve
```

---

## Configuration

### Environment Variables

Edit your `.env` file:

```bash
# Proxmox VE Configuration
PROXMOX_HOST=192.168.1.100          # Proxmox server IP or hostname
PROXMOX_PORT=8006                    # Default Proxmox web port
PROXMOX_VERIFY_SSL=false             # Set to true if using valid SSL cert
PROXMOX_NODE=pve                     # Default node name

# Authentication Method 1: API Token (Recommended)
PROXMOX_TOKEN_ID=root@pam!homeautomation
PROXMOX_TOKEN_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Authentication Method 2: Username/Password (Alternative)
PROXMOX_USERNAME=root@pam
PROXMOX_PASSWORD=your_password
```

### Testing Connection

Start the application and test the connection:

```bash
# Test Proxmox connection
curl http://localhost:5000/api/proxmox/connection
```

Expected response:
```json
{
  "success": true,
  "message": "Connected to Proxmox VE",
  "version": "8.0",
  "release": "8.0-4"
}
```

---

## API Endpoints

### Connection Test

**GET** `/api/proxmox/connection`

Test connectivity to Proxmox VE server.

**Response:**
```json
{
  "success": true,
  "message": "Connected to Proxmox VE",
  "version": "8.0",
  "release": "8.0-4"
}
```

### List Nodes

**GET** `/api/proxmox/nodes`

Get all nodes in the Proxmox cluster.

**Response:**
```json
{
  "success": true,
  "nodes": [
    {
      "node": "pve",
      "status": "online",
      "cpu": 0.05,
      "maxcpu": 8,
      "mem": 8589934592,
      "maxmem": 33719476224
    }
  ]
}
```

### Get All Resources

**GET** `/api/proxmox/resources`

Get all cluster resources (nodes, VMs, containers).

**Response:**
```json
{
  "success": true,
  "resources": [
    {
      "id": "qemu/100",
      "type": "qemu",
      "vmid": 100,
      "name": "home-assistant",
      "status": "running",
      "node": "pve"
    }
  ]
}
```

### Get VM Status

**GET** `/api/proxmox/vm/<vmid>?node=pve`

Get status of a specific VM.

**Example:**
```bash
curl "http://localhost:5000/api/proxmox/vm/100?node=pve"
```

**Response:**
```json
{
  "success": true,
  "status": {
    "status": "running",
    "cpu": 0.05,
    "mem": 2147483648,
    "maxmem": 4294967296,
    "uptime": 86400
  }
}
```

### Control VM

**POST** `/api/proxmox/vm/<vmid>`

Start, stop, or restart a VM.

**Request Body:**
```json
{
  "action": "start",  // or "stop", "restart"
  "node": "pve"       // optional if PROXMOX_NODE is set
}
```

**Examples:**

```bash
# Start VM 100
curl -X POST http://localhost:5000/api/proxmox/vm/100 \
  -H "Content-Type: application/json" \
  -d '{"action": "start", "node": "pve"}'

# Stop VM 100
curl -X POST http://localhost:5000/api/proxmox/vm/100 \
  -H "Content-Type: application/json" \
  -d '{"action": "stop", "node": "pve"}'

# Restart VM 100
curl -X POST http://localhost:5000/api/proxmox/vm/100 \
  -H "Content-Type: application/json" \
  -d '{"action": "restart", "node": "pve"}'
```

### Control Container

**POST** `/api/proxmox/container/<vmid>`

Start or stop an LXC container.

**Request Body:**
```json
{
  "action": "start",  // or "stop"
  "node": "pve"
}
```

---

## Home Assistant Integration

### Using Official Proxmox VE Integration

1. **Install via HACS** (recommended):
   - Open HACS in Home Assistant
   - Go to Integrations
   - Search for "Proxmox VE"
   - Install the integration

2. **Configure in Home Assistant**:
   - Go to: Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Proxmox VE"
   - Enter your Proxmox details:
     - Host: `192.168.1.100`
     - Username: `root@pam`
     - Password/Token: Your credentials
     - Port: `8006`
     - Verify SSL: `false`

### Using Custom Proxmox VE Integration

For enhanced features (VM control, failed task monitoring):

1. **Install Custom Integration**:
   ```bash
   cd /config/custom_components
   git clone https://github.com/dougiteixeira/proxmoxve.git proxmoxve
   ```

2. **Restart Home Assistant**

3. **Configure as above**

### Binary Sensors

After configuration, Home Assistant will create binary sensors for each VM/container:
- `binary_sensor.pve_vm_100` - Shows if VM 100 is running
- `binary_sensor.pve_lxc_101` - Shows if container 101 is running

### Controlling VMs from Home Assistant

Use the `proxmoxve.start_vm` and `proxmoxve.stop_vm` services:

```yaml
# Example automation
automation:
  - alias: "Start Home Assistant VM on boot"
    trigger:
      - platform: homeassistant
        event: start
    action:
      - service: proxmoxve.start_vm
        data:
          vm_id: 100
```

---

## Webhook Setup

### Creating Webhooks in Home Assistant

Webhooks allow Proxmox events to trigger Home Assistant automations.

**Steps:**

1. **Create Automation in Home Assistant**:
   - Go to: Settings → Automations & Scenes
   - Click "Create Automation"
   - Select "Start with an empty automation"
   - Add Trigger: "Webhook"
   - Set Webhook ID: `proxmox_vm_start` (example)
   - Add actions as desired

2. **Get Webhook URL**:
   - Format: `http://your-ha-url:8123/api/webhook/proxmox_vm_start`
   - Or use: `https://your-nabu-casa-url/api/webhook/proxmox_vm_start`

3. **Configure Webhook in HOME-AI-AUTOMATION**:
   ```bash
   WEBHOOK_SECRET=your_secret_key_here
   ```

4. **Test Webhook**:
   ```bash
   curl -X POST http://localhost:5000/api/webhook/proxmox_vm_start \
     -H "Content-Type: application/json" \
     -H "X-Webhook-Secret: your_secret_key_here" \
     -d '{"vmid": 100, "action": "start", "status": "success"}'
   ```

### Webhook Data Structure

```json
{
  "vmid": 100,
  "action": "start|stop|restart",
  "status": "success|failure",
  "timestamp": "2024-01-27T10:00:00Z",
  "node": "pve",
  "message": "VM started successfully"
}
```

---

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to Proxmox VE

**Solutions**:
1. Verify Proxmox is accessible: `curl -k https://192.168.1.100:8006`
2. Check firewall rules allow port 8006
3. Verify authentication credentials
4. Check Proxmox is running: `systemctl status pve-cluster`

### Authentication Failures

**Problem**: "Authentication failed" error

**Solutions**:
1. **For API Token**: Verify token ID and secret are correct
2. **For Username/Password**: Check credentials in Proxmox
3. Ensure user has required permissions (VM.Audit minimum)
4. Check token hasn't expired

### SSL Certificate Errors

**Problem**: SSL verification errors

**Solutions**:
1. Set `PROXMOX_VERIFY_SSL=false` in `.env`
2. Or install valid SSL certificate on Proxmox
3. Or add Proxmox cert to system trust store

### Permission Denied

**Problem**: "Permission denied" when controlling VMs

**Solutions**:
1. Ensure API token has `Administrator` role or `VM.PowerMgmt` privilege
2. Check user permissions in Proxmox: Datacenter → Permissions
3. If using privilege separation, ensure token has correct roles

### VM Not Found

**Problem**: "VM not found" error

**Solutions**:
1. Verify VMID is correct
2. Check VM exists on specified node
3. Ensure VM hasn't been migrated to another node
4. List all resources: `curl http://localhost:5000/api/proxmox/resources`

---

## Advanced Features

### Failed Task Monitoring

Monitor Proxmox tasks that failed in the last 24 hours (requires custom integration):

```python
# Check via automation engine
tasks = proxmox_client.get_cluster_resources()
failed_tasks = [t for t in tasks if t.get('type') == 'task' and t.get('status') == 'failed']
```

### Resource Monitoring

Monitor CPU, memory, and disk usage:

```bash
# Get node status
curl "http://localhost:5000/api/proxmox/resources"
```

### Integration with Glances

For hardware monitoring (CPU temp, disk I/O), integrate with Glances:

1. Install Glances on Proxmox node
2. Configure Glances to export metrics
3. Use Home Assistant Glances integration

---

## Security Best Practices

1. **Use API Tokens**: More secure than username/password
2. **Limit Permissions**: Grant minimum required privileges
3. **Enable SSL**: Use valid certificates in production
4. **Rotate Tokens**: Periodically regenerate API tokens
5. **Network Segmentation**: Keep Proxmox on isolated VLAN
6. **Webhook Secrets**: Always use secrets for webhook validation

---

## Support

For issues or questions:
- **Proxmox Documentation**: https://pve.proxmox.com/wiki/Main_Page
- **Home Assistant Integration**: https://www.home-assistant.io/integrations/proxmoxve/
- **GitHub Issues**: https://github.com/bryansrevision/HOME-AI-AUTOMATION/issues

---

**Implementation Status**: ✅ **COMPLETE** - Proxmox VE integration fully implemented and tested!
