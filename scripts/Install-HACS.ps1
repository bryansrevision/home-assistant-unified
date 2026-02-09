# HACS Installation Script for Home Assistant
# Downloads and installs HACS (Home Assistant Community Store)

param(
    [string]$HAConfigPath = "\\192.168.1.134\config",
    [switch]$SkipRestart
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🏪 HACS Installation Script                             ║" -ForegroundColor Cyan
Write-Host "║   Home Assistant Community Store                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Configuration
$hacsRepo = "hacs/integration"
$hacsApiUrl = "https://api.github.com/repos/$hacsRepo/releases/latest"
$customComponentsPath = Join-Path $HAConfigPath "custom_components"
$hacsPath = Join-Path $customComponentsPath "hacs"
$tempDir = Join-Path $env:TEMP "hacs-install"

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   HA Config Path: $HAConfigPath"
Write-Host "   HACS Target: $hacsPath"
Write-Host ""

# Check if HA config is accessible
if (-not (Test-Path $HAConfigPath)) {
    Write-Host "❌ Error: Cannot access Home Assistant config at $HAConfigPath" -ForegroundColor Red
    Write-Host "   Ensure network share is accessible or update -HAConfigPath parameter" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Home Assistant config path accessible" -ForegroundColor Green

# Check if HACS is already installed
if (Test-Path $hacsPath) {
    Write-Host "⚠️  HACS directory already exists at $hacsPath" -ForegroundColor Yellow
    $response = Read-Host "Do you want to reinstall/update HACS? (y/n)"
    if ($response -ne "y") {
        Write-Host "❌ Installation cancelled" -ForegroundColor Red
        exit 0
    }
    Write-Host "🗑️  Removing existing HACS installation..." -ForegroundColor Yellow
    Remove-Item -Path $hacsPath -Recurse -Force
}

# Create custom_components directory if needed
if (-not (Test-Path $customComponentsPath)) {
    Write-Host "📁 Creating custom_components directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $customComponentsPath -Force | Out-Null
}

# Get latest HACS release
Write-Host "🔍 Fetching latest HACS release from GitHub..." -ForegroundColor Cyan

try {
    $release = Invoke-RestMethod -Uri $hacsApiUrl -UseBasicParsing
    $version = $release.tag_name
    $downloadUrl = $release.assets | Where-Object { $_.name -eq "hacs.zip" } | Select-Object -ExpandProperty browser_download_url
    
    if (-not $downloadUrl) {
        throw "Could not find hacs.zip in release assets"
    }
    
    Write-Host "✅ Found HACS version: $version" -ForegroundColor Green
} catch {
    Write-Host "❌ Error fetching release info: $_" -ForegroundColor Red
    Write-Host "   Trying direct download URL..." -ForegroundColor Yellow
    $downloadUrl = "https://github.com/hacs/integration/releases/latest/download/hacs.zip"
    $version = "latest"
}

Write-Host "📥 Download URL: $downloadUrl" -ForegroundColor Cyan

# Create temp directory
if (Test-Path $tempDir) {
    Remove-Item -Path $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# Download HACS
$zipPath = Join-Path $tempDir "hacs.zip"
Write-Host "⬇️  Downloading HACS $version..." -ForegroundColor Cyan

try {
    $ProgressPreference = 'SilentlyContinue'  # Speed up download
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing
    Write-Host "✅ Download complete: $([math]::Round((Get-Item $zipPath).Length / 1MB, 2)) MB" -ForegroundColor Green
} catch {
    Write-Host "❌ Error downloading HACS: $_" -ForegroundColor Red
    exit 1
}

# Extract HACS
Write-Host "📦 Extracting HACS..." -ForegroundColor Cyan
$extractPath = Join-Path $tempDir "hacs"

try {
    Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
    Write-Host "✅ Extraction complete" -ForegroundColor Green
} catch {
    Write-Host "❌ Error extracting HACS: $_" -ForegroundColor Red
    exit 1
}

# Copy to custom_components
Write-Host "📂 Installing HACS to Home Assistant..." -ForegroundColor Cyan

try {
    # Check if extracted HACS has subdirectory structure
    $hacsFiles = Get-ChildItem -Path $extractPath
    
    if ($hacsFiles.Count -eq 1 -and $hacsFiles[0].PSIsContainer) {
        # HACS files are in subdirectory
        $sourcePath = $hacsFiles[0].FullName
    } else {
        # HACS files are at root of extraction
        $sourcePath = $extractPath
    }
    
    Copy-Item -Path $sourcePath -Destination $hacsPath -Recurse -Force
    Write-Host "✅ HACS installed to $hacsPath" -ForegroundColor Green
} catch {
    Write-Host "❌ Error copying HACS: $_" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host "🔍 Verifying installation..." -ForegroundColor Cyan

$manifestPath = Join-Path $hacsPath "manifest.json"
if (Test-Path $manifestPath) {
    $manifest = Get-Content $manifestPath | ConvertFrom-Json
    Write-Host "✅ HACS manifest found" -ForegroundColor Green
    Write-Host "   Domain: $($manifest.domain)" -ForegroundColor White
    Write-Host "   Version: $($manifest.version)" -ForegroundColor White
} else {
    Write-Host "⚠️  Warning: manifest.json not found at expected location" -ForegroundColor Yellow
}

# Cleanup
Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Cyan
Remove-Item -Path $tempDir -Recurse -Force
Write-Host "✅ Cleanup complete" -ForegroundColor Green

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅ HACS INSTALLATION COMPLETE                           ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Restart Home Assistant" -ForegroundColor White
Write-Host "      → Settings → System → Restart" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Add HACS Integration" -ForegroundColor White
Write-Host "      → Settings → Devices & Services → Add Integration" -ForegroundColor Gray
Write-Host "      → Search for 'HACS'" -ForegroundColor Gray
Write-Host ""
Write-Host "   3. Authenticate with GitHub" -ForegroundColor White
Write-Host "      → Follow the device activation flow" -ForegroundColor Gray
Write-Host "      → Visit: https://github.com/login/device" -ForegroundColor Gray
Write-Host ""
Write-Host "   4. Configure HACS" -ForegroundColor White
Write-Host "      → Select component types to track" -ForegroundColor Gray
Write-Host "      → Accept terms" -ForegroundColor Gray
Write-Host ""

if (-not $SkipRestart) {
    Write-Host "🔄 Would you like to trigger a Home Assistant restart now? (requires HA token)" -ForegroundColor Yellow
    $restart = Read-Host "Restart Home Assistant? (y/n)"
    
    if ($restart -eq "y") {
        Write-Host "🔄 Triggering restart..." -ForegroundColor Cyan
        
        # Load token from .env
        $envPath = "C:\Users\Dylan\Dev\.WorkSpace\HomeAssistant\home-assistant-unified\config\.env"
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
                Invoke-RestMethod -Uri "http://192.168.1.134:8123/api/services/homeassistant/restart" `
                    -Method POST -Headers $headers -Body "{}" | Out-Null
                Write-Host "✅ Restart triggered successfully" -ForegroundColor Green
                Write-Host "   Home Assistant will be back online in ~30-60 seconds" -ForegroundColor Gray
            } catch {
                Write-Host "⚠️  Could not trigger restart: $_" -ForegroundColor Yellow
                Write-Host "   Please restart manually via UI" -ForegroundColor Gray
            }
        } else {
            Write-Host "⚠️  No HA token found, please restart manually" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "📚 Documentation: docs/HACS-INSTALLATION-GUIDE.md" -ForegroundColor Cyan
Write-Host "🔗 HACS Website: https://hacs.xyz/" -ForegroundColor Cyan
Write-Host ""
