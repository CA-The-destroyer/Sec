<# 
 WinRAR Installer (defaults to your fixed 7.13 build)
 - Echoes default URL before download
 - Lets you override with a custom HTTP/HTTPS/FTP URL
 - Robust version detection (registry + uninstall + app paths + file version)
 - Post-install retry for registry settlement
 - Compatible with Windows PowerShell 5.1
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-Admin {
    ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).
      IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Try multiple strategies to find WinRAR's version + arch
function Get-WinRARInfo {
    $candidates = @(
        'HKLM:\SOFTWARE\WinRAR',
        'HKLM:\SOFTWARE\WOW6432Node\WinRAR',
        'HKCU:\SOFTWARE\WinRAR',
        'HKCU:\SOFTWARE\WOW6432Node\WinRAR',
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\WinRAR',
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\WinRAR'
    )

    foreach ($p in $candidates) {
        if (Test-Path $p) {
            try {
                $props = Get-ItemProperty -Path $p -ErrorAction SilentlyContinue
                if ($props) {
                    $ver = $null
                    if ($props.PSObject.Properties.Name -contains 'Version' -and $props.Version) { $ver = $props.Version }
                    if (-not $ver -and $props.PSObject.Properties.Name -contains 'DisplayVersion' -and $props.DisplayVersion) { $ver = $props.DisplayVersion }
                    if ($ver) {
                        $arch = if ($p -like '*WOW6432Node*') { 'x86' } else { 'x64' }
                        return [pscustomobject]@{ Version = $ver; Arch = $arch; Source = $p }
                    }
                }
            } catch {}
        }
    }

    # Fallback: scan Uninstall keys by DisplayName/Publisher
    $uninstallRoots = @(
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall',
        'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
        'HKCU:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
    )
    foreach ($root in $uninstallRoots) {
        if (-not (Test-Path $root)) { continue }
        foreach ($k in (Get-ChildItem -Path $root -ErrorAction SilentlyContinue)) {
            try {
                $p = Get-ItemProperty -Path $k.PSPath -ErrorAction SilentlyContinue
                if ($p -and ($p.DisplayName -like 'WinRAR*' -or $p.Publisher -like '*win.rar*')) {
                    $ver = $p.DisplayVersion
                    if ($ver) {
                        $arch = if ($k.PSPath -like '*WOW6432Node*') { 'x86' } else { 'x64' }
                        return [pscustomobject]@{ Version = $ver; Arch = $arch; Source = $k.PSPath }
                    }
                }
            } catch {}
        }
    }

    # Fallback: App Paths -> read file version of WinRAR.exe
    $appPaths = @(
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\WinRAR.exe',
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\WinRAR.exe',
        'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\WinRAR.exe',
        'HKCU:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\WinRAR.exe'
    )
    foreach ($ap in $appPaths) {
        if (Test-Path $ap) {
            try {
                $pp = Get-ItemProperty -Path $ap -ErrorAction SilentlyContinue
                $exe = $pp.'(Default)'; if (-not $exe) { $exe = $pp.Path }
                if (-not $exe -and $pp.PSObject.Properties.Name -contains 'Path') {
                    $exe = Join-Path $pp.Path 'WinRAR.exe'
                }
                if ($exe -and (Test-Path $exe)) {
                    $fi = Get-Item $exe
                    $ver = $fi.VersionInfo.ProductVersion
                    if ($ver) {
                        # infer arch from path
                        $arch = if ($exe -match '\\Program Files \(x86\)\\') { 'x86' } else { 'x64' }
                        return [pscustomobject]@{ Version = $ver; Arch = $arch; Source = $exe }
                    }
                }
            } catch {}
        }
    }

    # Last resort: check well-known install folders and read file version
    $guessPaths = @(
        "$env:ProgramFiles\WinRAR\WinRAR.exe",
        "${env:ProgramFiles(x86)}\WinRAR\WinRAR.exe"
    )
    foreach ($gp in $guessPaths) {
        if ($gp -and (Test-Path $gp)) {
            try {
                $fi = Get-Item $gp
                $ver = $fi.VersionInfo.ProductVersion
                if ($ver) {
                    $arch = if ($gp -match '\\Program Files \(x86\)\\') { 'x86' } else { 'x64' }
                    return [pscustomobject]@{ Version = $ver; Arch = $arch; Source = $gp }
                }
            } catch {}
        }
    }

    return $null
}

