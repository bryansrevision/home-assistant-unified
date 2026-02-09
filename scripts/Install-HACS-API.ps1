# HACS Installation via Home Assistant API
# Downloads HACS and uploads via File System API

param(
    [string]$HAHost = "192.168.1.134",
    [string]$HAPort = "8123",
    [string]$Token = $env:HOME_ASSISTANT_TOKEN
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🏪 HACS Installation Script (API Method)               ║" -ForegroundColor Cyan
Write-Host "║   Home Assistant Community Store                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Load .env if token not provided
if (-not $Token) {
    $repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    $envPath = Join-Path $repoRoot "config\.env"
    
    if (Test-Path $envPath) {
        Write-Host "📄 Loading configuration from .env..." -ForegroundColor Cyan
        Get-Content $envPath | ForEach-Object {
            if ($_ -match '^\s*([^#=]+)=(.*)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
        $Token = $env:HOME_ASSISTANT_TOKEN
    }
}

if (-not $Token) {
    Write-Host "❌ Error: No Home Assistant token provided" -ForegroundColor Red
    Write-Host "   Set HOME_ASSISTANT_TOKEN environment variable or use -Token parameter" -ForegroundColor Yellow
    exit 1
}

$baseUrl = "http://${HAHost}:${HAPort}/api"
$headers = @{
    "Authorization" = "Bearer $Token"
    "Content-Type" = "application/json"
}

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   HA URL: http://${HAHost}:${HAPort}"
Write-Host ""

# Test connection
Write-Host "🔍 Testing Home Assistant connection..." -ForegroundColor Cyan

try {
    $config = Invoke-RestMethod -Uri "${baseUrl}/" -Headers $headers -UseBasicParsing
    Write-Host "✅ Connected to Home Assistant $($config.version)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Cannot connect to Home Assistant" -ForegroundColor Red
    Write-Host "   $_" -ForegroundColor Yellow
    exit 1
}

# Download HACS
$tempDir = Join-Path $env:TEMP "hacs-install"
$hacsZip = Join-Path $tempDir "hacs.zip"

Write-Host ""
Write-Host "📥 Downloading HACS from GitHub..." -ForegroundColor Cyan

try {
    if (Test-Path $tempDir) {
        Remove-Item -Path $tempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    
    $hacsUrl = "https://github.com/hacs/integration/releases/latest/download/hacs.zip"
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $hacsUrl -OutFile $hacsZip -UseBasicParsing
    
    Write-Host "✅ Downloaded: $([math]::Round((Get-Item $hacsZip).Length / 1MB, 2)) MB" -ForegroundColor Green
} catch {
    Write-Host "❌ Error downloading HACS: $_" -ForegroundColor Red
    exit 1
}

# Extract HACS
Write-Host "📦 Extracting HACS..." -ForegroundColor Cyan

$extractPath = Join-Path $tempDir "hacs"
Expand-Archive -Path $hacsZip -DestinationPath $extractPath -Force

Write-Host "✅ Extraction complete" -ForegroundColor Green

# Note: Home Assistant File Upload API is limited
# This method requires the File Editor add-on or SSH access
Write-Host ""
Write-Host "⚠️  CURRENT LIMITATION:" -ForegroundColor Yellow
Write-Host "   Home Assistant's REST API doesn't support direct file uploads" -ForegroundColor Gray
Write-Host "   to custom_components directory." -ForegroundColor Gray
Write-Host ""
Write-Host "📋 Alternative Installation Methods:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Method 1 (Recommended): SSH Installation" -ForegroundColor White
Write-Host "   ----------------------------------------" -ForegroundColor Gray
Write-Host "   Run: .\scripts\Install-HACS-SSH.ps1" -ForegroundColor Green
Write-Host ""
Write-Host "   Method 2: Manual via Terminal & SSH Add-on" -ForegroundColor White
Write-Host "   ------------------------------------------" -ForegroundColor Gray
Write-Host "   1. Open Terminal & SSH add-on in Home Assistant" -ForegroundColor Gray
Write-Host "   2. Run: cd /config" -ForegroundColor Gray
Write-Host "   3. Run: wget -O - https://get.hacs.xyz | bash -" -ForegroundColor Gray
Write-Host "   4. Restart Home Assistant" -ForegroundColor Gray
Write-Host ""
Write-Host "   Method 3: Manual via File Editor Add-on" -ForegroundColor White
Write-Host "   ---------------------------------------" -ForegroundColor Gray
Write-Host "   1. Download HACS from:" -ForegroundColor Gray
Write-Host "      https://github.com/hacs/integration/releases/latest" -ForegroundColor Gray
Write-Host "   2. Extract hacs.zip" -ForegroundColor Gray
Write-Host "   3. Use File Editor to create /config/custom_components/hacs/" -ForegroundColor Gray
Write-Host "   4. Upload all HACS files to that directory" -ForegroundColor Gray
Write-Host "   5. Restart Home Assistant" -ForegroundColor Gray
Write-Host ""

# Offer to open Home Assistant Terminal
Write-Host "Would you like to open the Home Assistant web interface?" -ForegroundColor Yellow
$response = Read-Host "Open browser? (y/n)"

if ($response -eq "y") {
    Start-Process "http://${HAHost}:${HAPort}"
    Write-Host "✅ Browser opened to Home Assistant" -ForegroundColor Green
}

# Cleanup
Remove-Item -Path $tempDir -Recurse -Force

Write-Host ""
Write-Host "📚 Documentation: docs/HACS-INSTALLATION-GUIDE.md" -ForegroundColor Cyan
Write-Host ""
