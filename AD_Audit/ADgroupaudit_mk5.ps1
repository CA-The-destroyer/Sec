<#
.SYNOPSIS
    Search Active Directory groups from manual input or an input file, select discovered groups from a numbered menu, and optionally enumerate members.

.VERSION
    mk5

.DESCRIPTION
    Prompts whether to use an input file.
    If using an input file, prompts for the file path and optionally saves that location as the default.
    If not using an input file, prompts for a manual AD group name or partial group name.
    Searches Active Directory for matching groups.
    Displays discovered groups as a numbered menu.
    Prompts for selected group numbers such as 1,2,4 or ALL.
    Prompts whether to enumerate users/members of the selected groups.
    Can optionally replay the same operator inputs in non-interactive mode for Windows Scheduled Task runs.
    Can optionally prompt the operator to create a Windows Scheduled Task with the inputs from the current run.
    Echoes script logic and output to console during execution.
    Captures script logic, selected group result records, and member result records into one compiled CSV.

.INPUT FILE FORMAT
    Plain text file, one group search term per line.

    Example:
        Domain Admins
        VPN
        Finance
        App_Admin

    Blank lines and lines starting with # are ignored.

.REQUIREMENTS
    - RSAT Active Directory PowerShell module
    - Domain-joined machine or management workstation
    - Permission to read Active Directory group and user/member objects

.OUTPUT
    <launch location>\csv\AD_Group_Search_Compiled_mk5_<timestamp>.csv
    Or a custom CSV output folder selected by the operator.

.CONFIG
    Default input file path is saved to:
    C:\temp\ADgroupaudit_default_input_path.txt
#>

param(
    [ValidateSet("", "Manual", "File")]
    [string]$RunInputMode = "",

    [string]$RunInputFilePath = "",

    [string]$RunManualSearchInput = "",

    [string]$RunSelectedGroupNumbers = "",

    [ValidateSet("", "Y", "YES", "N", "NO", "Yes", "No")]
    [string]$RunEnumerateMembers = "",

    [string]$RunCsvOutputFolder = "",

    [switch]$NonInteractive,

    [switch]$SkipSchedulePrompt
)

# ============================================================
# Initialize Script
# ============================================================

$ScriptVersion = "mk5"
$ExecutionStart = Get-Date
$Timestamp = $ExecutionStart.ToString("yyyyMMdd_HHmmss")
$LaunchFolder = (Get-Location).Path
$DefaultCsvOutputFolder = Join-Path $LaunchFolder "csv"
$CsvOutputFolder = $DefaultCsvOutputFolder
$OutputFolder = $CsvOutputFolder
$DefaultInputPathConfig = Join-Path "C:\temp" "ADgroupaudit_default_input_path.txt"
$CompiledCsvPath = ""

$CompiledOutput = New-Object System.Collections.Generic.List[Object]

# Runtime values initialized for final summary safety
$InputMode = ""
$InputFilePath = ""
$SearchInputSummary = ""
$SelectedGroupNumbersNormalized = ""
$EnumerateMembersText = ""

# ============================================================
# Compiled Output Function
# ============================================================

function Add-CompiledRecord {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("LOGIC", "OUTPUT", "ERROR", "INFO", "WARNING", "INPUT_TERM", "DISCOVERED_GROUP", "GROUP_RESULT", "MEMBER_RESULT")]
        [string]$RecordType,

        [Parameter(Mandatory = $true)]
        [string]$Message,

        [string]$InputMode = "",
        [string]$InputFilePath = "",
        [string]$SearchInput = "",
        [string]$SelectedGroupNumbers = "",
        [string]$EnumerateMembers = "",

        # Group fields
        [object]$GroupMenuNumber = "",
        [string]$GroupName = "",
        [string]$GroupSamAccountName = "",
        [string]$GroupCategory = "",
        [string]$GroupScope = "",
        [string]$GroupDescription = "",
        [object]$GroupWhenCreated = "",
        [object]$GroupWhenChanged = "",
        [string]$GroupManagedBy = "",
        [string]$GroupDistinguishedName = "",

        # Member fields
        [string]$MemberName = "",
        [string]$MemberSamAccountName = "",
        [string]$MemberObjectClass = "",
        [string]$MemberUserPrincipalName = "",
        [string]$MemberEnabled = "",
        [string]$MemberMail = "",
        [string]$MemberTitle = "",
        [string]$MemberDepartment = "",
        [object]$MemberWhenCreated = "",
        [object]$MemberWhenChanged = "",
        [string]$MemberDistinguishedName = ""
    )

    $Now = Get-Date

    switch ($RecordType) {
        "LOGIC"           { Write-Host "[$RecordType] $Message" -ForegroundColor Cyan }
        "OUTPUT"          { Write-Host "[$RecordType] $Message" -ForegroundColor Green }
        "ERROR"           { Write-Host "[$RecordType] $Message" -ForegroundColor Red }
        "WARNING"         { Write-Host "[$RecordType] $Message" -ForegroundColor Yellow }
        "INPUT_TERM"      { Write-Host "[$RecordType] $Message" -ForegroundColor DarkCyan }
        "DISCOVERED_GROUP"{ Write-Host "[$RecordType] $Message" -ForegroundColor DarkCyan }
        "GROUP_RESULT"    { Write-Host "[$RecordType] $Message" -ForegroundColor Green }
        "MEMBER_RESULT"   { Write-Host "[$RecordType] $Message" -ForegroundColor Green }
        default           { Write-Host "[$RecordType] $Message" }
    }

    $CompiledOutput.Add([PSCustomObject]@{
        ScriptVersion             = $ScriptVersion
        ExecutionStartDateTime    = $ExecutionStart
        RecordDateTime            = $Now
        RecordType                = $RecordType
        Message                   = $Message

        InputMode                 = $InputMode
        InputFilePath             = $InputFilePath
        SearchInput               = $SearchInput
        SelectedGroupNumbers      = $SelectedGroupNumbers
        EnumerateMembers          = $EnumerateMembers

        GroupMenuNumber           = $GroupMenuNumber
        GroupName                 = $GroupName
        GroupSamAccountName       = $GroupSamAccountName
        GroupCategory             = $GroupCategory
        GroupScope                = $GroupScope
        GroupDescription          = $GroupDescription
        GroupWhenCreated          = $GroupWhenCreated
        GroupWhenChanged          = $GroupWhenChanged
        GroupManagedBy            = $GroupManagedBy
        GroupDistinguishedName    = $GroupDistinguishedName

        MemberName                = $MemberName
        MemberSamAccountName      = $MemberSamAccountName
        MemberObjectClass         = $MemberObjectClass
        MemberUserPrincipalName   = $MemberUserPrincipalName
        MemberEnabled             = $MemberEnabled
        MemberMail                = $MemberMail
        MemberTitle               = $MemberTitle
        MemberDepartment          = $MemberDepartment
        MemberWhenCreated         = $MemberWhenCreated
        MemberWhenChanged         = $MemberWhenChanged
        MemberDistinguishedName   = $MemberDistinguishedName
    })
}

# ============================================================
# Helper Function: Export On Exit/Error
# ============================================================

