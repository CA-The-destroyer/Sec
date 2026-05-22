# AD Group Audit Dashboard README

## Scripts

**Audit collection script:** `ADgroupaudit_mk4.ps1`  
**Dashboard script:** `ADgroupaudit_dashboard_mk1.ps1`  
**Dashboard version:** `mk1`

The dashboard is intentionally separate from the audit collection script. The audit script creates the evidence CSV. The dashboard script reviews an existing compiled CSV and generates a local static HTML dashboard.

`ADgroupaudit_mk4.ps1` is not replaced or modified by this dashboard package.

---

## Audit Script Flow

The existing audit script:

1. Prompts whether to use an input file for group search terms.
2. In input-file mode, prompts for the input file path and can save that path to `C:\temp\ADgroupaudit_default_input_path.txt`.
3. In manual mode, prompts for one AD group name or partial group name.
4. Searches Active Directory groups by `Name` using wildcard matching.
5. Deduplicates discovered groups by `DistinguishedName`.
6. Displays discovered groups in a numbered menu.
7. Allows selection by menu number, comma-separated menu numbers, or `ALL`.
8. Prompts whether to enumerate users/members of selected groups.
9. Uses `Get-ADGroupMember -Recursive` when member enumeration is selected.
10. Attempts to enrich members using `Get-ADUser`, `Get-ADGroup`, or `Get-ADObject`.
11. Writes one compiled CSV to the audit script's selected CSV output folder.

The current mk4 compiled CSV naming pattern is:

```text
<audit output folder>\AD_Group_Search_Compiled_mk4_<timestamp>.csv
```

---

## Dashboard Flow

`ADgroupaudit_dashboard_mk1.ps1`:

1. Displays a console banner with script name, version, and start time.
2. Prompts the operator to select the compiled CSV.
3. Uses a graphical file picker when available.
4. Falls back to a full-path console prompt when graphical file picker support is unavailable.
5. Validates that the selected file exists.
6. Validates that the selected file has a `.csv` extension.
7. Validates required CSV columns:
   - `RecordType`
   - `Message`
   - `GroupName`
   - `MemberName`
8. Imports the CSV using built-in PowerShell.
9. Generates summary values.
10. JSON-encodes the CSV data and embeds it into a standalone HTML file.
11. Saves the dashboard to the selected report output folder.
12. Opens the HTML file locally with `Invoke-Item`.

Dashboard output naming pattern:

```text
<launch location>\report\AD_Group_Audit_Dashboard_mk1_<timestamp>.html
```

The operator can choose a different report output folder at runtime.

---

## Report Output Folder

At startup, the dashboard asks whether to use the default report output folder:

```text
Use default report output folder '<launch location>\report'? Type Y for yes or N for no
```

If the operator answers `Y`, the dashboard creates and uses:

```text
<launch location>\report
```

If the operator answers `N`, the dashboard prompts for a custom full folder path.

The generated HTML report is written to the selected folder:

```text
AD_Group_Audit_Dashboard_mk1_<timestamp>.html
```

---

## How to Run

Run the audit script first if you need a new evidence CSV:

```powershell
PowerShell.exe -ExecutionPolicy Bypass -File C:\temp\ADgroupaudit_mk4.ps1
```

Then run the dashboard script manually:

```powershell
PowerShell.exe -ExecutionPolicy Bypass -File C:\temp\ADgroupaudit_dashboard_mk1.ps1
```

Select a compiled CSV such as:

```text
C:\temp\AD_Group_Search_Compiled_mk4_20260521_154455.csv
```

The dashboard is not launched automatically by mk4. It is manually launched only.

---

## CSV Requirements

The dashboard is built for the compiled CSV produced by the AD group audit script.

Minimum required columns:

| Column | Purpose |
|---|---|
| `RecordType` | Identifies evidence row type such as `INFO`, `GROUP_RESULT`, or `MEMBER_RESULT`. |
| `Message` | Human-readable logic, output, warning, error, or result text. |
| `GroupName` | Group name used for group tables and filtering. |
| `MemberName` | Member name used for member tables and filtering. |

