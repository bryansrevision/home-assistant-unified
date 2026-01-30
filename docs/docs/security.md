# Security Setup and Best Practices

## Overview

Security is critical for a home automation system. This document covers security setup and best practices for the Android-Home Automation integration.

## Network Security

### Tailscale VPN Setup

Tailscale provides secure, encrypted access to your home network from anywhere.

#### Installation on Proxmox Host/Containers

```bash
# Install Tailscale on Debian/Ubuntu-based containers
curl -fsSL https://tailscale.com/install.sh | sh

# Start Tailscale
sudo tailscale up

# Check status
sudo tailscale status

# Get IP address
sudo tailscale ip -4
```

#### Configuration

```bash
# Enable subnet routing (if needed)
sudo tailscale up --advertise-routes=192.168.1.0/24

# Enable exit node (optional)
sudo tailscale up --advertise-exit-node

# Set custom hostname
sudo tailscale up --hostname=home-automation
```

#### Access Control Lists (ACLs)

Configure Tailscale ACLs in your admin console:

```json
{
  "acls": [
    {
      "action": "accept",
      "src": ["group:android-devices"],
      "dst": [
        "home-assistant:8123",
        "mqtt-broker:1883",
        "mcp-hub:3000",
        "ai-automation:5000"
      ]
    }
  ],
  "groups": {
    "group:android-devices": ["user@example.com"]
  },
  "tagOwners": {
    "tag:home-automation": ["user@example.com"]
  }
}
```

### Firewall Configuration

#### Proxmox Firewall

```bash
# Enable Proxmox firewall
pvesh set /cluster/firewall/options -enable 1

# Allow specific ports
pvesh create /cluster/firewall/rules -type in -action ACCEPT -proto tcp -dport 8123 -comment "Home Assistant"
pvesh create /cluster/firewall/rules -type in -action ACCEPT -proto tcp -dport 3000 -comment "MCP Hub"
pvesh create /cluster/firewall/rules -type in -action ACCEPT -proto tcp -dport 5000 -comment "AI Automation"
pvesh create /cluster/firewall/rules -type in -action ACCEPT -proto tcp -dport 1883 -comment "MQTT"
```

#### Container/VM Firewall

```bash
# Using iptables
sudo iptables -A INPUT -p tcp --dport 8123 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 1883 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 3000 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5000 -s 192.168.1.0/24 -j ACCEPT

# Save rules
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

### Network Isolation

Best practices for network segmentation:

1. **IoT VLAN**: Separate VLAN for IoT devices
2. **Management VLAN**: Separate VLAN for Proxmox management
3. **Trusted VLAN**: Main network for authenticated devices

## Application Security

### Home Assistant Security

#### Strong Authentication

```yaml
# configuration.yaml
homeassistant:
  auth_providers:
    - type: homeassistant
    - type: trusted_networks
      trusted_networks:
        - 192.168.1.0/24
      allow_bypass_login: false
```

#### Enable MFA (Multi-Factor Authentication)

1. Navigate to Profile → Security
2. Enable Two-Factor Authentication
3. Scan QR code with authenticator app (Google Authenticator, Authy)
4. Save backup codes securely in Bitwarden

#### API Security

```yaml
# Long-Lived Access Tokens
# Generate from: Profile → Long-Lived Access Tokens
# Store in Bitwarden
# Use in API calls:
# Authorization: Bearer YOUR_TOKEN
```

#### SSL/TLS Configuration

```yaml
# configuration.yaml
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
  server_port: 8123
```

Generate self-signed certificate:
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /ssl/privkey.pem -out /ssl/fullchain.pem \
  -subj "/CN=192.168.1.201"
```

### MQTT Security

#### Authentication

```conf
# /etc/mosquitto/mosquitto.conf
allow_anonymous false
password_file /etc/mosquitto/passwd

# Enable ACLs
acl_file /etc/mosquitto/acl
```

#### Create Users

```bash
# Create password file
sudo mosquitto_passwd -c /etc/mosquitto/passwd homeassistant
sudo mosquitto_passwd /etc/mosquitto/passwd android_device
sudo mosquitto_passwd /etc/mosquitto/passwd zigbee2mqtt

# Restart Mosquitto
sudo systemctl restart mosquitto
```

#### Access Control Lists

```conf
# /etc/mosquitto/acl
# Home Assistant full access
user homeassistant
topic readwrite #

# Android device limited access
user android_device
topic read homeassistant/#
topic read zigbee2mqtt/#
topic write homeassistant/mobile_app/#

# Zigbee2MQTT
user zigbee2mqtt
topic readwrite zigbee2mqtt/#
topic read homeassistant/status
```

#### TLS Encryption

```conf
# /etc/mosquitto/mosquitto.conf
listener 8883
cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key
require_certificate false
tls_version tlsv1.2
```

### MCP Hub & AI Automation Security

#### API Key Authentication

```typescript
// MCP Hub authentication middleware
import { Request, Response, NextFunction } from 'express';

export const authenticateAPIKey = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const apiKey = req.headers['x-api-key'] || req.headers['authorization'];
  
  if (!apiKey || !isValidAPIKey(apiKey)) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  next();
};
```

```python
# AI Automation API key validation
from flask import request, jsonify
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('Authorization')
        if not api_key or not validate_api_key(api_key):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function
```

