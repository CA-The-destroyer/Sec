# AD Group Audit mk5 README

## Files

**Audit script:** `ADgroupaudit_mk5.ps1`  
**Audit version:** `mk5`  
**Dashboard script:** `ADgroupaudit_dashboard_mk1.ps1`

`ADgroupaudit_mk5.ps1` preserves the mk4 audit flow and adds optional Windows Scheduled Task creation. `ADgroupaudit_mk4.ps1` is not replaced or modified.

---

## What Changed in mk5

mk5 keeps the existing interactive audit behavior and adds:

- Non-interactive replay parameters for scheduled runs.
- A manual-mode prompt to create a future input file from the selected groups.
- A post-run prompt:

```text
Do you want to create a scheduled task with these inputs? Type Y for yes or N for no
```

- Optional daily Windows Scheduled Task creation using the same input mode, search input, selected group numbers, and member enumeration choice from the current run.
- Scheduled task runs include `-SkipSchedulePrompt` so the task does not recursively prompt to create another task.

The dashboard remains manually launched only. mk5 does not automatically launch the dashboard.

---

## Interactive Audit Flow

Run:

```powershell
PowerShell.exe -ExecutionPolicy Bypass -File C:\temp\ADgroupaudit_mk5.ps1
```

The script:

1. Prompts whether to use an input file.
2. In file mode, prompts for the input path or offers the saved default.
3. In manual mode, prompts for a group name or partial group name.
4. Searches AD groups by `Name` using wildcard matching.
5. Deduplicates groups by `DistinguishedName`.
6. Displays discovered groups as a numbered menu.
7. Prompts for selected group numbers, such as `1`, `1,2,4`, or `ALL`.
8. If manual mode was used, prompts whether to create an input file from the selected groups.
9. Prompts whether to enumerate users/members.
10. Writes a compiled CSV to the selected CSV output folder.
11. Prompts whether to create a scheduled task with the current inputs.

Compiled CSV naming pattern:

```text
<launch location>\csv\AD_Group_Search_Compiled_mk5_<timestamp>.csv
```

The operator can choose a different CSV output folder at runtime.

---

## CSV Output Folder

At startup, mk5 asks whether to use the default compiled CSV output folder:

```text
Use default compiled CSV output folder '<launch location>\csv'? Type Y for yes or N for no
```

If the operator answers `Y`, mk5 creates and uses:

```text
<launch location>\csv
```

If the operator answers `N`, mk5 prompts for a custom full folder path.

The compiled CSV is written to the selected folder:

```text
AD_Group_Search_Compiled_mk5_<timestamp>.csv
```

Scheduled tasks created by mk5 include the selected CSV output folder through `-RunCsvOutputFolder`, so scheduled runs keep writing to the intended location.

---

## Creating an Input File from Manual Selections

When the operator runs in manual mode and selects one or more discovered groups, mk5 asks:

```text
Do you want to create an input file from your selected groups? Type Y for yes or N for no
```

If the operator answers `Y`, mk5 creates a plain text input file with one selected group name per line.

Default generated input filename:

```text
C:\temp\ADgroupaudit_selected_groups_input_mk5_<timestamp>.txt
```

The generated file includes comment lines at the top with context about the source manual search and selected menu numbers. Those comment lines start with `#`, so mk5 ignores them during future input-file runs.

After creating the file, mk5 asks whether to save that generated file as the default input path:

```text
Save this generated input file as the default input path for future runs? Type Y for yes or N for no
```

If the operator answers `Y`, mk5 writes the path to:

```text
C:\temp\ADgroupaudit_default_input_path.txt
```

This prompt does not appear during file-mode runs or scheduled/non-interactive runs.

---

## Scheduled Task Flow

If the operator answers `Y` to:

```text
Do you want to create a scheduled task with these inputs?
```

mk5 then prompts for:

- Scheduled task name, default `ADgroupaudit_mk5_Daily`
- Daily run time in `HH:mm` format, default `08:00`
- Whether to overwrite the task if the name already exists

The task is registered for the current Windows user with:

