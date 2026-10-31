Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-Sha256([string]$Path) {
    # .NET avoids command auto-loading differences between PowerShell 5.1 and 7.
    $stream = [IO.File]::OpenRead($Path)
    $hasher = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($hasher.ComputeHash($stream))).Replace('-','').ToLowerInvariant() }
    finally { $hasher.Dispose(); $stream.Dispose() }
}

function Get-SkillRoot([string]$InstallRoot) {
    if (-not $InstallRoot) {
        $profileDir = [Environment]::GetFolderPath('UserProfile')
        if (-not $profileDir) { $profileDir = $HOME }
        $InstallRoot = Join-Path $profileDir '.agents\skills'
    }
    return [IO.Path]::GetFullPath($InstallRoot)
}
function Assert-Manifest([string]$Root, [string]$Manifest, [string[]]$Ignore = @()) {
    $Root = [IO.Path]::GetFullPath($Root)
    $prefix = $Root.TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar
    $data = Get-Content -LiteralPath $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json
    $expected = @{}
    foreach ($entry in $data.files) {
        $p = [IO.Path]::GetFullPath((Join-Path $Root $entry.path))
        if (-not $p.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Manifest path escapes root.' }
        if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { throw "Missing file: $($entry.path)" }
        if ((Get-Sha256 $p) -ne $entry.sha256) { throw "Hash mismatch: $($entry.path)" }
        $expected[$entry.path.Replace('\','/')] = $true
    }
    foreach ($item in Get-ChildItem -LiteralPath $Root -Force -Recurse) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse points are not supported in package or installation.' }
        if (-not $item.PSIsContainer) {
            $rel = $item.FullName.Substring($prefix.Length).Replace('\','/')
            if (-not $expected.ContainsKey($rel) -and $Ignore -notcontains $rel) { throw "Unexpected file: $rel" }
        }
    }
    return @($data.files).Count
}
function Get-ReaderPython([string]$PythonPath) {
    $candidates = @()
    if ($PythonPath) { $candidates += @{exe=$PythonPath; args=@()} }
    else {
        foreach ($name in @('python','py','python3')) {
            $command = Get-Command $name -ErrorAction SilentlyContinue
            if ($command) {
                $prefixArgs = @(); if ($name -eq 'py') { $prefixArgs = @('-3') }
                $candidates += @{exe=$command.Source; args=$prefixArgs}
            }
        }
    }
    foreach ($candidate in $candidates) {
        try {
            $pythonArgs = @($candidate.args) + @('-c','import sys,json; print(json.dumps(dict(version=sys.version.split()[0],executable=sys.executable,ok=sys.version_info>=(3,9) and __debug__)))')
            $raw = & $candidate.exe @pythonArgs 2>$null
            if ($LASTEXITCODE -eq 0) {
                $info = ($raw -join "`n") | ConvertFrom-Json
                if ($info.ok) { return @{exe=$info.executable; args=@(); version=$info.version} }
            }
        } catch { }
    }
    throw 'Python 3.9+ in normal mode was not found. Install Python from python.org, or pass -PythonPath. Reader needs only the standard library.'
}
