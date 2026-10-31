[CmdletBinding()]
param([string]$InstallRoot, [string]$PythonPath, [string]$ProjectPath = (Get-Location).Path, [string]$Paper2AgentPath, [string]$ReportPath)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\common.ps1')
$packageFiles = Assert-Manifest $PSScriptRoot (Join-Path $PSScriptRoot 'SHA256SUMS.json') @('SHA256SUMS.json','biomed-paper-reader-v1.0-portable.zip','biomed-paper-reader-v1.0-portable.zip.sha256')
$root = Get-SkillRoot $InstallRoot
$target = Join-Path $root 'biomed-paper-reader'
$count = Assert-Manifest $target (Join-Path $PSScriptRoot 'skill\biomed-paper-reader\skill-manifest.json') @('skill-manifest.json')
if ((Get-Sha256 (Join-Path $target 'skill-manifest.json')) -ne (Get-Sha256 (Join-Path $PSScriptRoot 'skill\biomed-paper-reader\skill-manifest.json'))) { throw 'Installed manifest differs.' }
$python = Get-ReaderPython $PythonPath
$testArgs = @($python.args) + @((Join-Path $target 'scripts\smoke_test.py'))
$testText = & $python.exe @testArgs
if ($LASTEXITCODE -ne 0) { throw 'Synthetic generator test failed.' }
$testResult = ($testText -join "`n") | ConvertFrom-Json
$duplicates = @()
$upstreamCandidates = @((Join-Path $root 'paper2agent'))
$profileDir = [Environment]::GetFolderPath('UserProfile')
$userReader = ''
if ($profileDir) {
    $upstreamCandidates += Join-Path $profileDir '.codex\skills\paper2agent'
    $upstreamCandidates += Join-Path $profileDir '.agents\skills\paper2agent'
    $userReader = Join-Path $profileDir '.agents\skills\biomed-paper-reader\SKILL.md'
}
if ($Paper2AgentPath) { $upstreamCandidates = @($Paper2AgentPath) }
$dir = Get-Item -LiteralPath $ProjectPath
while ($dir) {
    $candidate = Join-Path $dir.FullName '.agents\skills\biomed-paper-reader\SKILL.md'
    if ((Test-Path -LiteralPath $candidate) -and $candidate -ne (Join-Path $target 'SKILL.md') -and $candidate -ne $userReader) { $duplicates += $candidate }
    if (-not $Paper2AgentPath) { $upstreamCandidates += Join-Path $dir.FullName '.agents\skills\paper2agent' }
    if (Test-Path -LiteralPath (Join-Path $dir.FullName '.git')) { break }
    $dir = $dir.Parent
}
$upstream = @($upstreamCandidates | Select-Object -Unique | Where-Object {
    (Test-Path -LiteralPath (Join-Path $_ 'SKILL.md')) -and
    (Test-Path -LiteralPath (Join-Path $_ 'paper2skill\SKILL.md')) -and
    (Test-Path -LiteralPath (Join-Path $_ 'paper2skill\scripts\paper_bundle.py'))
})
$upstreamStatus = 'missing_conditional_dependency'
if ($upstream.Count) { $upstreamStatus = 'entrypoints_found_not_runtime_tested' }
if (-not $upstream.Count) { Write-Warning 'Paper2Agent missing: new-PDF preparation is unavailable. Existing reviewed resources can still be used. See references/portable.md for trusted-source installation guidance.' }
if ($duplicates.Count) { Write-Warning 'Same-name project Skill found. Explicitly select the USER scope Portable SKILL.md; project files were not changed.' }
$report = [ordered]@{
    status='passed_software_checks_only'; version='1.0-portable.1'; install_path=$target;
    package_files=$packageFiles; installed_files=$count; python_version=$python.version;
    dependencies='standard_library_only'; synthetic_test=$testResult;
    same_name_project_skills=$duplicates; paper2agent_status=$upstreamStatus; paper2agent_paths=$upstream;
    discovery='filesystem_only_use_Codex_skill_selector_or_app_server_to_confirm';
    science='not_tested_no_real_paper_data'; second_physical_computer='not_tested'
}
$json = $report | ConvertTo-Json -Depth 8
if ($ReportPath) {
    $destination = [IO.Path]::GetFullPath($ReportPath)
    foreach ($protected in @($PSScriptRoot,$target)) {
        $prefix = ([IO.Path]::GetFullPath($protected)).TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar
        if ($destination.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) { throw 'Write verification reports outside package and installed Skill.' }
    }
    [IO.File]::WriteAllText($destination,$json,(New-Object Text.UTF8Encoding($false)))
}
Write-Output $json