function Export-CompiledCsv {
    param(
        [string]$Reason = "Manual export"
    )

    try {
        Add-CompiledRecord `
            -RecordType "LOGIC" `
            -Message "Exporting compiled CSV. Reason: $Reason" `
            -InputMode $InputMode `
            -InputFilePath $InputFilePath `
            -SearchInput $SearchInputSummary `
            -SelectedGroupNumbers $SelectedGroupNumbersNormalized `
            -EnumerateMembers $EnumerateMembersText

        $CompiledOutput | Export-Csv -Path $CompiledCsvPath -NoTypeInformation -Encoding UTF8
        Write-Host "[OUTPUT] Compiled CSV exported successfully: $CompiledCsvPath" -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] Failed to export compiled CSV." -ForegroundColor Red
        Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ============================================================
# Helper Function: Parse Yes/No
# ============================================================

function Test-Yes {
    param(
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $false
    }

    return ($Value.Trim().ToUpperInvariant() -in @("Y", "YES"))
}

# ============================================================
# Helper Function: Resolve Output Directory
# ============================================================

function Resolve-OutputDirectory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DefaultPath,

        [Parameter(Mandatory = $true)]
        [string]$Purpose,

        [string]$NonInteractivePath = "",

        [switch]$UseNonInteractive
    )

    if ($UseNonInteractive) {
        if (-not [string]::IsNullOrWhiteSpace($NonInteractivePath)) {
            return $NonInteractivePath.Trim().Trim('"')
        }

        return $DefaultPath
    }

    $UseDefaultResponse = Read-Host "Use default $Purpose folder '$DefaultPath'? Type Y for yes or N for no"

    if (Test-Yes -Value $UseDefaultResponse) {
        return $DefaultPath
    }

    $CustomPath = Read-Host "Enter full path for $Purpose folder"

    if ([string]::IsNullOrWhiteSpace($CustomPath)) {
        Write-Host "[WARNING] No custom $Purpose folder entered. Using default: $DefaultPath" -ForegroundColor Yellow
        return $DefaultPath
    }

    return $CustomPath.Trim().Trim('"')
}

# ============================================================
# Helper Function: Parse Group Menu Selection
# ============================================================

function Resolve-GroupMenuSelection {
    param(
        [Parameter(Mandatory = $true)]
        [array]$MenuGroups,

        [Parameter(Mandatory = $true)]
        [string]$SelectionText
    )

    $SelectionText = $SelectionText.Trim()

    if ([string]::IsNullOrWhiteSpace($SelectionText)) {
        throw "No group selection was entered."
    }

    if ($SelectionText.ToUpperInvariant() -in @("A", "ALL", "*")) {
        return $MenuGroups
    }

    $RawParts = $SelectionText -split ","
    $RequestedNumbers = New-Object System.Collections.Generic.List[int]

    foreach ($RawPart in $RawParts) {
        $Part = $RawPart.Trim()

        if ([string]::IsNullOrWhiteSpace($Part)) {
            continue
        }

        $ParsedNumber = 0

        if (-not [int]::TryParse($Part, [ref]$ParsedNumber)) {
            throw "Invalid menu selection '$Part'. Use comma-separated numbers like 1,2,4 or type ALL."
        }

        if ($ParsedNumber -lt 1 -or $ParsedNumber -gt $MenuGroups.Count) {
            throw "Menu selection '$ParsedNumber' is outside the valid range of 1 through $($MenuGroups.Count)."
        }

        if (-not $RequestedNumbers.Contains($ParsedNumber)) {
            $RequestedNumbers.Add($ParsedNumber)
        }
    }

    if ($RequestedNumbers.Count -eq 0) {
        throw "No valid group numbers were selected."
    }

    $Selected = foreach ($Number in $RequestedNumbers) {
        $MenuGroups | Where-Object { $_.MenuNumber -eq $Number }
    }

    return $Selected
}

# ============================================================
# Helper Function: Read Search Terms from Input File
# ============================================================

function Get-SearchTermsFromInputFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -Path $Path -PathType Leaf)) {
        throw "Input file does not exist: $Path"
    }

    $Terms = Get-Content -Path $Path |
        ForEach-Object { $_.Trim() } |
        Where-Object {
            -not [string]::IsNullOrWhiteSpace($_) -and
            -not $_.StartsWith("#")
        } |
        Select-Object -Unique

    if (-not $Terms -or $Terms.Count -eq 0) {
        throw "Input file did not contain any usable group search terms. Blank lines and lines starting with # are ignored."
    }

    return @($Terms)
}

# ============================================================
# Helper Function: Quote Scheduled Task Arguments
# ============================================================

function ConvertTo-ScheduledTaskArgument {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    return '"' + ($Value -replace '"', '`"') + '"'
}

# ============================================================
# Helper Function: Create Scheduled Task
# ============================================================

function New-ADGroupAuditScheduledTaskFromCurrentInputs {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CurrentInputMode,

        [string]$CurrentInputFilePath = "",

        [string]$CurrentManualSearchInput = "",

        [Parameter(Mandatory = $true)]
        [string]$CurrentSelectedGroupNumbers,

        [Parameter(Mandatory = $true)]
        [string]$CurrentEnumerateMembers
    )

    if ([string]::IsNullOrWhiteSpace($PSCommandPath)) {
        Add-CompiledRecord -RecordType "WARNING" -Message "Scheduled task creation skipped because the script path could not be resolved."
        return
    }

    Add-CompiledRecord -RecordType "LOGIC" -Message "Prompting user whether to create a Windows Scheduled Task with the current run inputs." -InputMode $CurrentInputMode -InputFilePath $CurrentInputFilePath -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers -EnumerateMembers $CurrentEnumerateMembers

    $CreateTaskResponse = Read-Host "Do you want to create a scheduled task with these inputs? Type Y for yes or N for no"

    if (-not (Test-Yes -Value $CreateTaskResponse)) {
        Add-CompiledRecord -RecordType "OUTPUT" -Message "User chose not to create a scheduled task." -InputMode $CurrentInputMode -InputFilePath $CurrentInputFilePath -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers -EnumerateMembers $CurrentEnumerateMembers
        return
    }

    $DefaultTaskName = "ADgroupaudit_mk5_Daily"
    $TaskNameInput = Read-Host "Enter scheduled task name or press Enter for '$DefaultTaskName'"
    if ([string]::IsNullOrWhiteSpace($TaskNameInput)) {
        $TaskName = $DefaultTaskName
    }
    else {
        $TaskName = $TaskNameInput.Trim()
    }

    $DefaultRunTime = "08:00"
    $RunTimeInput = Read-Host "Enter daily run time in 24-hour HH:mm format or press Enter for $DefaultRunTime"
    if ([string]::IsNullOrWhiteSpace($RunTimeInput)) {
        $RunTimeInput = $DefaultRunTime
    }

    $RunTime = Get-Date
    if (-not [datetime]::TryParseExact($RunTimeInput.Trim(), "HH:mm", [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::None, [ref]$RunTime)) {
        Add-CompiledRecord -RecordType "ERROR" -Message "Scheduled task was not created because the run time '$RunTimeInput' is not valid. Use HH:mm, such as 08:00 or 17:30." -InputMode $CurrentInputMode -InputFilePath $CurrentInputFilePath -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers -EnumerateMembers $CurrentEnumerateMembers
        return
    }

    $ExistingTask = $null
    try {
        $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    }
    catch {
        $ExistingTask = $null
    }

    $ForceTaskCreation = $false
    if ($ExistingTask) {
        $OverwriteResponse = Read-Host "A scheduled task named '$TaskName' already exists. Overwrite it? Type Y for yes or N for no"
        if (-not (Test-Yes -Value $OverwriteResponse)) {
            Add-CompiledRecord -RecordType "WARNING" -Message "Scheduled task creation skipped because task '$TaskName' already exists and overwrite was not approved." -InputMode $CurrentInputMode -InputFilePath $CurrentInputFilePath -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers -EnumerateMembers $CurrentEnumerateMembers
            return
        }
        $ForceTaskCreation = $true
    }

    $ScriptPath = $PSCommandPath
    $ArgumentParts = @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        (ConvertTo-ScheduledTaskArgument -Value $ScriptPath),
        "-NonInteractive",
        "-SkipSchedulePrompt",
        "-RunInputMode",
        (ConvertTo-ScheduledTaskArgument -Value $CurrentInputMode),
        "-RunSelectedGroupNumbers",
        (ConvertTo-ScheduledTaskArgument -Value $CurrentSelectedGroupNumbers),
        "-RunEnumerateMembers",
        (ConvertTo-ScheduledTaskArgument -Value $CurrentEnumerateMembers),
        "-RunCsvOutputFolder",
        (ConvertTo-ScheduledTaskArgument -Value $CsvOutputFolder)
    )

    if ($CurrentInputMode -eq "File") {
        $ArgumentParts += @("-RunInputFilePath", (ConvertTo-ScheduledTaskArgument -Value $CurrentInputFilePath))
    }
    else {
        $ArgumentParts += @("-RunManualSearchInput", (ConvertTo-ScheduledTaskArgument -Value $CurrentManualSearchInput))
    }

    $TaskArguments = $ArgumentParts -join " "
    $CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

    Add-CompiledRecord -RecordType "LOGIC" -Message "Creating scheduled task '$TaskName' for user '$CurrentUser' to run daily at $($RunTime.ToString('HH:mm'))." -InputMode $CurrentInputMode -InputFilePath $CurrentInputFilePath -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers -EnumerateMembers $CurrentEnumerateMembers

    try {
        $NewActionCommand = Get-Command New-ScheduledTaskAction
        if ($NewActionCommand.Parameters.ContainsKey("WorkingDirectory")) {
            $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $TaskArguments -WorkingDirectory $LaunchFolder
        }
        else {
            Add-CompiledRecord -RecordType "WARNING" -Message "This host's ScheduledTasks module does not support -WorkingDirectory. The scheduled task will still use the explicit CSV output folder parameter." -InputMode $CurrentInputMode -InputFilePath $CurrentInputFilePath -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers -EnumerateMembers $CurrentEnumerateMembers
            $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $TaskArguments
        }
        $Trigger = New-ScheduledTaskTrigger -Daily -At $RunTime
        $Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
        $Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

        if ($ForceTaskCreation) {
            Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Runs ADgroupaudit_mk5.ps1 locally using saved non-interactive inputs." -Force | Out-Null
        }
        else {
            Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Runs ADgroupaudit_mk5.ps1 locally using saved non-interactive inputs." | Out-Null
        }

        Add-CompiledRecord -RecordType "OUTPUT" -Message "Scheduled task created successfully: $TaskName. The task runs locally, does not launch the dashboard, and uses the current audit inputs." -InputMode $CurrentInputMode -InputFilePath $CurrentInputFilePath -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers -EnumerateMembers $CurrentEnumerateMembers
        Write-Host ""
        Write-Host "Scheduled task created:" -ForegroundColor Green
        Write-Host "  Name:      $TaskName"
        Write-Host "  Schedule:  Daily at $($RunTime.ToString('HH:mm'))"
        Write-Host "  Script:    $ScriptPath"
        Write-Host "  User:      $CurrentUser"
        Write-Host ""
    }
    catch {
        Add-CompiledRecord -RecordType "ERROR" -Message "Failed to create scheduled task '$TaskName'. Error: $($_.Exception.Message)" -InputMode $CurrentInputMode -InputFilePath $CurrentInputFilePath -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers -EnumerateMembers $CurrentEnumerateMembers
    }
}

