[CmdletBinding()]
param([string]$InstallRoot, [string]$PythonPath)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\common.ps1')
$root = Get-SkillRoot $InstallRoot
$target = Join-Path $root 'biomed-paper-reader'
$payload = Join-Path $PSScriptRoot 'skill\biomed-paper-reader'
$checked = Assert-Manifest $PSScriptRoot (Join-Path $PSScriptRoot 'SHA256SUMS.json') @('SHA256SUMS.json','biomed-paper-reader-v1.0-portable.zip','biomed-paper-reader-v1.0-portable.zip.sha256')
$version = (Get-Content -LiteralPath (Join-Path $payload 'version.json') -Raw | ConvertFrom-Json).version
$python = Get-ReaderPython $PythonPath
if (Test-Path -LiteralPath $target) {
    $existing = 'unknown'
    try { $existing = (Get-Content -LiteralPath (Join-Path $target 'version.json') -Raw | ConvertFrom-Json).version } catch { }
    try { $count = Assert-Manifest $target (Join-Path $payload 'skill-manifest.json') @('skill-manifest.json')
        if ((Get-Sha256 (Join-Path $target 'skill-manifest.json')) -ne (Get-Sha256 (Join-Path $payload 'skill-manifest.json'))) { throw 'Installed manifest differs.' }
    } catch { throw "Target exists (version $existing), with different or unverifiable contents. Nothing overwritten. Back up and explicitly relocate the existing directory before retrying. Details: $_" }
    Write-Output "Already installed and identical: $version ($count files). No files changed."
} else {
    New-Item -ItemType Directory -Path $root -Force | Out-Null
    $stage = Join-Path $root ('.biomed-paper-reader-stage-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $stage | Out-Null
    Get-ChildItem -LiteralPath $payload -Force | Copy-Item -Destination $stage -Recurse
    $count = Assert-Manifest $stage (Join-Path $payload 'skill-manifest.json') @('skill-manifest.json')
    # Both resolved absolute paths must remain inside the explicit install root.
    $prefix = $root.TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar
    foreach ($p in @($stage,$target)) {
        if (-not ([IO.Path]::GetFullPath($p)).StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe install path.' }
    }
    if (Test-Path -LiteralPath $target) { throw 'Target appeared during installation; staging directory retained, nothing overwritten.' }
    Move-Item -LiteralPath $stage -Destination $target
    Write-Output "Installed $version at $target. Python $($python.version)."
}
& (Join-Path $PSScriptRoot 'verify-install.ps1') -InstallRoot $root -PythonPath $python.exe
