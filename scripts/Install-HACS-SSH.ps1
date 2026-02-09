# HACS Installation via SSH
# Installs HACS on remote Home Assistant server via SSH

param(
    [string]$HAHost = "192.168.1.134",
    [string]$SSHUser = "root",
    [switch]$SkipRestart,
    [string]$SSHKeyPath = ""
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🏪 HACS Installation Script (SSH Method)               ║" -ForegroundColor Cyan
Write-Host "║   Home Assistant Community Store                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   HA Host: $HAHost"
Write-Host "   SSH User: $SSHUser"
Write-Host ""

# Build SSH command options
$sshOptions = @()
if ($SSHKeyPath -and (Test-Path $SSHKeyPath)) {
    $sshOptions += "-i", $SSHKeyPath
}

# Test SSH connectivity
Write-Host "🔍 Testing SSH connection to $HAHost..." -ForegroundColor Cyan

try {
    $testCommand = "echo 'SSH connection successful'"
    $sshCmd = "ssh"
    $sshArgs = @($sshOptions) + @("${SSHUser}@${HAHost}", $testCommand)
    
    $result = & $sshCmd $sshArgs 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        throw "SSH connection failed"
    }
    
    Write-Host "✅ SSH connection successful" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Cannot connect via SSH to $HAHost" -ForegroundColor Red
    Write-Host "   $_" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   1. Ensure SSH is enabled on Home Assistant" -ForegroundColor Gray
    Write-Host "   2. Install 'Terminal & SSH' add-on if not installed" -ForegroundColor Gray
    Write-Host "   3. Check if you need to use -SSHKeyPath parameter" -ForegroundColor Gray
    Write-Host "   4. Try: ssh ${SSHUser}@${HAHost}" -ForegroundColor Gray
    exit 1
}

# Install HACS via SSH
Write-Host ""
Write-Host "📥 Downloading and installing HACS..." -ForegroundColor Cyan

$installScript = @"
set -e
cd /config
echo '🔍 Checking if HACS already exists...'
if [ -d 'custom_components/hacs' ]; then
    echo '⚠️  HACS directory exists, removing...'
    rm -rf custom_components/hacs
fi
echo '📥 Downloading HACS...'
wget -q -O - https://get.hacs.xyz | bash -
echo '✅ HACS installation complete'
if [ -f 'custom_components/hacs/manifest.json' ]; then
    echo '✅ Verified: HACS manifest found'
    cat custom_components/hacs/manifest.json | grep -o '\"version\": \"[^\"]*\"' || true
else
    echo '❌ Error: HACS manifest not found'
    exit 1
fi
"@

try {
    $sshArgs = @($sshOptions) + @("${SSHUser}@${HAHost}", $installScript)
    
    Write-Host "   Executing installation commands on remote server..." -ForegroundColor Gray
    $output = & ssh $sshArgs 2>&1
    
    # Display output
    $output | ForEach-Object {
        if ($_ -match '✅') {
            Write-Host $_ -ForegroundColor Green
        } elseif ($_ -match '⚠️|Warning') {
            Write-Host $_ -ForegroundColor Yellow
        } elseif ($_ -match '❌|Error') {
            Write-Host $_ -ForegroundColor Red
        } else {
            Write-Host $_ -ForegroundColor Gray
        }
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Installation failed with exit code $LASTEXITCODE"
    }
    
    Write-Host ""
    Write-Host "✅ HACS installed successfully to /config/custom_components/hacs" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error during installation: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅ HACS INSTALLATION COMPLETE                           ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# Restart Home Assistant
if (-not $SkipRestart) {
    Write-Host "🔄 Restarting Home Assistant..." -ForegroundColor Cyan
    
    # Load token from .env
    $repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    $envPath = Join-Path $repoRoot "config\.env"
    
    if (Test-Path $envPath) {
        Get-Content $envPath | ForEach-Object {
            if ($_ -match '^\s*([^#=]+)=(.*)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
    }
    
    $token = $env:HOME_ASSISTANT_TOKEN
    if ($token) {
        try {
            $headers = @{
                "Authorization" = "Bearer $token"
                "Content-Type" = "application/json"
            }
            $null = Invoke-RestMethod -Uri "http://${HAHost}:8123/api/services/homeassistant/restart" `
                -Method POST -Headers $headers -Body "{}" -UseBasicParsing
            Write-Host "✅ Restart triggered successfully" -ForegroundColor Green
            Write-Host "   Home Assistant will be back online in ~30-60 seconds" -ForegroundColor Gray
        } catch {
            Write-Host "⚠️  Could not trigger restart via API: $_" -ForegroundColor Yellow
            Write-Host "   Please restart manually via UI: Settings → System → Restart" -ForegroundColor Gray
        }
    } else {
        Write-Host "ℹ️  Please restart Home Assistant manually:" -ForegroundColor Cyan
        Write-Host "   Settings → System → Restart" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Wait for Home Assistant to restart (30-60 seconds)" -ForegroundColor White
Write-Host ""
Write-Host "   2. Add HACS Integration" -ForegroundColor White
Write-Host "      → http://192.168.1.134:8123" -ForegroundColor Gray
Write-Host "      → Settings → Devices & Services → Add Integration" -ForegroundColor Gray
Write-Host "      → Search for 'HACS'" -ForegroundColor Gray
Write-Host ""
Write-Host "   3. Authenticate with GitHub" -ForegroundColor White
Write-Host "      → Follow the device activation flow" -ForegroundColor Gray
Write-Host "      → Visit: https://github.com/login/device" -ForegroundColor Gray
Write-Host ""
Write-Host "   4. Configure HACS" -ForegroundColor White
Write-Host "      → Select: Integrations, Frontend, Themes" -ForegroundColor Gray
Write-Host "      → Accept terms" -ForegroundColor Gray
Write-Host ""
Write-Host "   5. Install Recommended Components" -ForegroundColor White
Write-Host "      → HACS → Integrations → Alexa Media Player" -ForegroundColor Gray
Write-Host "      → HACS → Frontend → button-card, card-mod" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation: docs/HACS-INSTALLATION-GUIDE.md" -ForegroundColor Cyan
Write-Host "🔗 HACS Website: https://hacs.xyz/" -ForegroundColor Cyan
Write-Host ""