# ============================================================
# Helper Function: Create Input File from Manual Selection
# ============================================================

function New-InputFileFromSelectedGroups {
    param(
        [Parameter(Mandatory = $true)]
        [array]$CurrentSelectedGroups,

        [Parameter(Mandatory = $true)]
        [string]$CurrentSelectedGroupNumbers
    )

    if (-not $CurrentSelectedGroups -or $CurrentSelectedGroups.Count -eq 0) {
        Add-CompiledRecord -RecordType "WARNING" -Message "Input file creation skipped because no selected groups were available." -InputMode $InputMode -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers
        return
    }

    Add-CompiledRecord -RecordType "LOGIC" -Message "Prompting user whether to create an input file from the selected groups." -InputMode $InputMode -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers

    $CreateInputFileResponse = Read-Host "Do you want to create an input file from your selected groups? Type Y for yes or N for no"

    if (-not (Test-Yes -Value $CreateInputFileResponse)) {
        Add-CompiledRecord -RecordType "OUTPUT" -Message "User chose not to create an input file from selected groups." -InputMode $InputMode -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers
        return
    }

    $DefaultGeneratedInputPath = Join-Path $OutputFolder "ADgroupaudit_selected_groups_input_${ScriptVersion}_$Timestamp.txt"
    $GeneratedInputPathResponse = Read-Host "Enter path for generated input file or press Enter for '$DefaultGeneratedInputPath'"

    if ([string]::IsNullOrWhiteSpace($GeneratedInputPathResponse)) {
        $GeneratedInputPath = $DefaultGeneratedInputPath
    }
    else {
        $GeneratedInputPath = $GeneratedInputPathResponse.Trim().Trim('"')
    }

    try {
        $GeneratedInputFolder = Split-Path -Path $GeneratedInputPath -Parent
        if ([string]::IsNullOrWhiteSpace($GeneratedInputFolder)) {
            $GeneratedInputFolder = (Get-Location).Path
            $GeneratedInputPath = Join-Path $GeneratedInputFolder $GeneratedInputPath
        }

        if (-not (Test-Path -Path $GeneratedInputFolder)) {
            New-Item -Path $GeneratedInputFolder -ItemType Directory -Force | Out-Null
        }

        $SelectedGroupNames = @(
            $CurrentSelectedGroups |
                Sort-Object MenuNumber |
                ForEach-Object { $_.Name } |
                Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
                Select-Object -Unique
        )

        if (-not $SelectedGroupNames -or $SelectedGroupNames.Count -eq 0) {
            Add-CompiledRecord -RecordType "WARNING" -Message "Input file creation skipped because selected groups did not contain usable group names." -InputMode $InputMode -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers
            return
        }

        $InputFileLines = @(
            "# ADgroupaudit generated input file"
            "# ScriptVersion: $ScriptVersion"
            "# Generated: $(Get-Date)"
            "# Source manual search input: $SearchInputSummary"
            "# Selected group numbers: $CurrentSelectedGroupNumbers"
            "# One group search term per line. Blank lines and lines starting with # are ignored."
            ""
        ) + $SelectedGroupNames

        Set-Content -Path $GeneratedInputPath -Value $InputFileLines -Encoding UTF8 -ErrorAction Stop

        Add-CompiledRecord -RecordType "OUTPUT" -Message "Created input file from selected groups: $GeneratedInputPath" -InputMode $InputMode -InputFilePath $GeneratedInputPath -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers
        Write-Host ""
        Write-Host "Generated input file from selected groups:" -ForegroundColor Green
        Write-Host $GeneratedInputPath -ForegroundColor Green
        Write-Host ""

        $SaveGeneratedAsDefaultResponse = Read-Host "Save this generated input file as the default input path for future runs? Type Y for yes or N for no"
        if (Test-Yes -Value $SaveGeneratedAsDefaultResponse) {
            Set-Content -Path $DefaultInputPathConfig -Value $GeneratedInputPath -Encoding UTF8 -ErrorAction Stop
            Add-CompiledRecord -RecordType "OUTPUT" -Message "Saved generated input file path as default: $GeneratedInputPath" -InputMode $InputMode -InputFilePath $GeneratedInputPath -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers
            Write-Host "Saved generated input file as default input path." -ForegroundColor Green
        }
        else {
            Add-CompiledRecord -RecordType "OUTPUT" -Message "User chose not to save generated input file path as default." -InputMode $InputMode -InputFilePath $GeneratedInputPath -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers
        }
    }
    catch {
        Add-CompiledRecord -RecordType "ERROR" -Message "Failed to create input file from selected groups. Error: $($_.Exception.Message)" -InputMode $InputMode -SearchInput $SearchInputSummary -SelectedGroupNumbers $CurrentSelectedGroupNumbers
    }
}