- `powershell.exe`
- `-NoProfile`
- `-ExecutionPolicy Bypass`
- `-File "<path to ADgroupaudit_mk5.ps1>"`
- `-NonInteractive`
- `-SkipSchedulePrompt`
- Saved run input parameters

The scheduled task principal uses `-RunLevel Limited`, which is the built-in ScheduledTasks enum value for non-elevated execution. If the audit must run elevated in a controlled admin environment, change that value to `Highest` after confirming the security requirement.

The task runs locally and does not start the dashboard.

---

## Non-Interactive Parameters

mk5 supports these parameters for scheduled or automated execution:

| Parameter | Purpose |
|---|---|
| `-NonInteractive` | Enables scheduled/automated replay mode. |
| `-SkipSchedulePrompt` | Prevents prompting to create a scheduled task. |
| `-RunInputMode Manual` | Uses manual search replay mode. |
| `-RunInputMode File` | Uses file input replay mode. |
| `-RunManualSearchInput "<term>"` | Search term for manual replay mode. |
| `-RunInputFilePath "<path>"` | Input file path for file replay mode. |
| `-RunSelectedGroupNumbers "ALL"` | Group menu selection to replay. |
| `-RunEnumerateMembers "Yes"` | Enumerates members. Use `No` to skip. |
| `-RunCsvOutputFolder "<path>"` | Writes compiled CSVs to the selected folder during scheduled or automated runs. |

Manual replay example:

```powershell
PowerShell.exe -NoProfile -ExecutionPolicy Bypass -File C:\temp\ADgroupaudit_mk5.ps1 -NonInteractive -SkipSchedulePrompt -RunInputMode Manual -RunManualSearchInput "Admin" -RunSelectedGroupNumbers "ALL" -RunEnumerateMembers "Yes" -RunCsvOutputFolder "C:\AuditRuns\csv"
```

File replay example:

```powershell
PowerShell.exe -NoProfile -ExecutionPolicy Bypass -File C:\temp\ADgroupaudit_mk5.ps1 -NonInteractive -SkipSchedulePrompt -RunInputMode File -RunInputFilePath "C:\temp\ad_groups_to_audit.txt" -RunSelectedGroupNumbers "ALL" -RunEnumerateMembers "Yes" -RunCsvOutputFolder "C:\AuditRuns\csv"
```

---

## Important Scheduling Note

Scheduled tasks replay the selected group menu numbers from the interactive run.

If you schedule `ALL`, future runs will select all discovered groups after the search is performed.

If you schedule specific numbers such as `1,2,4`, those numbers are applied to the future run's discovered group menu. If AD search results change, the numbered menu may change too. For repeatable scheduled audits, `ALL` is usually safer when the input terms are already scoped.

---

## Privacy and Safety

mk5 remains read-only against Active Directory.

It does not:

- Modify AD users
- Modify AD groups
- Change memberships
- Launch the dashboard automatically
- Start a web server
- Send data externally

The script writes:

```text
<selected csv output folder>\AD_Group_Search_Compiled_mk5_<timestamp>.csv
```

If the operator chooses to save an input-file default, it may also write:

```text
C:\temp\ADgroupaudit_default_input_path.txt
```

If the operator chooses to create a scheduled task, it writes a Windows Scheduled Task registration for the current user.

---

## Troubleshooting

### Scheduled task creation fails

Likely causes:

- The current user cannot register scheduled tasks.
- The task name is invalid.
- The run time was not entered in `HH:mm` format.
- Local policy restricts scheduled task creation.
- The ScheduledTasks module rejects an invalid run level. Valid run levels are `Limited` and `Highest`.

Check task registration manually:

```powershell
Get-ScheduledTask -TaskName ADgroupaudit_mk5_Daily
```

### Scheduled task runs but produces no useful output

Check:

- The machine has the Active Directory PowerShell module.
- The scheduled user has AD read permissions.
- The input file path still exists if file mode was scheduled.
- The scheduled selection still matches the future discovered group menu.

### Scheduled task waits for input

Confirm the task action includes:

```text
-NonInteractive -SkipSchedulePrompt
```

Without those switches, the audit script will prompt like a normal interactive run.