#### Rate Limiting

```typescript
// Express rate limiting
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests, please try again later.'
});

app.use('/api/', limiter);
```

## Credential Management with Bitwarden

### Self-Hosted Bitwarden (Vaultwarden)

Installation on Proxmox LXC:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Run Vaultwarden
docker run -d --name vaultwarden \
  -v /vw-data/:/data/ \
  -p 80:80 \
  -e SIGNUPS_ALLOWED=true \
  -e ADMIN_TOKEN=$(openssl rand -base64 48) \
  --restart unless-stopped \
  vaultwarden/server:latest
```

### Credential Storage

Store these credentials in Bitwarden:

1. **Home Assistant**
   - Username/Password
   - Long-lived access tokens
   - API keys

2. **MQTT**
   - Broker credentials
   - Client certificates (as attachments)

3. **Proxmox**
   - Root password
   - API tokens
   - Console passwords

4. **Tailscale**
   - Auth keys
   - API keys

5. **Android Device**
   - Lock screen PIN/Password
   - Biometric backup password

### Bitwarden Organization

Create collections:
- Home Automation
- Network Infrastructure
- API Keys
- Certificates

Share with family members as needed.

## Android Device Security

### Device Hardening

1. **Enable Full Disk Encryption**
   - Settings → Security → Encrypt Device

2. **Strong Lock Screen**
   - Use 6+ digit PIN or strong password
   - Enable fingerprint/face unlock as secondary

3. **Enable Remote Wipe**
   - Set up Find My Device
   - Configure remote wipe via Bitwarden

4. **App Permissions**
   - Review and limit app permissions
   - Use permission management tools

### App Security

#### Home Assistant App
- Enable app lock with biometric
- Use long-lived tokens, not password
- Enable SSL certificate validation

#### MQTT Client
- Use encrypted connections (port 8883)
- Enable certificate pinning
- Use client certificates

#### Bitwarden App
- Enable biometric unlock
- Set vault timeout
- Require master password for sensitive items

## Certificate Management

### Let's Encrypt (Optional)

If exposing services externally:

```bash
# Install certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone \
  -d your-domain.com \
  --preferred-challenges http

# Auto-renewal
sudo crontab -e
# Add: 0 0 * * * certbot renew --quiet
```

### Internal Certificate Authority

For internal use:

```bash
# Create CA
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt

# Create server certificate
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out server.crt

# Distribute ca.crt to Android devices
```

## Monitoring and Alerts

### Security Monitoring

```yaml
# Home Assistant security automations
automation:
  - alias: "Failed Login Attempt"
    trigger:
      - platform: state
        entity_id: persistent_notification.http_login
    action:
      - service: notify.mobile_app_android
        data:
          message: "Failed login attempt detected"
          title: "🔒 Security Alert"
          data:
            priority: high

  - alias: "New Device Connected"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
    action:
      - service: notify.mobile_app_android
        data:
          message: "New device connected to network"
```

### Log Monitoring

```bash
# Monitor authentication logs
tail -f /var/log/auth.log | grep -i failed

# Monitor Home Assistant logs
docker logs -f homeassistant | grep -i "Login attempt"

# Monitor MQTT connections
tail -f /var/log/mosquitto/mosquitto.log
```

## Backup and Recovery

### Encrypted Backups

```bash
# Backup with encryption
tar czf - /path/to/configs | \
  openssl enc -aes-256-cbc -e -out backup.tar.gz.enc \
  -pass file:/path/to/keyfile

# Restore
openssl enc -aes-256-cbc -d -in backup.tar.gz.enc \
  -pass file:/path/to/keyfile | tar xzf -
```

### CloudDataSync Security

- Enable encryption at rest
- Use secure transfer protocols (SFTP, FTPS)
- Implement retention policies
- Test recovery procedures regularly

## Incident Response

### Security Breach Procedure

1. **Identify**: Detect the breach
2. **Contain**: Isolate affected systems
3. **Eradicate**: Remove threat
4. **Recover**: Restore services
5. **Lessons Learned**: Document and improve

### Emergency Actions

```bash
# Disable user account
ha auth disable-user USERNAME

# Revoke all tokens
# Via Home Assistant UI: Profile → Security → Sessions

# Reset MQTT passwords
sudo mosquitto_passwd -D /etc/mosquitto/passwd android_device

# Disconnect Tailscale
sudo tailscale down
```

## Security Checklist

- [ ] Tailscale VPN configured and tested
- [ ] Home Assistant MFA enabled
- [ ] MQTT authentication configured
- [ ] SSL/TLS enabled on all services
- [ ] Firewall rules configured
- [ ] Bitwarden set up with all credentials
- [ ] Android device encrypted
- [ ] App permissions reviewed
- [ ] Backup encryption enabled
- [ ] Monitoring and alerts configured
- [ ] Incident response plan documented
- [ ] Regular security audits scheduled

## Additional Resources

- [Tailscale Best Practices](https://tailscale.com/kb/1017/install/)
- [Home Assistant Security](https://www.home-assistant.io/docs/configuration/securing/)
- [MQTT Security](https://mosquitto.org/man/mosquitto-conf-5.html)
- [Android Security Guide](https://source.android.com/security)