Expected audit columns include:

```text
ScriptVersion
ExecutionStartDateTime
RecordDateTime
RecordType
Message
InputMode
InputFilePath
SearchInput
SelectedGroupNumbers
EnumerateMembers
GroupMenuNumber
GroupName
GroupSamAccountName
GroupCategory
GroupScope
GroupDescription
GroupWhenCreated
GroupWhenChanged
GroupManagedBy
GroupDistinguishedName
MemberName
MemberSamAccountName
MemberObjectClass
MemberUserPrincipalName
MemberEnabled
MemberMail
MemberTitle
MemberDepartment
MemberWhenCreated
MemberWhenChanged
MemberDistinguishedName
```

The dashboard can still open a CSV that has the minimum required columns, but tables and analysis are most useful when the full compiled audit schema is present.

---

## Dashboard Features

Summary cards:

- Total discovered groups
- Total selected groups
- Total member rows
- Total unique members
- Total warnings
- Total errors
- Input mode
- Input file path, when applicable
- Execution start time
- Script version from CSV

Filters:

- `RecordType`
- `GroupName`
- `MemberName`
- `MemberObjectClass`
- `SearchInput`
- Show only errors/warnings
- Show only selected groups
- Show only member results

Tables:

- Discovered groups
- Selected groups
- Member results
- Errors and warnings
- Full raw CSV

Review views:

- Group-focused selected group view with member counts
- Clickable selected groups to show members for one group
- Chronological evidence trace using `RecordDateTime`
- Member analysis by object class, enabled status, and department
- Missing key member field counts

Export:

- Dashboard table views include browser-side CSV export buttons where practical.
- Export is performed by local JavaScript in the generated HTML file.
- No external services are called.

---

## Privacy Model

The dashboard is a local static HTML file generated from the selected CSV.

It does not:

- Start a web server
- Start a listener
- Use IIS, Apache, nginx, or any hosted service
- Use external JavaScript
- Use external CSS
- Use CDNs
- Use analytics
- Use telemetry
- Call APIs
- Transmit CSV contents externally
- Modify Active Directory

The dashboard reads only the selected CSV and writes one local HTML file to the selected report output folder.

The generated dashboard visibly states:

```text
This dashboard is a local static HTML file generated from the selected CSV. No data is transmitted externally.
```

---

## Troubleshooting

### File picker does not appear

Some locked-down or non-interactive PowerShell sessions cannot show Windows Forms dialogs.

Expected behavior:

- The script logs a warning.
- The script prompts for a full CSV path in the console.

Enter a path like:

```text
C:\temp\AD_Group_Search_Compiled_mk4_20260521_154455.csv
```

### Selected file is not found

Confirm the path exists:

```powershell
Test-Path "C:\temp\AD_Group_Search_Compiled_mk4_20260521_154455.csv"
```

### Selected file is not a CSV

The dashboard requires a `.csv` file extension.

### CSV is missing expected columns

The script requires these columns:

```text
RecordType
Message
GroupName
MemberName
```

Use a compiled CSV from the AD group audit script rather than a manually edited or unrelated CSV.

### Browser blocks active content

The dashboard uses embedded local JavaScript for filtering, rendering, and CSV export. If browser policy blocks local scripts, open the generated HTML in an approved browser or approved local security context.

### Dashboard opens but some sections are empty

This usually means the selected CSV does not contain those `RecordType` rows.

Examples:

- No `MEMBER_RESULT` rows: member enumeration may not have been selected.
- No `WARNING` or `ERROR` rows: the errors and warnings table will be empty.
- No `GROUP_RESULT` rows: the audit may have stopped before group selection.

---

## Safety Statement

`ADgroupaudit_dashboard_mk1.ps1` is read-only against audit evidence and does not interact with Active Directory.

The only write action is creation of the local dashboard HTML file:

```text
<selected report output folder>\AD_Group_Audit_Dashboard_mk1_<timestamp>.html
```