# ============================================================
# Script Banner
# ============================================================

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Active Directory Group and Member Audit" -ForegroundColor Cyan
Write-Host " Input File Support and Numbered Selection" -ForegroundColor Cyan
Write-Host " Version: $ScriptVersion" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Add-CompiledRecord -RecordType "INFO" -Message "Script execution started."
Add-CompiledRecord -RecordType "INFO" -Message "Script version: $ScriptVersion"
Add-CompiledRecord -RecordType "INFO" -Message "Execution start time: $ExecutionStart"
if ($NonInteractive) {
    Add-CompiledRecord -RecordType "INFO" -Message "Non-interactive mode enabled for scheduled or automated execution."
}

Add-CompiledRecord -RecordType "INFO" -Message "Launch folder: $LaunchFolder"
Add-CompiledRecord -RecordType "LOGIC" -Message "Resolving CSV output folder."

$CsvOutputFolder = Resolve-OutputDirectory `
    -DefaultPath $DefaultCsvOutputFolder `
    -Purpose "compiled CSV output" `
    -NonInteractivePath $RunCsvOutputFolder `
    -UseNonInteractive:$NonInteractive

$OutputFolder = $CsvOutputFolder
$CompiledCsvPath = Join-Path $CsvOutputFolder "AD_Group_Search_Compiled_${ScriptVersion}_$Timestamp.csv"

Add-CompiledRecord -RecordType "INFO" -Message "Compiled CSV output folder: $CsvOutputFolder"
Add-CompiledRecord -RecordType "INFO" -Message "Compiled CSV path will be: $CompiledCsvPath"
Add-CompiledRecord -RecordType "INFO" -Message "Default input path config file: $DefaultInputPathConfig"

# ============================================================
# Ensure Output Folder Exists
# ============================================================

Add-CompiledRecord -RecordType "LOGIC" -Message "Checking whether compiled CSV output folder exists: $OutputFolder"

try {
    if (-not (Test-Path -Path $OutputFolder)) {
        Add-CompiledRecord -RecordType "LOGIC" -Message "Output folder does not exist. Creating folder."
        New-Item -Path $OutputFolder -ItemType Directory -Force | Out-Null
        Add-CompiledRecord -RecordType "OUTPUT" -Message "Created output folder: $OutputFolder"
    }
    else {
        Add-CompiledRecord -RecordType "OUTPUT" -Message "Output folder already exists: $OutputFolder"
    }
}
catch {
    Add-CompiledRecord -RecordType "ERROR" -Message "Failed to create or access output folder: $OutputFolder"
    Add-CompiledRecord -RecordType "ERROR" -Message $_.Exception.Message
    Export-CompiledCsv -Reason "Output folder failure"
    exit 1
}

# ============================================================
# Load Active Directory Module
# ============================================================

Add-CompiledRecord -RecordType "LOGIC" -Message "Checking for the Active Directory PowerShell module."

try {
    Import-Module ActiveDirectory -ErrorAction Stop
    Add-CompiledRecord -RecordType "OUTPUT" -Message "Active Directory module loaded successfully."
}
catch {
    Add-CompiledRecord -RecordType "ERROR" -Message "Failed to load the Active Directory PowerShell module."
    Add-CompiledRecord -RecordType "ERROR" -Message "Install RSAT Active Directory tools or run this from a domain management host."
    Add-CompiledRecord -RecordType "ERROR" -Message $_.Exception.Message
    Export-CompiledCsv -Reason "Active Directory module load failure"
    exit 1
}

# ============================================================
# Initial Prompt: Use Input File?
# ============================================================

Add-CompiledRecord -RecordType "LOGIC" -Message "Prompting user whether to use an input file."

if ($NonInteractive) {
    if ([string]::IsNullOrWhiteSpace($RunInputMode)) {
        Add-CompiledRecord -RecordType "ERROR" -Message "Non-interactive mode requires -RunInputMode Manual or -RunInputMode File."
        Export-CompiledCsv -Reason "Missing non-interactive input mode"
        exit 1
    }

    $InputMode = $RunInputMode
    Add-CompiledRecord -RecordType "OUTPUT" -Message "Non-interactive input mode supplied: $InputMode" -InputMode $InputMode
}
else {
    $UseInputFileResponse = Read-Host "Use an input file for group search terms? Type Y for yes or N for no"

    if (Test-Yes -Value $UseInputFileResponse) {
        $InputMode = "File"
    }
    else {
        $InputMode = "Manual"
    }

    Add-CompiledRecord -RecordType "OUTPUT" -Message "User selected input mode: $InputMode" -InputMode $InputMode
}

$SearchTerms = @()

# ============================================================
# File Input Path Flow
# ============================================================

