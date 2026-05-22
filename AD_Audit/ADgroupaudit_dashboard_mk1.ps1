<#
.SYNOPSIS
    Generate a local static HTML dashboard from an AD group audit compiled CSV.

.VERSION
    mk1

.DESCRIPTION
    Prompts the operator to select an ADgroupaudit compiled CSV, validates the
    expected evidence columns, imports the CSV, and generates a standalone local
    HTML dashboard in a report folder under the launch location or a custom
    folder selected by the operator.

    The dashboard is not hosted, does not start a listener, does not use external
    scripts or CSS, and does not transmit data externally. It reads only the
    selected CSV and writes a local HTML file.

.OUTPUT
    <launch location>\report\AD_Group_Audit_Dashboard_mk1_<timestamp>.html
    Or a custom report output folder selected by the operator.

.COMPATIBILITY
    Windows PowerShell 5.1+
#>

# ============================================================
# Initialize Dashboard Script
# ============================================================

$DashboardScriptName = "ADgroupaudit_dashboard_mk1.ps1"
$DashboardVersion = "mk1"
$ExecutionStart = Get-Date
$Timestamp = $ExecutionStart.ToString("yyyyMMdd_HHmmss")
$LaunchFolder = (Get-Location).Path
$DefaultCsvFolder = Join-Path $LaunchFolder "csv"
$DefaultReportOutputFolder = Join-Path $LaunchFolder "report"
$ReportOutputFolder = $DefaultReportOutputFolder
$OutputFolder = $ReportOutputFolder
$DashboardHtmlPath = ""

# ============================================================
# Console Helpers
# ============================================================

function Write-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Host "[LOGIC] $Message" -ForegroundColor Cyan
}

function Write-Result {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Host "[OUTPUT] $Message" -ForegroundColor Green
}

function Write-Warn {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Fail {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Stop-WithError {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Fail $Message
    exit 1
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
# Helper Function: Resolve Report Output Directory
# ============================================================

function Resolve-ReportOutputDirectory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DefaultPath
    )

    $UseDefaultResponse = Read-Host "Use default report output folder '$DefaultPath'? Type Y for yes or N for no"

    if (Test-Yes -Value $UseDefaultResponse) {
        return $DefaultPath
    }

    $CustomPath = Read-Host "Enter full path for report output folder"

    if ([string]::IsNullOrWhiteSpace($CustomPath)) {
        Write-Warn "No custom report output folder entered. Using default: $DefaultPath"
        return $DefaultPath
    }

    return $CustomPath.Trim().Trim('"')
}

# ============================================================
# Helper Function: Select CSV File
# ============================================================

function Select-CompiledCsvPath {
    Write-Step "Attempting to open a graphical CSV file picker."

    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop

        $Dialog = New-Object System.Windows.Forms.OpenFileDialog
        $Dialog.Title = "Select AD Group Audit Compiled CSV"
        $Dialog.Filter = "CSV files (*.csv)|*.csv|All files (*.*)|*.*"
        if (Test-Path -Path $DefaultCsvFolder -PathType Container) {
            $Dialog.InitialDirectory = $DefaultCsvFolder
        }
        else {
            $Dialog.InitialDirectory = $LaunchFolder
        }
        $Dialog.Multiselect = $false

        $DialogResult = $Dialog.ShowDialog()

        if ($DialogResult -eq [System.Windows.Forms.DialogResult]::OK -and -not [string]::IsNullOrWhiteSpace($Dialog.FileName)) {
            Write-Result "Selected CSV with graphical picker: $($Dialog.FileName)"
            return $Dialog.FileName
        }

        Write-Warn "No CSV was selected in the graphical picker."
    }
    catch {
        Write-Warn "Graphical file picker is unavailable. Error: $($_.Exception.Message)"
    }

    Write-Step "Falling back to console prompt for full CSV path."
    $Path = Read-Host "Enter full path to AD group audit compiled CSV"

    if ([string]::IsNullOrWhiteSpace($Path)) {
        Stop-WithError "No CSV path was entered."
    }

    return $Path.Trim().Trim('"')
}

# ============================================================
# Helper Function: Validate CSV
# ============================================================

function Test-ExpectedColumns {
    param(
        [Parameter(Mandatory = $true)]
        [array]$Rows,

        [Parameter(Mandatory = $true)]
        [string[]]$RequiredColumns
    )

    if (-not $Rows -or $Rows.Count -eq 0) {
        Stop-WithError "CSV imported successfully but contains no data rows."
    }

    $AvailableColumns = @($Rows[0].PSObject.Properties.Name)
    $MissingColumns = @()

    foreach ($RequiredColumn in $RequiredColumns) {
        if ($AvailableColumns -notcontains $RequiredColumn) {
            $MissingColumns += $RequiredColumn
        }
    }

    if ($MissingColumns.Count -gt 0) {
        Stop-WithError "CSV is missing expected column(s): $($MissingColumns -join ', ')"
    }
}

# ============================================================
# Helper Function: Convert Data to Base64 JSON
# ============================================================

function ConvertTo-Base64Json {
    param(
        [Parameter(Mandatory = $true)]
        [object]$InputObject
    )

    $Json = ConvertTo-Json -InputObject $InputObject -Depth 8 -Compress
    return [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Json))
}

