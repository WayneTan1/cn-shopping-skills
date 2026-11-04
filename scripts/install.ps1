<#
.SYNOPSIS
Install this Windows shopping skill bundle into a selected Codex directory.
.DESCRIPTION
Inputs: PythonExecutable (Python 3.10+ command/path), CodexHomePath (optional
installation directory), SkipDependencies (copy/configuration-only mode).
Outputs: installation summary and JSON connection records in CodexHomePath.
Side effects: downloads npm/Python dependencies into this bundle, copies skills,
and moves existing matching skills into a timestamped local backup directory.
Does not edit existing MCP client configuration or launch browser services.
Throws on missing tools, dependency failures or unsafe destination paths.
.EXAMPLE
.\scripts\install.ps1 -PythonExecutable 'C:\Python312\python.exe'
.EXAMPLE
.\scripts\install.ps1 -CodexHomePath 'C:\Temp\shopping-skill-check' -SkipDependencies
.NOTES
Updated: 2026-11-04. Initial portable package installer.
Copyright: Zhenyu Guo, zhenyu.guo.cn@outlook.com
School of Electronic and Communication Engineering, Guangzhou University
#>
[CmdletBinding()]
param(
    [string] $PythonExecutable = 'python',
    [string] $CodexHomePath,
    [switch] $SkipDependencies
)

$ErrorActionPreference = 'Stop'
$packageRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$projectDir = Join-Path $packageRoot 'tools\shopping-browser'
$nodePath = (Get-Command node -CommandType Application -ErrorAction Stop).Source

if (-not $CodexHomePath) {
    $CodexHomePath = if ($env:CODEX_HOME) { $env:CODEX_HOME } else {
        Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex'
    }
}
$codexRoot = [IO.Path]::GetFullPath($CodexHomePath)
$skillsRoot = Join-Path $codexRoot 'skills'
$backupRoot = Join-Path $codexRoot ('skill-backups\' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))

if (-not $SkipDependencies) {
    & $PythonExecutable -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10+ required'"
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.10+ is required; use -PythonExecutable to select a real interpreter.' }
    $venvRoot = Join-Path $packageRoot 'tools\.venv-price-pilot'
    $venvPython = Join-Path $venvRoot 'Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $venvPython)) {
        & $PythonExecutable -m venv $venvRoot
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the isolated Price Pilot virtual environment.' }
    }
    & $venvPython -m pip install (Join-Path $packageRoot 'vendor\price-pilot')
    if ($LASTEXITCODE -ne 0) { throw 'Price Pilot installation failed.' }
    $npmPath = (Get-Command npm.cmd -CommandType Application -ErrorAction Stop).Source
    Push-Location -LiteralPath $projectDir
    try {
        & $npmPath ci --ignore-scripts --no-audit --no-fund
        if ($LASTEXITCODE -ne 0) { throw 'npm dependency installation failed.' }
    } finally { Pop-Location }
}

New-Item -ItemType Directory -Path $skillsRoot -Force | Out-Null
$skillsPrefix = $skillsRoot.TrimEnd([char[]]'\/') + [IO.Path]::DirectorySeparatorChar
$backupPrefix = $backupRoot.TrimEnd([char[]]'\/') + [IO.Path]::DirectorySeparatorChar
foreach ($skillName in @('cn-shopping-cart', 'cn-shopping-compare')) {
    $sourcePath = Join-Path $packageRoot ('skills\' + $skillName)
    $targetPath = [IO.Path]::GetFullPath((Join-Path $skillsRoot $skillName))
    $backupPath = [IO.Path]::GetFullPath((Join-Path $backupRoot $skillName))
    if (-not $targetPath.StartsWith($skillsPrefix, [StringComparison]::OrdinalIgnoreCase) -or
        -not $backupPath.StartsWith($backupPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'The resolved skill or backup path is outside its intended directory.'
    }
    if (-not (Test-Path -LiteralPath (Join-Path $sourcePath 'SKILL.md'))) {
        throw "Missing skill entry point: $skillName"
    }
    if (Test-Path -LiteralPath $targetPath) {
        New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
        Move-Item -LiteralPath $targetPath -Destination $backupPath
    }
    Copy-Item -LiteralPath $sourcePath -Destination $targetPath -Recurse
}

$serverPath = Join-Path $projectDir 'server.mjs'
$installRecord = [ordered]@{
    schemaVersion = 1
    installedAt = (Get-Date).ToString('o')
    packageRoot = $packageRoot
    projectDir = $projectDir
    nodePath = $nodePath
    serverPath = $serverPath
    skillsRoot = $skillsRoot
    dependenciesInstalledByThisRun = (-not $SkipDependencies.IsPresent)
}
$installRecord | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $codexRoot 'shopping-browser-install.json') -Encoding utf8
$mcpRecord = @{ mcpServers = @{ shopping_browser = @{ command = $nodePath; args = @($serverPath) } } }
$mcpRecord | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $codexRoot 'shopping-browser-mcp.json') -Encoding utf8
Write-Output "Installed shopping skills into $skillsRoot"
Write-Output "MCP entry point: $serverPath"
Write-Output "Connection example: $(Join-Path $codexRoot 'shopping-browser-mcp.json')"
if ($SkipDependencies) { Write-Warning 'Dependencies were skipped. Install them before starting the MCP service.' }
