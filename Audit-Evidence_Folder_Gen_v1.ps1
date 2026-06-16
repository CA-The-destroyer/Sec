<#
.SYNOPSIS
Creates audit evidence folder structure for controls C001 through C072.

.DESCRIPTION
Creates the Audit_evidence folder in the current working directory where the script is executed from.

.EXAMPLE
cd C:\temp\XXXXXXX
.\Create-AuditEvidenceStructure.ps1

Creates:
C:\temp\XXXXXXX\Audit_evidence
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$ParentPath = (Join-Path $PWD.ProviderPath "Audit_evidence"),

    [int]$StartControl = 1,

    [int]$EndControl = 72,

    [switch]$OverwriteManifest
)

$ErrorActionPreference = "Stop"

$SubFolders = @(
    "Population",
    "Policies",
    "Logs",
    "Approvals"
)

function New-FolderIfMissing {
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        if ($PSCmdlet.ShouldProcess($Path, "Create folder")) {
            New-Item -ItemType Directory -Path $Path -Force | Out-Null
        }
    }
}

function New-Manifest {
    param(
        [Parameter(Mandatory)]
        [string]$ControlId,

        [Parameter(Mandatory)]
        [string]$ManifestPath
    )

    if ((Test-Path -LiteralPath $ManifestPath) -and -not $OverwriteManifest) {
        return
    }

    $ManifestContent = @"
# $ControlId Audit Evidence Manifest

## Evidence Folders

| Folder | Purpose | Status | Notes |
|---|---|---:|---|
| Population | Source population, scoped systems, users, assets, or transactions | Pending | |
| Policies | Control policy, standard, procedure, or governance reference | Pending | |
| Logs | System logs, exports, screenshots, reports, or monitoring data | Pending | |
| Approvals | Approval records, sign-offs, exceptions, or review evidence | Pending | |

## Evidence Summary

- Control ID: $ControlId
- Prepared By:
- Review Period:
- Control Owner:
- Evidence Complete: No

## Reviewer Notes

-

## Change History

| Date | Change | Author |
|---|---|---|
| $(Get-Date -Format "yyyy-MM-dd") | Manifest created | PowerShell script |
"@

    if ($PSCmdlet.ShouldProcess($ManifestPath, "Create manifest")) {
        Set-Content -Path $ManifestPath -Value $ManifestContent -Encoding UTF8
    }
}

Write-Host "Creating audit evidence structure under: $ParentPath"

New-FolderIfMissing -Path $ParentPath

foreach ($Number in $StartControl..$EndControl) {
    $ControlId = "C{0:D3}" -f $Number
    $ControlPath = Join-Path $ParentPath $ControlId

    New-FolderIfMissing -Path $ControlPath

    foreach ($Folder in $SubFolders) {
        $FolderPath = Join-Path $ControlPath $Folder
        New-FolderIfMissing -Path $FolderPath
    }

    $ManifestPath = Join-Path $ControlPath "manifest.MD"
    New-Manifest -ControlId $ControlId -ManifestPath $ManifestPath
}

Write-Host "Completed audit evidence folder creation."
Write-Host "Created or validated: $ParentPath"