# ============================================================
# Script Banner
# ============================================================

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " AD Group Audit Local Dashboard Generator" -ForegroundColor Cyan
Write-Host " Script:  $DashboardScriptName" -ForegroundColor Cyan
Write-Host " Version: $DashboardVersion" -ForegroundColor Cyan
Write-Host " Started: $ExecutionStart" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Step "Launch folder: $LaunchFolder"
Write-Step "Resolving report output folder."
$ReportOutputFolder = Resolve-ReportOutputDirectory -DefaultPath $DefaultReportOutputFolder
$OutputFolder = $ReportOutputFolder
$DashboardHtmlPath = Join-Path $ReportOutputFolder "AD_Group_Audit_Dashboard_${DashboardVersion}_$Timestamp.html"
Write-Result "Report output folder selected: $ReportOutputFolder"
Write-Result "Dashboard HTML path will be: $DashboardHtmlPath"

# ============================================================
# Ensure Output Folder Exists
# ============================================================

Write-Step "Checking report output folder: $OutputFolder"

try {
    if (-not (Test-Path -Path $OutputFolder)) {
        New-Item -Path $OutputFolder -ItemType Directory -Force | Out-Null
        Write-Result "Created output folder: $OutputFolder"
    }
    else {
        Write-Result "Output folder exists: $OutputFolder"
    }
}
catch {
    Stop-WithError "Failed to create or access output folder '$OutputFolder'. Error: $($_.Exception.Message)"
}

# ============================================================
# Select and Validate CSV
# ============================================================

$CsvPath = Select-CompiledCsvPath

Write-Step "Validating selected CSV path: $CsvPath"

if (-not (Test-Path -Path $CsvPath -PathType Leaf)) {
    Stop-WithError "CSV file does not exist: $CsvPath"
}

$CsvExtension = [System.IO.Path]::GetExtension($CsvPath)
if ($CsvExtension -ne ".csv") {
    Stop-WithError "Selected file must have a .csv extension. Selected extension: $CsvExtension"
}

Write-Step "Importing selected CSV."

try {
    $CsvRows = @(Import-Csv -Path $CsvPath -ErrorAction Stop)
}
catch {
    Stop-WithError "Failed to import CSV. Error: $($_.Exception.Message)"
}

$RequiredColumns = @("RecordType", "Message", "GroupName", "MemberName")
Test-ExpectedColumns -Rows $CsvRows -RequiredColumns $RequiredColumns
Write-Result "CSV validation passed. Imported $($CsvRows.Count) row(s)."

# ============================================================
# Generate Summary Data
# ============================================================

Write-Step "Generating summary values for console output and dashboard metadata."

$DiscoveredGroups = @($CsvRows | Where-Object { $_.RecordType -eq "DISCOVERED_GROUP" })
$SelectedGroups = @($CsvRows | Where-Object { $_.RecordType -eq "GROUP_RESULT" })
$MemberRows = @($CsvRows | Where-Object { $_.RecordType -eq "MEMBER_RESULT" })
$Warnings = @($CsvRows | Where-Object { $_.RecordType -eq "WARNING" })
$Errors = @($CsvRows | Where-Object { $_.RecordType -eq "ERROR" })

$UniqueMembers = @(
    $MemberRows |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_.MemberDistinguishedName) -or -not [string]::IsNullOrWhiteSpace($_.MemberName) } |
        ForEach-Object {
            if (-not [string]::IsNullOrWhiteSpace($_.MemberDistinguishedName)) {
                $_.MemberDistinguishedName
            }
            else {
                $_.MemberName
            }
        } |
        Select-Object -Unique
)

$FirstRow = $CsvRows | Select-Object -First 1
$FirstInputMode = ($CsvRows | Where-Object { -not [string]::IsNullOrWhiteSpace($_.InputMode) } | Select-Object -First 1).InputMode
$FirstInputFilePath = ($CsvRows | Where-Object { -not [string]::IsNullOrWhiteSpace($_.InputFilePath) } | Select-Object -First 1).InputFilePath

$Summary = [PSCustomObject]@{
    SourceCsvPath            = $CsvPath
    DashboardGeneratedAt     = (Get-Date).ToString("o")
    TotalRows                = $CsvRows.Count
    TotalDiscoveredGroups    = $DiscoveredGroups.Count
    TotalSelectedGroups      = $SelectedGroups.Count
    TotalMemberRows          = $MemberRows.Count
    TotalUniqueMembers       = $UniqueMembers.Count
    TotalWarnings            = $Warnings.Count
    TotalErrors              = $Errors.Count
    InputMode                = $FirstInputMode
    InputFilePath            = $FirstInputFilePath
    ExecutionStartDateTime   = $FirstRow.ExecutionStartDateTime
    ScriptVersion            = $FirstRow.ScriptVersion
}

Write-Result "Total discovered groups: $($Summary.TotalDiscoveredGroups)"
Write-Result "Total selected groups:   $($Summary.TotalSelectedGroups)"
Write-Result "Total member rows:       $($Summary.TotalMemberRows)"
Write-Result "Total unique members:    $($Summary.TotalUniqueMembers)"
Write-Result "Warnings:                $($Summary.TotalWarnings)"
Write-Result "Errors:                  $($Summary.TotalErrors)"

# ============================================================
# Encode Data for HTML
# ============================================================

Write-Step "Safely JSON-encoding CSV rows for standalone HTML embedding."

try {
    $CsvDataBase64 = ConvertTo-Base64Json -InputObject $CsvRows
    $SummaryBase64 = ConvertTo-Base64Json -InputObject $Summary
}
catch {
    Stop-WithError "Failed to JSON-encode CSV data. Error: $($_.Exception.Message)"
}

# ============================================================
# Generate Standalone HTML
# ============================================================