function Download-File {
    param(
        [Parameter(Mandatory)] [string]$SourceUrl,
        [Parameter(Mandatory)] [string]$Destination
    )
    $scheme = ([Uri]$SourceUrl).Scheme.ToLowerInvariant()
    if ($scheme -eq 'ftp') {
        $wc = New-Object System.Net.WebClient
        try { $wc.DownloadFile($SourceUrl, $Destination) }
        finally { $wc.Dispose() }
    } else {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $SourceUrl -OutFile $Destination -MaximumRedirection 5 -TimeoutSec 300
    }
}

# -------- Main --------
$osArch = if ([Environment]::Is64BitOperatingSystem) { 'x64' } else { 'x86' }

# Your fixed default (x64 7.13). If OS is 32-bit, use the x32 variant.
$defaultUrlX64 = 'https://www.win-rar.com/fileadmin/winrar-versions/winrar/winrar-x64-713.exe'
$defaultUrlX86 = $defaultUrlX64 -replace 'x64', 'x32'
$defaultUrl    = if ($osArch -eq 'x64') { $defaultUrlX64 } else { $defaultUrlX86 }

$installed = Get-WinRARInfo
if ($installed) {
    Write-Host ("WinRAR ({0}) is already installed: {1}" -f $installed.Arch, $installed.Version) -ForegroundColor Green
    return
}

if (-not (Test-Admin)) {
    throw "Installer requires elevation. Please run this PowerShell session as Administrator."
}

Write-Host ("WinRAR ({0}) is not installed." -f $osArch) -ForegroundColor Yellow
Write-Host ("Default download URL: {0}" -f $defaultUrl) -ForegroundColor Cyan
$urlChoice = Read-Host "Press Enter to use default, or paste a custom HTTP/HTTPS/FTP URL"
$url = if ([string]::IsNullOrWhiteSpace($urlChoice)) { $defaultUrl } else { $urlChoice }

if (-not [Uri]::IsWellFormedUriString($url, [UriKind]::Absolute)) {
    throw "The provided URL is not a valid absolute URI: $url"
}

Write-Host ("Downloading WinRAR from: {0}" -f $url) -ForegroundColor Cyan
$tmp = Join-Path $env:TEMP 'winrar_setup.exe'
try {
    Download-File -SourceUrl $url -Destination $tmp
} catch {
    throw "Download failed: $($_.Exception.Message)"
}

Write-Host "Installing WinRAR silently..." -ForegroundColor Cyan
try {
    $p = Start-Process -FilePath $tmp -ArgumentList '/S' -PassThru -Wait
    if ($p.ExitCode -ne 0) { throw "Installer exited with code $($p.ExitCode)" }
} catch {
    throw "Install failed: $($_.Exception.Message)"
} finally {
    try { if (Test-Path $tmp) { Remove-Item $tmp -Force } } catch {}
}

# Retry loop: give the registry a moment to catch up
$detected = $null
for ($i=0; $i -lt 10 -and -not $detected; $i++) {
    Start-Sleep -Milliseconds 800
    $detected = Get-WinRARInfo
}

if ($detected) {
    Write-Host ("WinRAR ({0}) installed successfully: {1}" -f $detected.Arch, $detected.Version) -ForegroundColor Green
    Write-Host ("Detected via: {0}" -f $detected.Source) -ForegroundColor DarkGray
} else {
    Write-Host "Installation completed, but version was not detected. Checked registry, uninstall entries, App Paths, and file version." -ForegroundColor Yellow
}