if ($InputMode -eq "File") {
    Add-CompiledRecord -RecordType "LOGIC" -Message "Input file mode selected. Checking for saved default input file path." -InputMode $InputMode

    $DefaultInputPath = ""

    if ($NonInteractive) {
        $InputFilePath = $RunInputFilePath.Trim().Trim('"')

        if ([string]::IsNullOrWhiteSpace($InputFilePath)) {
            Add-CompiledRecord -RecordType "ERROR" -Message "Non-interactive file mode requires -RunInputFilePath." -InputMode $InputMode
            Export-CompiledCsv -Reason "Missing non-interactive input file path"
            exit 1
        }

        Add-CompiledRecord -RecordType "OUTPUT" -Message "Non-interactive input file path supplied: $InputFilePath" -InputMode $InputMode -InputFilePath $InputFilePath
    }
    elseif (Test-Path -Path $DefaultInputPathConfig -PathType Leaf) {
        try {
            $DefaultInputPath = (Get-Content -Path $DefaultInputPathConfig -Raw).Trim()
        }
        catch {
            Add-CompiledRecord -RecordType "WARNING" -Message "Could not read default input path config. Error: $($_.Exception.Message)" -InputMode $InputMode
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($DefaultInputPath)) {
        Add-CompiledRecord -RecordType "OUTPUT" -Message "Saved default input file path found: $DefaultInputPath" -InputMode $InputMode -InputFilePath $DefaultInputPath

        $UseDefaultPathResponse = Read-Host "Use saved default input file path '$DefaultInputPath'? Type Y for yes or N for no"

        if (Test-Yes -Value $UseDefaultPathResponse) {
            $InputFilePath = $DefaultInputPath
            Add-CompiledRecord -RecordType "OUTPUT" -Message "User chose to use saved default input file path." -InputMode $InputMode -InputFilePath $InputFilePath
        }
    }

    if ([string]::IsNullOrWhiteSpace($InputFilePath)) {
        Add-CompiledRecord -RecordType "LOGIC" -Message "Prompting user for input file path." -InputMode $InputMode

        $InputFilePath = Read-Host "Enter full path to input file"

        if ([string]::IsNullOrWhiteSpace($InputFilePath)) {
            Add-CompiledRecord -RecordType "ERROR" -Message "No input file path was entered. Script will exit." -InputMode $InputMode
            Export-CompiledCsv -Reason "No input file path"
            exit 1
        }

        $InputFilePath = $InputFilePath.Trim().Trim('"')

        Add-CompiledRecord -RecordType "OUTPUT" -Message "User entered input file path: $InputFilePath" -InputMode $InputMode -InputFilePath $InputFilePath

        $SaveDefaultResponse = Read-Host "Save this input file location as the default for future runs? Type Y for yes or N for no"

        if (Test-Yes -Value $SaveDefaultResponse) {
            try {
                Set-Content -Path $DefaultInputPathConfig -Value $InputFilePath -Encoding UTF8
                Add-CompiledRecord -RecordType "OUTPUT" -Message "Saved input file path as default: $InputFilePath" -InputMode $InputMode -InputFilePath $InputFilePath
            }
            catch {
                Add-CompiledRecord -RecordType "WARNING" -Message "Failed to save default input file path. Error: $($_.Exception.Message)" -InputMode $InputMode -InputFilePath $InputFilePath
            }
        }
        else {
            Add-CompiledRecord -RecordType "OUTPUT" -Message "User chose not to save input file path as default." -InputMode $InputMode -InputFilePath $InputFilePath
        }
    }

    Add-CompiledRecord -RecordType "LOGIC" -Message "Reading group search terms from input file." -InputMode $InputMode -InputFilePath $InputFilePath

    try {
        $SearchTerms = @(Get-SearchTermsFromInputFile -Path $InputFilePath)
        $SearchInputSummary = ($SearchTerms -join "; ")
        Add-CompiledRecord -RecordType "OUTPUT" -Message "Loaded $($SearchTerms.Count) group search term(s) from input file." -InputMode $InputMode -InputFilePath $InputFilePath -SearchInput $SearchInputSummary

        foreach ($Term in $SearchTerms) {
            Add-CompiledRecord -RecordType "INPUT_TERM" -Message "Input file search term loaded: $Term" -InputMode $InputMode -InputFilePath $InputFilePath -SearchInput $Term
        }
    }
    catch {
        Add-CompiledRecord -RecordType "ERROR" -Message "Failed to read input file. Error: $($_.Exception.Message)" -InputMode $InputMode -InputFilePath $InputFilePath
        Export-CompiledCsv -Reason "Input file read failure"
        exit 1
    }
}

# ============================================================
# Manual Input Flow
# ============================================================

if ($InputMode -eq "Manual") {
    Add-CompiledRecord -RecordType "LOGIC" -Message "Manual input mode selected. Prompting user for AD group name or partial group name." -InputMode $InputMode

    if ($NonInteractive) {
        $ManualSearchInput = $RunManualSearchInput.Trim()
        Add-CompiledRecord -RecordType "OUTPUT" -Message "Non-interactive manual search value supplied: $ManualSearchInput" -InputMode $InputMode -SearchInput $ManualSearchInput
    }
    else {
        $ManualSearchInput = Read-Host "Enter the AD group name or partial group name to search for"
    }

    if ([string]::IsNullOrWhiteSpace($ManualSearchInput)) {
        if ($NonInteractive) {
            Add-CompiledRecord -RecordType "ERROR" -Message "Non-interactive manual mode requires -RunManualSearchInput." -InputMode $InputMode
            Export-CompiledCsv -Reason "Missing non-interactive manual group input"
        }
        else {
            Add-CompiledRecord -RecordType "ERROR" -Message "No group name was entered. Script will exit." -InputMode $InputMode
            Export-CompiledCsv -Reason "No manual group input"
        }
        exit 1
    }

    $ManualSearchInput = $ManualSearchInput.Trim()
    $SearchTerms = @($ManualSearchInput)
    $SearchInputSummary = $ManualSearchInput

    if (-not $NonInteractive) {
        Add-CompiledRecord -RecordType "OUTPUT" -Message "User entered manual search value: $ManualSearchInput" -InputMode $InputMode -SearchInput $ManualSearchInput
    }
}

# ============================================================
# Search Active Directory Groups
# ============================================================

$AllDiscoveredGroups = @()
$SeenGroupDNs = @{}

foreach ($SearchTerm in $SearchTerms) {
    Add-CompiledRecord `
        -RecordType "LOGIC" `
        -Message "Preparing to search Active Directory groups where Name matches wildcard pattern: *$SearchTerm*" `
        -InputMode $InputMode `
        -InputFilePath $InputFilePath `
        -SearchInput $SearchTerm

    Add-CompiledRecord `
        -RecordType "LOGIC" `
        -Message "Executing Get-ADGroup search for search term: $SearchTerm" `
        -InputMode $InputMode `
        -InputFilePath $InputFilePath `
        -SearchInput $SearchTerm

    try {
        $Groups = Get-ADGroup `
            -Filter "Name -like '*$SearchTerm*'" `
            -Properties Name, SamAccountName, DistinguishedName, GroupCategory, GroupScope, Description, WhenCreated, WhenChanged, ManagedBy

        if ($Groups) {
            foreach ($Group in $Groups) {
                if (-not $SeenGroupDNs.ContainsKey($Group.DistinguishedName)) {
                    $SeenGroupDNs[$Group.DistinguishedName] = $true

                    $AllDiscoveredGroups += [PSCustomObject]@{
                        SourceSearchInput  = $SearchTerm
                        Name               = $Group.Name
                        SamAccountName     = $Group.SamAccountName
                        GroupCategory      = $Group.GroupCategory
                        GroupScope         = $Group.GroupScope
                        Description        = $Group.Description
                        WhenCreated        = $Group.WhenCreated
                        WhenChanged        = $Group.WhenChanged
                        ManagedBy          = $Group.ManagedBy
                        DistinguishedName  = $Group.DistinguishedName
                    }
                }
            }
        }

        $FoundCount = if ($Groups) { $Groups.Count } else { 0 }

        Add-CompiledRecord `
            -RecordType "OUTPUT" `
            -Message "Get-ADGroup search completed successfully for '$SearchTerm'. Matches found before deduplication: $FoundCount" `
            -InputMode $InputMode `
            -InputFilePath $InputFilePath `
            -SearchInput $SearchTerm
    }
    catch {
        Add-CompiledRecord -RecordType "ERROR" -Message "Failed while searching Active Directory groups for '$SearchTerm'." -InputMode $InputMode -InputFilePath $InputFilePath -SearchInput $SearchTerm
        Add-CompiledRecord -RecordType "ERROR" -Message $_.Exception.Message -InputMode $InputMode -InputFilePath $InputFilePath -SearchInput $SearchTerm
        Export-CompiledCsv -Reason "Group search failure"
        exit 1
    }
}

# ============================================================
# Build and Display Numbered Menu
# ============================================================

Add-CompiledRecord `
    -RecordType "LOGIC" `
    -Message "Checking whether any matching AD groups were found across all search terms." `
    -InputMode $InputMode `
    -InputFilePath $InputFilePath `
    -SearchInput $SearchInputSummary

if (-not $AllDiscoveredGroups -or $AllDiscoveredGroups.Count -eq 0) {
    Add-CompiledRecord `
        -RecordType "WARNING" `
        -Message "No AD groups found matching supplied search input." `
        -InputMode $InputMode `
        -InputFilePath $InputFilePath `
        -SearchInput $SearchInputSummary

    Export-CompiledCsv -Reason "No groups found"
    exit 0
}

Add-CompiledRecord `
    -RecordType "OUTPUT" `
    -Message "Found $($AllDiscoveredGroups.Count) unique matching AD group(s) across supplied search input." `
    -InputMode $InputMode `
    -InputFilePath $InputFilePath `
    -SearchInput $SearchInputSummary

$MenuGroups = @()
$MenuIndex = 1

foreach ($Group in ($AllDiscoveredGroups | Sort-Object Name)) {
    $MenuGroups += [PSCustomObject]@{
        MenuNumber        = $MenuIndex
        SourceSearchInput = $Group.SourceSearchInput
        Name              = $Group.Name
        SamAccountName    = $Group.SamAccountName
        GroupCategory     = $Group.GroupCategory
        GroupScope        = $Group.GroupScope
        Description       = $Group.Description
        WhenCreated       = $Group.WhenCreated
        WhenChanged       = $Group.WhenChanged
        ManagedBy         = $Group.ManagedBy
        DistinguishedName = $Group.DistinguishedName
    }

    Add-CompiledRecord `
        -RecordType "DISCOVERED_GROUP" `
        -Message "Discovered AD group menu item $MenuIndex`: $($Group.Name)" `
        -InputMode $InputMode `
        -InputFilePath $InputFilePath `
        -SearchInput $Group.SourceSearchInput `
        -GroupMenuNumber $MenuIndex `
        -GroupName $Group.Name `
        -GroupSamAccountName $Group.SamAccountName `
        -GroupCategory $Group.GroupCategory `
        -GroupScope $Group.GroupScope `
        -GroupDescription $Group.Description `
        -GroupWhenCreated $Group.WhenCreated `
        -GroupWhenChanged $Group.WhenChanged `
        -GroupManagedBy $Group.ManagedBy `
        -GroupDistinguishedName $Group.DistinguishedName

    $MenuIndex++
}

Write-Host ""
Write-Host "========== Discovered AD Groups ==========" -ForegroundColor Cyan
$MenuGroups |
    Select-Object MenuNumber, SourceSearchInput, Name, SamAccountName, GroupCategory, GroupScope, WhenCreated, WhenChanged |
    Format-Table -AutoSize

Write-Host ""
Write-Host "Select groups by number. Examples:" -ForegroundColor Yellow
Write-Host "  1" -ForegroundColor Yellow
Write-Host "  1,2,4" -ForegroundColor Yellow
Write-Host "  ALL" -ForegroundColor Yellow
Write-Host ""

Add-CompiledRecord `
    -RecordType "LOGIC" `
    -Message "Prompting user to select discovered groups by menu number." `
    -InputMode $InputMode `
    -InputFilePath $InputFilePath `
    -SearchInput $SearchInputSummary

if ($NonInteractive) {
    $SelectedGroupNumbersInput = $RunSelectedGroupNumbers
    Add-CompiledRecord `
        -RecordType "OUTPUT" `
        -Message "Non-interactive group menu selection supplied: $SelectedGroupNumbersInput" `
        -InputMode $InputMode `
        -InputFilePath $InputFilePath `
        -SearchInput $SearchInputSummary `
        -SelectedGroupNumbers $SelectedGroupNumbersInput
}
else {
    $SelectedGroupNumbersInput = Read-Host "Enter group number(s) to audit"
}

try {
    $SelectedGroups = @(Resolve-GroupMenuSelection -MenuGroups $MenuGroups -SelectionText $SelectedGroupNumbersInput)
}
catch {
    Add-CompiledRecord `
        -RecordType "ERROR" `
        -Message "Invalid group menu selection. $($_.Exception.Message)" `
        -InputMode $InputMode `
        -InputFilePath $InputFilePath `
        -SearchInput $SearchInputSummary `
        -SelectedGroupNumbers $SelectedGroupNumbersInput

    Export-CompiledCsv -Reason "Invalid group menu selection"
    exit 1
}

$SelectedGroupNumbersNormalized = ($SelectedGroups | Sort-Object MenuNumber | ForEach-Object { $_.MenuNumber }) -join ","

Add-CompiledRecord `
    -RecordType "OUTPUT" `
    -Message "User selected group menu number(s): $SelectedGroupNumbersNormalized" `
    -InputMode $InputMode `
    -InputFilePath $InputFilePath `
    -SearchInput $SearchInputSummary `
    -SelectedGroupNumbers $SelectedGroupNumbersNormalized

Write-Host ""
Write-Host "========== Selected AD Groups ==========" -ForegroundColor Cyan
$SelectedGroups |
    Sort-Object MenuNumber |
    Select-Object MenuNumber, SourceSearchInput, Name, SamAccountName, GroupCategory, GroupScope, WhenCreated, WhenChanged |
    Format-Table -AutoSize
Write-Host ""

# ============================================================
# Optional Input File Creation from Manual Selection
# ============================================================

if ($InputMode -eq "Manual" -and -not $NonInteractive) {
    New-InputFileFromSelectedGroups `
        -CurrentSelectedGroups $SelectedGroups `
        -CurrentSelectedGroupNumbers $SelectedGroupNumbersNormalized
}

# ============================================================
# Prompt for Member Enumeration
# ============================================================

Add-CompiledRecord `
    -RecordType "LOGIC" `
    -Message "Prompting user whether to enumerate users/members of selected groups." `
    -InputMode $InputMode `
    -InputFilePath $InputFilePath `
    -SearchInput $SearchInputSummary `
    -SelectedGroupNumbers $SelectedGroupNumbersNormalized

if ($NonInteractive) {
    $EnumerateMembersInput = $RunEnumerateMembers
    if ([string]::IsNullOrWhiteSpace($EnumerateMembersInput)) {
        $EnumerateMembersInput = "N"
    }
    Add-CompiledRecord `
        -RecordType "OUTPUT" `
        -Message "Non-interactive member enumeration value supplied: $EnumerateMembersInput" `
        -InputMode $InputMode `
        -InputFilePath $InputFilePath `
        -SearchInput $SearchInputSummary `
        -SelectedGroupNumbers $SelectedGroupNumbersNormalized
}
else {
    $EnumerateMembersInput = Read-Host "Show users/members of selected groups? Type Y for yes or N for no"
}

if ([string]::IsNullOrWhiteSpace($EnumerateMembersInput)) {
    $EnumerateMembersInput = "N"
}

if (Test-Yes -Value $EnumerateMembersInput) {
    $EnumerateMembers = $true
    $EnumerateMembersText = "Yes"
}
else {
    $EnumerateMembers = $false
    $EnumerateMembersText = "No"
}

Add-CompiledRecord `
    -RecordType "OUTPUT" `
    -Message "User selected member enumeration: $EnumerateMembersText" `
    -InputMode $InputMode `
    -InputFilePath $InputFilePath `
    -SearchInput $SearchInputSummary `
    -SelectedGroupNumbers $SelectedGroupNumbersNormalized `
    -EnumerateMembers $EnumerateMembersText

# ============================================================
# Record Selected Group Results
# ============================================================

Add-CompiledRecord `
    -RecordType "LOGIC" `
    -Message "Adding selected AD group objects to the compiled CSV output." `
    -InputMode $InputMode `
    -InputFilePath $InputFilePath `
    -SearchInput $SearchInputSummary `
    -SelectedGroupNumbers $SelectedGroupNumbersNormalized `
    -EnumerateMembers $EnumerateMembersText

foreach ($Group in ($SelectedGroups | Sort-Object MenuNumber)) {
    Add-CompiledRecord `
        -RecordType "GROUP_RESULT" `
        -Message "Selected AD group for audit: $($Group.Name)" `
        -InputMode $InputMode `
        -InputFilePath $InputFilePath `
        -SearchInput $Group.SourceSearchInput `
        -SelectedGroupNumbers $SelectedGroupNumbersNormalized `
        -EnumerateMembers $EnumerateMembersText `
        -GroupMenuNumber $Group.MenuNumber `
        -GroupName $Group.Name `
        -GroupSamAccountName $Group.SamAccountName `
        -GroupCategory $Group.GroupCategory `
        -GroupScope $Group.GroupScope `
        -GroupDescription $Group.Description `
        -GroupWhenCreated $Group.WhenCreated `
        -GroupWhenChanged $Group.WhenChanged `
        -GroupManagedBy $Group.ManagedBy `
        -GroupDistinguishedName $Group.DistinguishedName
}

# ============================================================
# Optional Member Enumeration
# ============================================================

if ($SelectedGroups -and $SelectedGroups.Count -gt 0 -and $EnumerateMembers) {
    Add-CompiledRecord `
        -RecordType "LOGIC" `
        -Message "Member enumeration selected. Beginning group member lookup for selected groups." `
        -InputMode $InputMode `
        -InputFilePath $InputFilePath `
        -SearchInput $SearchInputSummary `
        -SelectedGroupNumbers $SelectedGroupNumbersNormalized `
        -EnumerateMembers $EnumerateMembersText

    foreach ($Group in ($SelectedGroups | Sort-Object MenuNumber)) {
        Add-CompiledRecord `
            -RecordType "LOGIC" `
            -Message "Enumerating members for selected group: $($Group.Name)" `
            -InputMode $InputMode `
            -InputFilePath $InputFilePath `
            -SearchInput $Group.SourceSearchInput `
            -SelectedGroupNumbers $SelectedGroupNumbersNormalized `
            -EnumerateMembers $EnumerateMembersText `
            -GroupMenuNumber $Group.MenuNumber `
            -GroupName $Group.Name `
            -GroupSamAccountName $Group.SamAccountName `
            -GroupDistinguishedName $Group.DistinguishedName

        try {
            $Members = Get-ADGroupMember -Identity $Group.DistinguishedName -Recursive -ErrorAction Stop

            if (-not $Members -or $Members.Count -eq 0) {
                Add-CompiledRecord `
                    -RecordType "WARNING" `
                    -Message "No members found for selected group: $($Group.Name)" `
                    -InputMode $InputMode `
                    -InputFilePath $InputFilePath `
                    -SearchInput $Group.SourceSearchInput `
                    -SelectedGroupNumbers $SelectedGroupNumbersNormalized `
                    -EnumerateMembers $EnumerateMembersText `
                    -GroupMenuNumber $Group.MenuNumber `
                    -GroupName $Group.Name `
                    -GroupSamAccountName $Group.SamAccountName `
                    -GroupDistinguishedName $Group.DistinguishedName
            }
            else {
                Add-CompiledRecord `
                    -RecordType "OUTPUT" `
                    -Message "Found $($Members.Count) member(s) for selected group: $($Group.Name)" `
                    -InputMode $InputMode `
                    -InputFilePath $InputFilePath `
                    -SearchInput $Group.SourceSearchInput `
                    -SelectedGroupNumbers $SelectedGroupNumbersNormalized `
                    -EnumerateMembers $EnumerateMembersText `
                    -GroupMenuNumber $Group.MenuNumber `
                    -GroupName $Group.Name `
                    -GroupSamAccountName $Group.SamAccountName `
                    -GroupDistinguishedName $Group.DistinguishedName

                Write-Host ""
                Write-Host "========== Members for Group: $($Group.Name) ==========" -ForegroundColor Cyan

                $DisplayMembers = foreach ($Member in ($Members | Sort-Object Name)) {
                    [PSCustomObject]@{
                        Name              = $Member.Name
                        SamAccountName    = $Member.SamAccountName
                        ObjectClass       = $Member.ObjectClass
                        DistinguishedName = $Member.DistinguishedName
                    }
                }

                $DisplayMembers | Format-Table Name, SamAccountName, ObjectClass -AutoSize
                Write-Host ""

                foreach ($Member in ($Members | Sort-Object Name)) {
                    $DetailedMember = $null
                    $MemberUserPrincipalName = ""
                    $MemberEnabled = ""
                    $MemberMail = ""
                    $MemberTitle = ""
                    $MemberDepartment = ""
                    $MemberWhenCreated = ""
                    $MemberWhenChanged = ""

                    try {
                        if ($Member.ObjectClass -eq "user") {
                            $DetailedMember = Get-ADUser `
                                -Identity $Member.DistinguishedName `
                                -Properties UserPrincipalName, Enabled, Mail, Title, Department, WhenCreated, WhenChanged `
                                -ErrorAction Stop

                            $MemberUserPrincipalName = $DetailedMember.UserPrincipalName
                            $MemberEnabled = [string]$DetailedMember.Enabled
                            $MemberMail = $DetailedMember.Mail
                            $MemberTitle = $DetailedMember.Title
                            $MemberDepartment = $DetailedMember.Department
                            $MemberWhenCreated = $DetailedMember.WhenCreated
                            $MemberWhenChanged = $DetailedMember.WhenChanged
                        }
                        elseif ($Member.ObjectClass -eq "group") {
                            $DetailedMember = Get-ADGroup `
                                -Identity $Member.DistinguishedName `
                                -Properties WhenCreated, WhenChanged `
                                -ErrorAction Stop

                            $MemberWhenCreated = $DetailedMember.WhenCreated
                            $MemberWhenChanged = $DetailedMember.WhenChanged
                        }
                        else {
                            $DetailedMember = Get-ADObject `
                                -Identity $Member.DistinguishedName `
                                -Properties WhenCreated, WhenChanged `
                                -ErrorAction Stop

                            $MemberWhenCreated = $DetailedMember.WhenCreated
                            $MemberWhenChanged = $DetailedMember.WhenChanged
                        }
                    }
                    catch {
                        Add-CompiledRecord `
                            -RecordType "WARNING" `
                            -Message "Could not enrich member details for $($Member.Name). Basic member details will still be recorded. Error: $($_.Exception.Message)" `
                            -InputMode $InputMode `
                            -InputFilePath $InputFilePath `
                            -SearchInput $Group.SourceSearchInput `
                            -SelectedGroupNumbers $SelectedGroupNumbersNormalized `
                            -EnumerateMembers $EnumerateMembersText `
                            -GroupMenuNumber $Group.MenuNumber `
                            -GroupName $Group.Name `
                            -GroupSamAccountName $Group.SamAccountName `
                            -GroupDistinguishedName $Group.DistinguishedName `
                            -MemberName $Member.Name `
                            -MemberSamAccountName $Member.SamAccountName `
                            -MemberObjectClass $Member.ObjectClass `
                            -MemberDistinguishedName $Member.DistinguishedName
                    }

                    Add-CompiledRecord `
                        -RecordType "MEMBER_RESULT" `
                        -Message "Member found in selected group $($Group.Name): $($Member.Name)" `
                        -InputMode $InputMode `
                        -InputFilePath $InputFilePath `
                        -SearchInput $Group.SourceSearchInput `
                        -SelectedGroupNumbers $SelectedGroupNumbersNormalized `
                        -EnumerateMembers $EnumerateMembersText `
                        -GroupMenuNumber $Group.MenuNumber `
                        -GroupName $Group.Name `
                        -GroupSamAccountName $Group.SamAccountName `
                        -GroupDistinguishedName $Group.DistinguishedName `
                        -MemberName $Member.Name `
                        -MemberSamAccountName $Member.SamAccountName `
                        -MemberObjectClass $Member.ObjectClass `
                        -MemberUserPrincipalName $MemberUserPrincipalName `
                        -MemberEnabled $MemberEnabled `
                        -MemberMail $MemberMail `
                        -MemberTitle $MemberTitle `
                        -MemberDepartment $MemberDepartment `
                        -MemberWhenCreated $MemberWhenCreated `
                        -MemberWhenChanged $MemberWhenChanged `
                        -MemberDistinguishedName $Member.DistinguishedName
                }
            }
        }
        catch {
            Add-CompiledRecord `
                -RecordType "ERROR" `
                -Message "Failed to enumerate members for selected group $($Group.Name). Error: $($_.Exception.Message)" `
                -InputMode $InputMode `
                -InputFilePath $InputFilePath `
                -SearchInput $Group.SourceSearchInput `
                -SelectedGroupNumbers $SelectedGroupNumbersNormalized `
                -EnumerateMembers $EnumerateMembersText `
                -GroupMenuNumber $Group.MenuNumber `
                -GroupName $Group.Name `
                -GroupSamAccountName $Group.SamAccountName `
                -GroupDistinguishedName $Group.DistinguishedName
        }
    }
}
elseif ($SelectedGroups -and $SelectedGroups.Count -gt 0 -and -not $EnumerateMembers) {
    Add-CompiledRecord `
        -RecordType "INFO" `
        -Message "Member enumeration was not selected. Selected group results only were captured." `
        -InputMode $InputMode `
        -InputFilePath $InputFilePath `
        -SearchInput $SearchInputSummary `
        -SelectedGroupNumbers $SelectedGroupNumbersNormalized `
        -EnumerateMembers $EnumerateMembersText
}

# ============================================================
# Complete Script
# ============================================================

$ExecutionEnd = Get-Date
$Duration = $ExecutionEnd - $ExecutionStart

Add-CompiledRecord -RecordType "INFO" -Message "Script execution completed." -InputMode $InputMode -InputFilePath $InputFilePath -SearchInput $SearchInputSummary -SelectedGroupNumbers $SelectedGroupNumbersNormalized -EnumerateMembers $EnumerateMembersText
Add-CompiledRecord -RecordType "INFO" -Message "Execution end time: $ExecutionEnd" -InputMode $InputMode -InputFilePath $InputFilePath -SearchInput $SearchInputSummary -SelectedGroupNumbers $SelectedGroupNumbersNormalized -EnumerateMembers $EnumerateMembersText
Add-CompiledRecord -RecordType "INFO" -Message "Execution duration: $($Duration.ToString())" -InputMode $InputMode -InputFilePath $InputFilePath -SearchInput $SearchInputSummary -SelectedGroupNumbers $SelectedGroupNumbersNormalized -EnumerateMembers $EnumerateMembersText
Add-CompiledRecord -RecordType "OUTPUT" -Message "Final compiled CSV location: $CompiledCsvPath" -InputMode $InputMode -InputFilePath $InputFilePath -SearchInput $SearchInputSummary -SelectedGroupNumbers $SelectedGroupNumbersNormalized -EnumerateMembers $EnumerateMembersText

if (-not $NonInteractive -and -not $SkipSchedulePrompt) {
    New-ADGroupAuditScheduledTaskFromCurrentInputs `
        -CurrentInputMode $InputMode `
        -CurrentInputFilePath $InputFilePath `
        -CurrentManualSearchInput $SearchInputSummary `
        -CurrentSelectedGroupNumbers $SelectedGroupNumbersNormalized `
        -CurrentEnumerateMembers $EnumerateMembersText
}
elseif ($NonInteractive) {
    Add-CompiledRecord -RecordType "INFO" -Message "Scheduled task creation prompt skipped because non-interactive mode is enabled." -InputMode $InputMode -InputFilePath $InputFilePath -SearchInput $SearchInputSummary -SelectedGroupNumbers $SelectedGroupNumbersNormalized -EnumerateMembers $EnumerateMembersText
}
elseif ($SkipSchedulePrompt) {
    Add-CompiledRecord -RecordType "INFO" -Message "Scheduled task creation prompt skipped by -SkipSchedulePrompt." -InputMode $InputMode -InputFilePath $InputFilePath -SearchInput $SearchInputSummary -SelectedGroupNumbers $SelectedGroupNumbersNormalized -EnumerateMembers $EnumerateMembersText
}

# ============================================================
# Export Compiled CSV
# ============================================================

Export-CompiledCsv -Reason "Normal script completion"

# ============================================================
# Final Console Summary
# ============================================================

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Script Complete" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Script Version:           $ScriptVersion"
Write-Host "Input Mode:               $InputMode"
if ($InputMode -eq "File") {
    Write-Host "Input File:               $InputFilePath"
}
Write-Host "Execution Start Time:     $ExecutionStart"
Write-Host "Execution End Time:       $ExecutionEnd"
Write-Host "Execution Duration:       $($Duration.ToString())"
Write-Host "Selected Group Number(s): $SelectedGroupNumbersNormalized"
Write-Host "Enumerated Members:       $EnumerateMembersText"
Write-Host ""
Write-Host "Compiled CSV:"
Write-Host $CompiledCsvPath -ForegroundColor Green
Write-Host "CSV Output Folder:"
Write-Host $CsvOutputFolder -ForegroundColor Green
Write-Host ""