Write-Step "Generating standalone local HTML dashboard."

$HtmlTemplate = @'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AD Group Audit Dashboard mk1</title>
  <style>
    :root {
      --bg: #0b0f14;
      --surface: #111821;
      --panel: #151d28;
      --panel-soft: #1d2835;
      --panel-raised: #192332;
      --field: #0f151d;
      --text: #edf2f7;
      --muted: #9aa7b7;
      --quiet: #758294;
      --line: #2b3747;
      --line-strong: #3a4758;
      --accent: #36d6bd;
      --accent-soft: #12362f;
      --accent-dark: #0f766e;
      --blue: #7dd3fc;
      --danger: #fb7185;
      --danger-bg: #35151d;
      --warning: #fbbf24;
      --warning-bg: #302411;
      --success-bg: #10251f;
      --success-line: #236b58;
      --success-text: #b7f7dc;
      --shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background:
        linear-gradient(180deg, #101722 0, var(--bg) 290px),
        var(--bg);
      color: var(--text);
      font-family: Segoe UI, Arial, sans-serif;
      font-size: 14px;
      line-height: 1.4;
    }

    header {
      background: transparent;
      color: var(--text);
      padding: 24px 28px 10px;
    }

    .header-shell {
      max-width: 1680px;
      margin: 0 auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      background: rgba(21, 29, 40, 0.86);
      box-shadow: var(--shadow);
    }

    .header-row {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 18px;
      align-items: start;
    }

    .eyebrow {
      margin: 0 0 8px;
      color: var(--accent);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    header h1 {
      margin: 0 0 6px;
      font-size: 28px;
      font-weight: 750;
      letter-spacing: 0;
    }

    header .meta {
      color: var(--muted);
      font-size: 13px;
      overflow-wrap: anywhere;
    }

    .status-strip {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
      min-width: 260px;
    }

    .status-pill {
      display: inline-flex;
      align-items: center;
      min-height: 30px;
      padding: 5px 10px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--field);
      color: var(--muted);
      font-size: 12px;
      font-weight: 750;
      white-space: nowrap;
    }

    .status-pill.good {
      border-color: var(--success-line);
      background: var(--success-bg);
      color: var(--success-text);
    }

    .status-pill.warn {
      border-color: rgba(251, 191, 36, 0.5);
      background: var(--warning-bg);
      color: #fde68a;
    }

    .status-pill.bad {
      border-color: rgba(251, 113, 133, 0.5);
      background: var(--danger-bg);
      color: #fecdd3;
    }

    main {
      padding: 14px 28px 44px;
      max-width: 1680px;
      margin: 0 auto;
    }

    section {
      margin-top: 18px;
    }

    h2 {
      margin: 0 0 12px;
      font-size: 16px;
      font-weight: 750;
    }

    h3 {
      margin: 0 0 8px;
      font-size: 15px;
      font-weight: 650;
    }

    .privacy-note {
      background: var(--success-bg);
      border: 1px solid var(--success-line);
      color: var(--success-text);
      padding: 10px 12px;
      border-radius: 6px;
      margin-top: 14px;
      font-weight: 600;
      font-size: 13px;
    }

    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 12px;
    }

    .card {
      position: relative;
      overflow: hidden;
      background: linear-gradient(180deg, var(--panel-raised), var(--panel));
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 15px;
      box-shadow: var(--shadow);
      min-height: 96px;
    }

    .card::before {
      content: "";
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 3px;
      background: var(--line-strong);
    }

    .card.good::before { background: var(--accent); }
    .card.warn::before { background: var(--warning); }
    .card.bad::before { background: var(--danger); }
    .card.info::before { background: var(--blue); }

    .card.bad {
      border-color: rgba(251, 113, 133, 0.38);
    }

    .card.warn {
      border-color: rgba(251, 191, 36, 0.35);
    }

    .card .label {
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      font-weight: 800;
      letter-spacing: 0.06em;
    }

    .card .value {
      margin-top: 6px;
      font-size: 24px;
      font-weight: 780;
      overflow-wrap: anywhere;
    }

    .card.wide {
      grid-column: span 2;
    }

    .filters {
      position: sticky;
      top: 10px;
      z-index: 4;
      background: rgba(21, 29, 40, 0.96);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 14px;
      box-shadow: var(--shadow);
    }

    .filter-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 10px;
      align-items: end;
    }

    label {
      display: block;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 4px;
    }

    input[type="text"], select {
      width: 100%;
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 5px;
      padding: 8px 10px;
      color: var(--text);
      background: var(--field);
      font: inherit;
    }

    input[type="text"]::placeholder {
      color: #737d8c;
    }

    .checks {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 8px;
      margin-top: 12px;
    }

    .check {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 13px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--field);
    }

    button {
      min-height: 38px;
      border: 1px solid var(--accent-dark);
      border-radius: 5px;
      background: var(--accent);
      color: #071411;
      font: inherit;
      font-weight: 650;
      padding: 7px 12px;
      cursor: pointer;
    }

    button:hover {
      filter: brightness(1.08);
    }

    button.secondary {
      background: var(--panel-soft);
      color: var(--text);
      border-color: var(--line);
    }

    button.small {
      min-height: 28px;
      padding: 4px 8px;
      font-size: 12px;
    }

    .tabs {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin: 18px 0 12px;
      padding: 6px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--field);
      width: fit-content;
      max-width: 100%;
    }

    .tab {
      background: transparent;
      color: var(--text);
      border-color: transparent;
      min-height: 34px;
    }

    .tab.active {
      background: var(--panel-soft);
      color: var(--accent);
      border-color: var(--line-strong);
    }

    .panel {
      background: rgba(21, 29, 40, 0.92);
      border: 1px solid var(--line);
      border-radius: 6px;
      box-shadow: var(--shadow);
      padding: 16px;
      margin-bottom: 16px;
    }

    .table-wrap {
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 6px;
      max-height: 520px;
      background: var(--field);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 900px;
    }

    th, td {
      border-bottom: 1px solid var(--line);
      padding: 8px 10px;
      text-align: left;
      vertical-align: top;
      white-space: nowrap;
    }

    th {
      position: sticky;
      top: 0;
      z-index: 2;
      background: var(--panel-soft);
      font-size: 12px;
      color: var(--text);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    td {
      font-size: 13px;
      max-width: 360px;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    tr:hover td {
      background: #202733;
    }

    .issue-error { color: var(--danger); font-weight: 700; }
    .issue-warning { color: var(--warning); font-weight: 700; }

    .split {
      display: grid;
      grid-template-columns: minmax(280px, 360px) 1fr;
      gap: 14px;
    }

    .group-list {
      display: grid;
      gap: 8px;
      max-height: 520px;
      overflow: auto;
      padding-right: 2px;
    }

    .group-item {
      width: 100%;
      background: var(--panel-raised);
      color: var(--text);
      border: 1px solid var(--line);
      text-align: left;
      padding: 12px;
      min-height: auto;
    }

    .group-item.active {
      border-color: var(--accent);
      background: var(--accent-soft);
    }

    .group-item .name {
      font-weight: 700;
      overflow-wrap: anywhere;
    }

    .group-item .sub {
      color: var(--muted);
      font-size: 12px;
      margin-top: 3px;
    }

    .analysis-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px;
    }

    .metric-list {
      margin: 0;
      padding: 0;
      list-style: none;
      border: 1px solid var(--line);
      border-radius: 6px;
      overflow: hidden;
    }

    .metric-list li {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      background: var(--panel-raised);
    }

    .metric-list li:last-child { border-bottom: 0; }
    .metric-list span:first-child { overflow-wrap: anywhere; }
    .metric-list strong { white-space: nowrap; }

    .section-actions {
      display: flex;
      gap: 8px;
      justify-content: flex-end;
      margin-bottom: 8px;
      flex-wrap: wrap;
    }

    .hidden { display: none; }

    @media (max-width: 900px) {
      header { padding: 18px; }
      main { padding: 14px; }
      .header-row { grid-template-columns: 1fr; }
      .status-strip { justify-content: flex-start; min-width: 0; }
      .split { grid-template-columns: 1fr; }
      .card.wide { grid-column: span 1; }
      .filters { position: static; }
      .tabs { width: 100%; }
      table { min-width: 760px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="header-shell">
      <div class="header-row">
        <div>
          <div class="eyebrow">Local Evidence Review</div>
          <h1>AD Group Audit Dashboard mk1</h1>
          <div class="meta" id="headerMeta"></div>
        </div>
        <div class="status-strip" id="statusStrip"></div>
      </div>
      <div class="privacy-note">This dashboard is a local static HTML file generated from the selected CSV. No data is transmitted externally.</div>
    </div>
  </header>

  <main>
    <section>
      <h2>Summary</h2>
      <div class="cards" id="summaryCards"></div>
    </section>

    <section class="filters">
      <h2>Filters</h2>
      <div class="filter-grid">
        <div>
          <label for="recordTypeFilter">RecordType</label>
          <select id="recordTypeFilter"></select>
        </div>
        <div>
          <label for="groupNameFilter">GroupName</label>
          <input id="groupNameFilter" type="text" placeholder="Filter group name">
        </div>
        <div>
          <label for="memberNameFilter">MemberName</label>
          <input id="memberNameFilter" type="text" placeholder="Filter member name">
        </div>
        <div>
          <label for="memberClassFilter">MemberObjectClass</label>
          <select id="memberClassFilter"></select>
        </div>
        <div>
          <label for="searchInputFilter">SearchInput</label>
          <input id="searchInputFilter" type="text" placeholder="Filter search input">
        </div>
        <div>
          <button id="clearFilters" type="button" class="secondary">Clear Filters</button>
        </div>
      </div>
      <div class="checks">
        <label class="check"><input id="issuesOnly" type="checkbox"> Show only errors/warnings</label>
        <label class="check"><input id="selectedOnly" type="checkbox"> Show only selected groups</label>
        <label class="check"><input id="membersOnly" type="checkbox"> Show only member results</label>
      </div>
    </section>

    <div class="tabs" id="tabs"></div>

    <section class="panel tab-panel" data-panel="groups">
      <h2>Group-Focused View</h2>
      <div class="split">
        <div>
          <h3>Selected Groups</h3>
          <div class="group-list" id="selectedGroupList"></div>
        </div>
        <div>
          <div class="section-actions">
            <button type="button" class="small secondary" data-export="groupMembers">Export Members</button>
          </div>
          <h3 id="groupMembersTitle">Members for Selected Group</h3>
          <div class="table-wrap" id="groupMembersTable"></div>
        </div>
      </div>
    </section>

    <section class="panel tab-panel hidden" data-panel="analysis">
      <h2>Member Analysis</h2>
      <div class="analysis-grid">
        <div>
          <h3>Members by Object Class</h3>
          <ul class="metric-list" id="classCounts"></ul>
        </div>
        <div>
          <h3>Enabled vs Disabled Users</h3>
          <ul class="metric-list" id="enabledCounts"></ul>
        </div>
        <div>
          <h3>Members by Department</h3>
          <ul class="metric-list" id="departmentCounts"></ul>
        </div>
        <div>
          <h3>Missing Key Member Fields</h3>
          <ul class="metric-list" id="missingCounts"></ul>
        </div>
      </div>
    </section>

    <section class="panel tab-panel hidden" data-panel="tables">
      <h2>Evidence Tables</h2>
      <div id="tablesRoot"></div>
    </section>

    <section class="panel tab-panel hidden" data-panel="trace">
      <h2>Evidence Trace</h2>
      <div class="section-actions">
        <button type="button" class="small secondary" data-export="trace">Export Trace</button>
      </div>
      <div class="table-wrap" id="traceTable"></div>
    </section>

    <section class="panel tab-panel hidden" data-panel="raw">
      <h2>Full Raw CSV</h2>
      <div class="section-actions">
        <button type="button" class="small secondary" data-export="raw">Export Filtered Raw</button>
      </div>
      <div class="table-wrap" id="rawTable"></div>
    </section>
  </main>

  <script>
    (function () {
      "use strict";

      var dataBase64 = "__CSV_DATA_BASE64__";
      var summaryBase64 = "__SUMMARY_BASE64__";
      var rows = parseBase64Json(dataBase64);
      var summary = parseBase64Json(summaryBase64);
      var activeGroupName = "";
      var latestFilteredRows = rows.slice();
      var latestTables = {};

      var columns = [
        "ScriptVersion", "ExecutionStartDateTime", "RecordDateTime", "RecordType", "Message",
        "InputMode", "InputFilePath", "SearchInput", "SelectedGroupNumbers", "EnumerateMembers",
        "GroupMenuNumber", "GroupName", "GroupSamAccountName", "GroupCategory", "GroupScope",
        "GroupDescription", "GroupWhenCreated", "GroupWhenChanged", "GroupManagedBy",
        "GroupDistinguishedName", "MemberName", "MemberSamAccountName", "MemberObjectClass",
        "MemberUserPrincipalName", "MemberEnabled", "MemberMail", "MemberTitle",
        "MemberDepartment", "MemberWhenCreated", "MemberWhenChanged", "MemberDistinguishedName"
      ];

      var tableDefinitions = [
        { id: "discovered", title: "Discovered Groups", filter: function (r) { return r.RecordType === "DISCOVERED_GROUP"; }, columns: ["GroupMenuNumber", "SearchInput", "GroupName", "GroupSamAccountName", "GroupCategory", "GroupScope", "GroupWhenCreated", "GroupWhenChanged", "GroupManagedBy", "GroupDistinguishedName"] },
        { id: "selected", title: "Selected Groups", filter: function (r) { return r.RecordType === "GROUP_RESULT"; }, columns: ["GroupMenuNumber", "SearchInput", "GroupName", "GroupSamAccountName", "GroupCategory", "GroupScope", "GroupDescription", "GroupWhenCreated", "GroupWhenChanged", "GroupManagedBy", "GroupDistinguishedName"] },
        { id: "members", title: "Member Results", filter: function (r) { return r.RecordType === "MEMBER_RESULT"; }, columns: ["GroupMenuNumber", "GroupName", "MemberName", "MemberSamAccountName", "MemberObjectClass", "MemberUserPrincipalName", "MemberEnabled", "MemberMail", "MemberTitle", "MemberDepartment", "MemberWhenCreated", "MemberWhenChanged", "MemberDistinguishedName"] },
        { id: "issues", title: "Errors and Warnings", filter: function (r) { return r.RecordType === "ERROR" || r.RecordType === "WARNING"; }, columns: ["RecordDateTime", "RecordType", "Message", "SearchInput", "GroupName", "MemberName"] }
      ];

      function parseBase64Json(value) {
        var binary = atob(value);
        if (window.TextDecoder) {
          var bytes = new Uint8Array(binary.length);
          for (var i = 0; i < binary.length; i += 1) {
            bytes[i] = binary.charCodeAt(i);
          }
          return JSON.parse(new TextDecoder("utf-8").decode(bytes));
        }
        return JSON.parse(decodeURIComponent(escape(binary)));
      }

      function text(value) {
        if (value === null || value === undefined) {
          return "";
        }
        return String(value);
      }

      function lower(value) {
        return text(value).toLowerCase();
      }

      function uniqueValues(field) {
        var seen = {};
        rows.forEach(function (row) {
          var value = text(row[field]);
          if (value !== "") {
            seen[value] = true;
          }
        });
        return Object.keys(seen).sort();
      }

      function populateSelect(id, values, allLabel) {
        var select = document.getElementById(id);
        select.innerHTML = "";
        var all = document.createElement("option");
        all.value = "";
        all.textContent = allLabel;
        select.appendChild(all);
        values.forEach(function (value) {
          var option = document.createElement("option");
          option.value = value;
          option.textContent = value;
          select.appendChild(option);
        });
      }

      function getFilters() {
        return {
          recordType: document.getElementById("recordTypeFilter").value,
          groupName: lower(document.getElementById("groupNameFilter").value),
          memberName: lower(document.getElementById("memberNameFilter").value),
          memberClass: document.getElementById("memberClassFilter").value,
          searchInput: lower(document.getElementById("searchInputFilter").value),
          issuesOnly: document.getElementById("issuesOnly").checked,
          selectedOnly: document.getElementById("selectedOnly").checked,
          membersOnly: document.getElementById("membersOnly").checked
        };
      }

      function applyFilters(sourceRows) {
        var f = getFilters();
        return sourceRows.filter(function (row) {
          if (f.recordType && row.RecordType !== f.recordType) { return false; }
          if (f.groupName && lower(row.GroupName).indexOf(f.groupName) === -1) { return false; }
          if (f.memberName && lower(row.MemberName).indexOf(f.memberName) === -1) { return false; }
          if (f.memberClass && row.MemberObjectClass !== f.memberClass) { return false; }
          if (f.searchInput && lower(row.SearchInput).indexOf(f.searchInput) === -1) { return false; }
          if (f.issuesOnly && row.RecordType !== "ERROR" && row.RecordType !== "WARNING") { return false; }
          if (f.selectedOnly && row.RecordType !== "GROUP_RESULT") { return false; }
          if (f.membersOnly && row.RecordType !== "MEMBER_RESULT") { return false; }
          return true;
        });
      }

      function renderSummary() {
        document.getElementById("headerMeta").textContent =
          "Source CSV: " + text(summary.SourceCsvPath) + " | Generated: " + text(summary.DashboardGeneratedAt);

        var statusRoot = document.getElementById("statusStrip");
        statusRoot.innerHTML = "";
        [
          ["Local Static", "good"],
          ["Errors " + text(summary.TotalErrors || 0), Number(summary.TotalErrors || 0) > 0 ? "bad" : "good"],
          ["Warnings " + text(summary.TotalWarnings || 0), Number(summary.TotalWarnings || 0) > 0 ? "warn" : "good"],
          [text(summary.ScriptVersion || "No Version"), ""]
        ].forEach(function (item) {
          var pill = document.createElement("div");
          pill.className = item[1] ? "status-pill " + item[1] : "status-pill";
          pill.textContent = item[0];
          statusRoot.appendChild(pill);
        });

        var cardData = [
          ["Total discovered groups", summary.TotalDiscoveredGroups, "info"],
          ["Total selected groups", summary.TotalSelectedGroups, "good"],
          ["Total member rows", summary.TotalMemberRows, "info"],
          ["Total unique members", summary.TotalUniqueMembers, "info"],
          ["Total warnings", summary.TotalWarnings, Number(summary.TotalWarnings || 0) > 0 ? "warn" : "good"],
          ["Total errors", summary.TotalErrors, Number(summary.TotalErrors || 0) > 0 ? "bad" : "good"],
          ["Input mode", summary.InputMode || "Not populated", "info"],
          ["Execution start time", summary.ExecutionStartDateTime || "Not populated", "info"],
          ["Script version from CSV", summary.ScriptVersion || "Not populated", "info"],
          ["Input file path", summary.InputFilePath || "Not applicable", "info"]
        ];

        var root = document.getElementById("summaryCards");
        root.innerHTML = "";
        cardData.forEach(function (item) {
          var card = document.createElement("div");
          card.className = item[0] === "Input file path" ? "card wide " + item[2] : "card " + item[2];
          var label = document.createElement("div");
          label.className = "label";
          label.textContent = item[0];
          var value = document.createElement("div");
          value.className = "value";
          value.textContent = text(item[1]);
          card.appendChild(label);
          card.appendChild(value);
          root.appendChild(card);
        });
      }

      function renderTable(containerId, tableRows, tableColumns) {
        var container = document.getElementById(containerId);
        container.innerHTML = buildTable(tableRows, tableColumns);
      }

      function buildTable(tableRows, tableColumns) {
        var html = "<table><thead><tr>";
        tableColumns.forEach(function (column) {
          html += "<th>" + escapeHtml(column) + "</th>";
        });
        html += "</tr></thead><tbody>";

        if (tableRows.length === 0) {
          html += "<tr><td colspan=\"" + tableColumns.length + "\">No rows match the current filters.</td></tr>";
        }
        else {
          tableRows.forEach(function (row) {
            html += "<tr>";
            tableColumns.forEach(function (column) {
              var css = "";
              if (column === "RecordType" && row.RecordType === "ERROR") { css = " class=\"issue-error\""; }
              if (column === "RecordType" && row.RecordType === "WARNING") { css = " class=\"issue-warning\""; }
              html += "<td" + css + " title=\"" + escapeHtml(text(row[column])) + "\">" + escapeHtml(text(row[column])) + "</td>";
            });
            html += "</tr>";
          });
        }

        html += "</tbody></table>";
        return html;
      }

      function escapeHtml(value) {
        return text(value)
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;")
          .replace(/'/g, "&#39;");
      }

      function renderTabs() {
        var tabs = [
          ["groups", "Group View"],
          ["analysis", "Member Analysis"],
          ["tables", "Tables"],
          ["trace", "Evidence Trace"],
          ["raw", "Raw CSV"]
        ];
        var root = document.getElementById("tabs");
        root.innerHTML = "";
        tabs.forEach(function (tab, index) {
          var button = document.createElement("button");
          button.type = "button";
          button.className = index === 0 ? "tab active" : "tab";
          button.textContent = tab[1];
          button.setAttribute("data-tab", tab[0]);
          root.appendChild(button);
        });
      }

      function switchTab(name) {
        var tabButtons = document.querySelectorAll("[data-tab]");
        for (var i = 0; i < tabButtons.length; i += 1) {
          tabButtons[i].className = tabButtons[i].getAttribute("data-tab") === name ? "tab active" : "tab";
        }

        var panels = document.querySelectorAll(".tab-panel");
        for (var j = 0; j < panels.length; j += 1) {
          if (panels[j].getAttribute("data-panel") === name) {
            panels[j].classList.remove("hidden");
          }
          else {
            panels[j].classList.add("hidden");
          }
        }
      }

      function renderAll() {
        latestFilteredRows = applyFilters(rows);
        renderGroupView();
        renderAnalysis();
        renderEvidenceTables();
        renderTrace();
        renderRaw();
      }

      function renderGroupView() {
        var selectedGroups = rows.filter(function (r) { return r.RecordType === "GROUP_RESULT"; });
        var list = document.getElementById("selectedGroupList");
        list.innerHTML = "";

        if (selectedGroups.length === 0) {
          list.textContent = "No selected group rows are present in the CSV.";
          renderTable("groupMembersTable", [], tableDefinitions[2].columns);
          return;
        }

        if (!activeGroupName) {
          activeGroupName = selectedGroups[0].GroupName || "";
        }

        selectedGroups.forEach(function (group) {
          var members = rows.filter(function (r) {
            return r.RecordType === "MEMBER_RESULT" && r.GroupName === group.GroupName;
          });
          var button = document.createElement("button");
          button.type = "button";
          button.className = group.GroupName === activeGroupName ? "group-item active" : "group-item";
          button.setAttribute("data-group-name", group.GroupName || "");
          button.innerHTML =
            "<div class=\"name\">" + escapeHtml(group.GroupName || "(blank group name)") + "</div>" +
            "<div class=\"sub\">Menu #" + escapeHtml(group.GroupMenuNumber || "") + " | Members: " + members.length + "</div>";
          list.appendChild(button);
        });

        var groupMembers = applyFilters(rows).filter(function (r) {
          return r.RecordType === "MEMBER_RESULT" && r.GroupName === activeGroupName;
        });
        latestTables.groupMembers = groupMembers;
        document.getElementById("groupMembersTitle").textContent = "Members for " + (activeGroupName || "Selected Group");
        renderTable("groupMembersTable", groupMembers, tableDefinitions[2].columns);
      }

      function countBy(tableRows, field, blankLabel) {
        var counts = {};
        tableRows.forEach(function (row) {
          var value = text(row[field]).trim();
          if (value === "") {
            value = blankLabel;
          }
          counts[value] = (counts[value] || 0) + 1;
        });
        return counts;
      }

      function renderMetricList(id, counts) {
        var root = document.getElementById(id);
        var keys = Object.keys(counts).sort(function (a, b) {
          return counts[b] - counts[a] || a.localeCompare(b);
        });
        root.innerHTML = "";

        if (keys.length === 0) {
          var empty = document.createElement("li");
          empty.innerHTML = "<span>No data</span><strong>0</strong>";
          root.appendChild(empty);
          return;
        }

        keys.forEach(function (key) {
          var item = document.createElement("li");
          item.innerHTML = "<span>" + escapeHtml(key) + "</span><strong>" + counts[key] + "</strong>";
          root.appendChild(item);
        });
      }

      function renderAnalysis() {
        var members = applyFilters(rows).filter(function (r) { return r.RecordType === "MEMBER_RESULT"; });
        renderMetricList("classCounts", countBy(members, "MemberObjectClass", "(blank)"));
        renderMetricList("departmentCounts", countBy(members.filter(function (r) { return text(r.MemberDepartment).trim() !== ""; }), "MemberDepartment", "(blank)"));

        var enabled = {};
        members.forEach(function (row) {
          var value = text(row.MemberEnabled).trim();
          if (value !== "") {
            enabled[value] = (enabled[value] || 0) + 1;
          }
        });
        renderMetricList("enabledCounts", enabled);

        var missing = {
          "Blank MemberName": 0,
          "Blank MemberSamAccountName": 0,
          "Blank MemberObjectClass": 0,
          "Blank MemberDistinguishedName": 0,
          "Blank MemberUserPrincipalName for user rows": 0,
          "Blank MemberEnabled for user rows": 0,
          "Blank MemberMail for user rows": 0,
          "Blank MemberDepartment for user rows": 0
        };

        members.forEach(function (row) {
          if (!text(row.MemberName).trim()) { missing["Blank MemberName"] += 1; }
          if (!text(row.MemberSamAccountName).trim()) { missing["Blank MemberSamAccountName"] += 1; }
          if (!text(row.MemberObjectClass).trim()) { missing["Blank MemberObjectClass"] += 1; }
          if (!text(row.MemberDistinguishedName).trim()) { missing["Blank MemberDistinguishedName"] += 1; }
          if (lower(row.MemberObjectClass) === "user") {
            if (!text(row.MemberUserPrincipalName).trim()) { missing["Blank MemberUserPrincipalName for user rows"] += 1; }
            if (!text(row.MemberEnabled).trim()) { missing["Blank MemberEnabled for user rows"] += 1; }
            if (!text(row.MemberMail).trim()) { missing["Blank MemberMail for user rows"] += 1; }
            if (!text(row.MemberDepartment).trim()) { missing["Blank MemberDepartment for user rows"] += 1; }
          }
        });
        renderMetricList("missingCounts", missing);
      }

      function renderEvidenceTables() {
        var root = document.getElementById("tablesRoot");
        root.innerHTML = "";
        tableDefinitions.forEach(function (def) {
          var section = document.createElement("section");
          section.innerHTML =
            "<div class=\"section-actions\"><button type=\"button\" class=\"small secondary\" data-export=\"" + def.id + "\">Export " + escapeHtml(def.title) + "</button></div>" +
            "<h3>" + escapeHtml(def.title) + "</h3>" +
            "<div class=\"table-wrap\" id=\"table-" + def.id + "\"></div>";
          root.appendChild(section);

          var tableRows = latestFilteredRows.filter(def.filter);
          latestTables[def.id] = tableRows;
          document.getElementById("table-" + def.id).innerHTML = buildTable(tableRows, def.columns);
        });
      }

      function renderTrace() {
        var allowed = { INFO: true, LOGIC: true, OUTPUT: true, WARNING: true, ERROR: true };
        var traceRows = latestFilteredRows.filter(function (row) {
          return allowed[row.RecordType] === true;
        }).sort(function (a, b) {
          return text(a.RecordDateTime).localeCompare(text(b.RecordDateTime));
        });
        latestTables.trace = traceRows;
        renderTable("traceTable", traceRows, ["RecordDateTime", "RecordType", "Message", "InputMode", "InputFilePath", "SearchInput", "SelectedGroupNumbers", "EnumerateMembers", "GroupName", "MemberName"]);
      }

      function renderRaw() {
        latestTables.raw = latestFilteredRows;
        renderTable("rawTable", latestFilteredRows, columns);
      }

      function exportRows(name, exportRowsValue, exportColumns) {
        var csv = [];
        csv.push(exportColumns.map(csvEscape).join(","));
        exportRowsValue.forEach(function (row) {
          csv.push(exportColumns.map(function (column) {
            return csvEscape(row[column]);
          }).join(","));
        });
        var blob = new Blob([csv.join("\r\n")], { type: "text/csv;charset=utf-8" });
        var url = URL.createObjectURL(blob);
        var link = document.createElement("a");
        link.href = url;
        link.download = name + "_" + new Date().toISOString().replace(/[:.]/g, "-") + ".csv";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }

      function csvEscape(value) {
        var output = text(value);
        if (/[",\r\n]/.test(output)) {
          output = "\"" + output.replace(/"/g, "\"\"") + "\"";
        }
        return output;
      }

      function bindEvents() {
        ["recordTypeFilter", "groupNameFilter", "memberNameFilter", "memberClassFilter", "searchInputFilter", "issuesOnly", "selectedOnly", "membersOnly"].forEach(function (id) {
          document.getElementById(id).addEventListener("input", renderAll);
          document.getElementById(id).addEventListener("change", renderAll);
        });

        document.getElementById("clearFilters").addEventListener("click", function () {
          document.getElementById("recordTypeFilter").value = "";
          document.getElementById("groupNameFilter").value = "";
          document.getElementById("memberNameFilter").value = "";
          document.getElementById("memberClassFilter").value = "";
          document.getElementById("searchInputFilter").value = "";
          document.getElementById("issuesOnly").checked = false;
          document.getElementById("selectedOnly").checked = false;
          document.getElementById("membersOnly").checked = false;
          renderAll();
        });

        document.addEventListener("click", function (event) {
          var tab = event.target.getAttribute("data-tab");
          if (tab) {
            switchTab(tab);
            return;
          }

          var groupButton = event.target.closest ? event.target.closest("[data-group-name]") : null;
          if (groupButton) {
            activeGroupName = groupButton.getAttribute("data-group-name");
            renderAll();
            return;
          }

          var exportName = event.target.getAttribute("data-export");
          if (exportName) {
            var exportMap = {
              groupMembers: tableDefinitions[2].columns,
              discovered: tableDefinitions[0].columns,
              selected: tableDefinitions[1].columns,
              members: tableDefinitions[2].columns,
              issues: tableDefinitions[3].columns,
              trace: ["RecordDateTime", "RecordType", "Message", "InputMode", "InputFilePath", "SearchInput", "SelectedGroupNumbers", "EnumerateMembers", "GroupName", "MemberName"],
              raw: columns
            };
            exportRows("AD_Group_Audit_" + exportName, latestTables[exportName] || [], exportMap[exportName] || columns);
          }
        });
      }

      renderSummary();
      populateSelect("recordTypeFilter", uniqueValues("RecordType"), "All record types");
      populateSelect("memberClassFilter", uniqueValues("MemberObjectClass"), "All member classes");
      renderTabs();
      bindEvents();
      renderAll();
    }());
  </script>
</body>
</html>
'@

$HtmlContent = $HtmlTemplate.Replace("__CSV_DATA_BASE64__", $CsvDataBase64).Replace("__SUMMARY_BASE64__", $SummaryBase64)

try {
    Set-Content -Path $DashboardHtmlPath -Value $HtmlContent -Encoding UTF8 -ErrorAction Stop
    Write-Result "Dashboard HTML generated: $DashboardHtmlPath"
}
catch {
    Stop-WithError "Failed to write dashboard HTML. Error: $($_.Exception.Message)"
}

# ============================================================
# Open Dashboard Locally
# ============================================================

Write-Step "Opening dashboard HTML locally with Invoke-Item. No web server will be started."

try {
    Invoke-Item -Path $DashboardHtmlPath
    Write-Result "Dashboard opened locally in the default browser."
}
catch {
    Write-Warn "Dashboard was generated but could not be opened automatically. Error: $($_.Exception.Message)"
    Write-Host "Open this file manually:"
    Write-Host $DashboardHtmlPath -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Dashboard Generation Complete" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Source CSV:      $CsvPath"
Write-Host "Dashboard HTML:  $DashboardHtmlPath"
Write-Host "Generated At:    $(Get-Date)"
Write-Host ""
