#!/usr/bin/env pwsh
<#
.SYNOPSIS
Home Assistant MCP Integration Setup Script
Initializes and aligns Home Assistant repository with live server

.DESCRIPTION
This script:
1. Verifies prerequisites
2. Loads environment variables
3. Initializes MCP integration
4. Performs initial sync
5. Validates alignment

.EXAMPLE
.\Initialize-MCPIntegration.ps1
.\Initialize-MCPIntegration.ps1 -FullSync
.\Initialize-MCPIntegration.ps1 -Verbose

.NOTES
Requires Python 3.8+ and Home Assistant token in config/.env
#>

param(
    [switch]$FullSync,
    [switch]$Verbose = $false,
    [string]$RepoPath = $PSScriptRoot
)

$ErrorActionPreference = "Stop"
$WarningPreference = if ($Verbose) { "Continue" } else { "SilentlyContinue" }

# Colors for output
$Colors = @{
    Success = "Green"
    Error   = "Red"
    Warning = "Yellow"
    Info    = "Cyan"
    Header  = "Magenta"
}

function Write-Header {
    param([string]$Message)
    Write-Host "`n" -ForegroundColor $Colors.Header
    Write-Host "=" * 70 -ForegroundColor $Colors.Header
    Write-Host $Message -ForegroundColor $Colors.Header
    Write-Host "=" * 70 -ForegroundColor $Colors.Header
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Colors.Success
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Colors.Error
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Colors.Warning
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $Colors.Info
}

# Main execution
try {
    Write-Header "🏠 Home Assistant MCP Integration Setup"
    
    # Step 1: Verify Python
    Write-Info "Checking Python installation..."
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command python3 -ErrorAction SilentlyContinue
    }
    
    if (-not $python) {
        Write-Error-Custom "Python not found. Please install Python 3.8+"
        exit 1
    }
    
    $pythonVersion = & $python.Source --version 2>&1
    Write-Success "Python found: $pythonVersion"
    
    # Step 2: Verify repository structure
    Write-Info "Verifying repository structure..."
    $requiredDirs = @(
        "core",
        "automations",
        "mcp-servers",
        "integrations",
        "config",
        "scripts",
        "logs"
    )
    
    $missingDirs = @()
    foreach ($dir in $requiredDirs) {
        $dirPath = Join-Path $RepoPath $dir
        if (-not (Test-Path $dirPath)) {
            $missingDirs += $dir
        }
    }
    
    if ($missingDirs.Count -gt 0) {
        Write-Warning-Custom "Missing directories: $($missingDirs -join ', ')"
    } else {
        Write-Success "Repository structure verified"
    }
    
    # Step 3: Check environment configuration
    Write-Info "Checking environment configuration..."
    $envFile = Join-Path $RepoPath "config\.env"
    
    if (-not (Test-Path $envFile)) {
        Write-Warning-Custom "config/.env not found"
        
        # Create from template
        $envExample = Join-Path $RepoPath "config\.env.example"
        if (Test-Path $envExample) {
            Write-Info "Creating .env from template..."
            Copy-Item $envExample $envFile
            Write-Info "Created config/.env - Please update with your credentials"
        }
    }
    
    # Load environment variables
    Write-Info "Loading environment configuration..."
    $envContent = Get-Content $envFile -ErrorAction SilentlyContinue
    if ($envContent) {
        foreach ($line in $envContent) {
            if ($line -match '^\s*([^#=]+)=(.*)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
        Write-Success "Environment variables loaded"
    }
    
    # Step 4: Verify Home Assistant token
    Write-Info "Verifying Home Assistant credentials..."
    $token = $env:HOME_ASSISTANT_TOKEN
    if (-not $token -or $token -eq "your_home_assistant_token_here") {
        Write-Error-Custom "HOME_ASSISTANT_TOKEN not configured in config/.env"
        Write-Info "Generate token in Home Assistant: Settings → Developer Tools → Create Long-Lived Access Token"
        exit 1
    }
    Write-Success "Home Assistant token configured"
    
    # Step 5: Install Python dependencies
    Write-Info "Checking Python dependencies..."
    $packages = @("aiohttp", "pyyaml", "python-dotenv")
    
    foreach ($package in $packages) {
        try {
            & $python.Source -c "import $($package.Replace('-', '_'))" 2>$null
            Write-Success "$package is installed"
        } catch {
            Write-Warning-Custom "$package not installed, installing..."
            & pip install $package --quiet
            Write-Success "$package installed"
        }
    }
    
    # Step 6: Initialize MCP Integration
    Write-Header "🚀 Initializing MCP Integration"
    
    $initScript = Join-Path $RepoPath "mcp-servers\init_mcp_integration.py"
    if (Test-Path $initScript) {
        Write-Info "Running MCP integration initialization..."
        & $python.Source $initScript
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "MCP integration initialized successfully"
        } else {
            Write-Warning-Custom "MCP integration initialization completed with warnings"
        }
    } else {
        Write-Error-Custom "MCP initialization script not found"
    }
    
    # Step 7: Perform initial sync
    if ($FullSync) {
        Write-Header "🔄 Performing Initial Synchronization"
        
        $alignScript = Join-Path $RepoPath "scripts\align-server.py"
        if (Test-Path $alignScript) {
            Write-Info "Syncing from server to repository..."
            & $python.Source $alignScript sync-pull --type all
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Repository synchronized with server"
            } else {
                Write-Warning-Custom "Sync completed with warnings"
            }
        } else {
            Write-Error-Custom "Alignment script not found"
        }
    }
    
    # Step 8: Run health check
    Write-Header "🏥 Running Health Check"
    
    $alignScript = Join-Path $RepoPath "scripts\align-server.py"
    if (Test-Path $alignScript) {
        & $python.Source $alignScript health-check
    }
    
    # Success summary
    Write-Header "✨ Setup Complete"
    
    Write-Success "MCP Integration is ready!"
    Write-Info "Next steps:"
    Write-Info ""
    Write-Info "1. Review and commit changes:"
    Write-Info "   git add -A"
    Write-Info "   git commit -m 'Add: MCP live server integration'"
    Write-Info ""
    Write-Info "2. Perform full sync with server:"
    Write-Info "   python scripts/align-server.py sync-pull --type all"
    Write-Info ""
    Write-Info "3. View MCP integration guide:"
    Write-Info "   more mcp-servers/MCP-LIVE-SERVER-INTEGRATION.md"
    Write-Info ""
    Write-Info "📚 Documentation: mcp-servers/MCP-LIVE-SERVER-INTEGRATION.md"
    Write-Info "🔧 Configuration: mcp-servers/home-assistant-live.yaml"
    Write-Info "📝 Status: mcp-servers/.integration-status.json"
    Write-Info ""
    
} catch {
    Write-Error-Custom "Setup failed: $_"
    Write-Info "Run with -Verbose flag for more details"
    exit 1
}
