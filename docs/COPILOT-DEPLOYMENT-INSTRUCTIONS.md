# GitHub Copilot Deployment Instructions - Home Assistant Unified

## Purpose
This guide enables GitHub Copilot to deploy the home-assistant-unified
repository with automatic secret management from GitHub Secrets.

## Required GitHub Secrets
Configure these secrets in GitHub repository settings (Settings > Secrets and
variables > Actions):

### Core Secrets
- `OPENAI_API_KEY` - OpenAI API key for AI agent functionality
- `GOOGLE_API_KEY` - Google API key for calendar and services
- `HOME_ASSISTANT_TOKEN` - Home Assistant long-lived access token
- `GITHUB_TOKEN` - GitHub Personal Access Token (auto-provided by Actions)

### Azure/M365 Integration
- `AZURE_CLIENT_ID` - Azure Active Directory application client ID
- `AZURE_CLIENT_SECRET` - Azure AD application secret
- `AZURE_TENANT_ID` - Azure AD tenant ID
- `AZURE_SECRET_ID` - Azure secret identifier
- `SECRET_EXPIRES` - Secret expiration date

### Notification Services
- `NOTIFICATION_EMAIL` - Email for system notifications
- `AGENT_API_TOKEN` - API token for AI agent authentication

## Deployment Steps

### Step 1: Pre-Deployment Validation
```bash
# Ensure all required secrets are set in GitHub
gh secret list --repo bryansrevision/home-assistant-unified

# Verify Home Assistant is accessible
curl http://192.168.1.134:8123/api/ -H "Authorization: Bearer ${{ secrets.HOME_ASSISTANT_TOKEN }}"
```

### Step 2: Retrieve Secrets
```powershell
# Retrieve environment variables from GitHub Secrets (GitHub Actions auto-injects these)
$env:AZURE_CLIENT_ID = "${{ secrets.AZURE_CLIENT_ID }}"
$env:AZURE_TENANT_ID = "${{ secrets.AZURE_TENANT_ID }}"
$env:AZURE_CLIENT_SECRET = "${{ secrets.AZURE_CLIENT_SECRET }}"
$env:OPENAI_API_KEY = "${{ secrets.OPENAI_API_KEY }}"
$env:GOOGLE_API_KEY = "${{ secrets.GOOGLE_API_KEY }}"
$env:HOME_ASSISTANT_TOKEN = "${{ secrets.HOME_ASSISTANT_TOKEN }}"
```

### Step 3: Deploy Configuration Files
```powershell
# Update MCP configuration with GitHub Secrets
$mcpConfig = Get-Content config/mcp-m365-config.json -Raw
$mcpConfig = $mcpConfig -replace '\$\{\{ secrets\.AZURE_CLIENT_ID \}\}', $env:AZURE_CLIENT_ID
$mcpConfig = $mcpConfig -replace '\$\{\{ secrets\.AZURE_TENANT_ID \}\}', $env:AZURE_TENANT_ID
$mcpConfig = $mcpConfig -replace '\$\{\{ secrets\.AZURE_CLIENT_SECRET \}\}', $env:AZURE_CLIENT_SECRET
$mcpConfig | Out-File config/mcp-m365-config-live.json -Encoding UTF8

# Deploy to Home Assistant
# Copy configuration files to Home Assistant config directory
# Restart Home Assistant services
```

### Step 4: Verification
```powershell
# Test Azure MCP connection
npx @modelcontextprotocol/server-m365

# Test Home Assistant API
Invoke-RestMethod -Uri "http://192.168.1.134:8123/api/" `
  -Method GET `
  -Headers @{ "Authorization" = "Bearer $env:HOME_ASSISTANT_TOKEN" }
```

### Step 5: Multi-Service Connection Options

#### Option 1: GitHub Connections (Simplest for Dev/Staging)
Create `.github/connections/ha-services.yml`:
```yaml
connections:
  - name: home-assistant
    url: http://192.168.1.134:8123
    auth:
      type: bearer
      token: ${{ secrets.HOME_ASSISTANT_TOKEN }}
    healthCheck:
      endpoint: /api/
      interval: 30s
  
  - name: ai-agent
    url: http://localhost:5000
    auth:
      type: bearer
      token: ${{ secrets.AGENT_API_TOKEN }}
```

#### Option 2: MCP Hub Orchestration (Production)
```bash
# Start MCP Hub with all service connections
npx @modelcontextprotocol/hub start \
  --config config/mcp-hub-multi-service.json \
  --port 50051
```

#### Option 3: WebSocket Bridge (Real-Time Events)
```python
import asyncio
import websockets

async def listen_ha_events():
    uri = "ws://192.168.1.134:8123/api/websocket"
    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({
            "type": "auth",
            "access_token": os.getenv("HOME_ASSISTANT_TOKEN")
        }))
        # Listen for events...
```

#### Option 4: OAuth2/OIDC Federation (Azure → Services)
```yaml
# Azure OAuth2 token exchange for federated auth
oauth2:
  provider: azure-ad
  client_id: ${{ secrets.AZURE_CLIENT_ID }}
  client_secret: ${{ secrets.AZURE_CLIENT_SECRET }}
  tenant_id: ${{ secrets.AZURE_TENANT_ID }}
  scopes:
    - https://graph.microsoft.com/.default
```

#### Option 5: Kafka Event Bus (Distributed Systems)
```bash
# Start Kafka consumer for HA events
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic home-assistant-events
```

#### Option 6: NGINX API Gateway (Load Balancing)
```nginx
upstream ha_backend {
    server 192.168.1.134:8123;
}

upstream agent_backend {
    server localhost:5000;
}

server {
    listen 8080 ssl;
    location /ha/ {
        proxy_pass http://ha_backend/;
        proxy_set_header Authorization "Bearer ${{ secrets.HOME_ASSISTANT_TOKEN }}";
    }
    location /agent/ {
        proxy_pass http://agent_backend/;
    }
}
```

## Security Best Practices
⚠️ **CRITICAL**: Never commit secrets to source code
- ✅ Use GitHub Secrets exclusively
- ✅ Reference secrets via `${{ secrets.SECRET_NAME }}`
- ✅ Rotate secrets regularly
- ✅ Use least-privilege access tokens
- ❌ Never hardcode credentials in files
- ❌ Never commit .env files with real secrets

## Troubleshooting
- If secrets are missing: Check GitHub repository settings
- If connection fails: Verify network access to services
- If auth fails: Regenerate secrets and update GitHub Secrets
- If push blocked: GitHub Push Protection detected secrets in history—use this
  guide to clean them

## Related Documentation
- `GITHUB-SECRETS-SETUP-GUIDE.md` - How to configure secrets properly
- `MCP-CONNECTION-METHODS.md` - Detailed connection patterns (when created)
- `/config/mcp-m365-config.json` - MCP configuration template
- `/scripts/start-mcp-hub.ps1` - MCP Hub startup script


**Status**: Ready for production deployment with secure secret management **Last
Updated**: 2026-02-02
