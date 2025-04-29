# cis_modules/__init__.py

import subprocess

def _run_check_fix(section, description, check_cmd, fix_cmd, verify_only, REPORT, log):
    try:
        result = subprocess.run(check_cmd, shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        compliant = (result.returncode == 0)
        status = "Compliant" if compliant else "Non-compliant"
        if not compliant and not verify_only and fix_cmd:
            fix = subprocess.run(fix_cmd, shell=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            status = "Fixed" if fix.returncode == 0 else "Fix failed"
        log(f"[{status}] {section} - {description}")
        REPORT.append((section, description, status))
    except Exception as e:
        log(f"[Error] {section} - {description}: {e}")
        REPORT.append((section, description, f"Error: {e}"))
