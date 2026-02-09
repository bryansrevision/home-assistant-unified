<# 
.SYNOPSIS
    Updates IP addresses across the Home Assistant repository
.DESCRIPTION
    Replaces old IP addresses with new ones in all configuration files
.PARAMETER OldIP
    The IP address to replace
.PARAMETER NewIP
    The new IP address
.PARAMETER DryRun
    Preview changes without modifying files
.EXAMPLE
    .\update-ip-addresses.ps1 -OldIP "192.168.1.201" -NewIP "192.168.1.134"
    .\update-ip-addresses.ps1 -OldIP "192.168.1.134" -NewIP "192.168.1.150" -DryRun
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$OldIP,
    
    [Parameter(Mandatory=$true)]
    [string]$NewIP,
    
    [switch]$DryRun
)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not $RepoRoot) { $RepoRoot = (Get-Location).Path }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Home Assistant IP Address Updater" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository: $RepoRoot"
Write-Host "Replacing:  $OldIP -> $NewIP"
if ($DryRun) { Write-Host "Mode:       DRY RUN (no changes)" -ForegroundColor Yellow }
Write-Host ""

# File patterns to search
$FilePatterns = @(
    "*.yaml",
    "*.yml", 
    "*.py",
    "*.json",
    "*.env",
    "*.sh",
    "*.ps1",
    "*.md"
)

# Directories to search
$SearchDirs = @(
    "config",
    "integrations",
    "mcp-servers",
    "scripts",
    "core",
    "dashboards",
    "automations"
)

$TotalFiles = 0
$ModifiedFiles = 0
$TotalReplacements = 0

foreach ($dir in $SearchDirs) {
    $DirPath = Join-Path $RepoRoot $dir
    if (-not (Test-Path $DirPath)) { continue }
    
    foreach ($pattern in $FilePatterns) {
        $Files = Get-ChildItem -Path $DirPath -Filter $pattern -Recurse -ErrorAction SilentlyContinue
        
        foreach ($file in $Files) {
            $TotalFiles++
            $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
            if (-not $content) { continue }
            
            $matches = [regex]::Matches($content, [regex]::Escape($OldIP))
            if ($matches.Count -gt 0) {
                $relativePath = $file.FullName.Replace($RepoRoot, "").TrimStart("\", "/")
                
                if ($DryRun) {
                    Write-Host "  [WOULD UPDATE] $relativePath ($($matches.Count) occurrences)" -ForegroundColor Yellow
                } else {
                    $newContent = $content -replace [regex]::Escape($OldIP), $NewIP
                    Set-Content -Path $file.FullName -Value $newContent -NoNewline
                    Write-Host "  [UPDATED] $relativePath ($($matches.Count) replacements)" -ForegroundColor Green
                }
                
                $ModifiedFiles++
                $TotalReplacements += $matches.Count
            }
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Files scanned:    $TotalFiles"
Write-Host "Files modified:   $ModifiedFiles"
Write-Host "Total changes:    $TotalReplacements"

if ($DryRun -and $ModifiedFiles -gt 0) {
    Write-Host ""
    Write-Host "Run without -DryRun to apply changes" -ForegroundColor Yellow
}

if (-not $DryRun -and $ModifiedFiles -gt 0) {
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Review changes: git diff"
    Write-Host "  2. Commit: git add -A && git commit -m 'config: Update IP from $OldIP to $NewIP'"
    Write-Host "  3. Push: git push origin master"
    Write-Host "  4. Sync to HA: python scripts/align-server.py sync-push --type all"
}
