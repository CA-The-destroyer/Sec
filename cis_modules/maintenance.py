# cis_modules/maintenance.py

import os
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "7.1 System Maintenance"

    # 7.1.12 Ensure no files or directories without an owner and a group exist
    desc = "Ensure no files/directories without an owner or group exist"
    check_cmd = "find / -xdev \\( -nouser -o -nogroup \\)"
    fix_cmd = "find / -xdev \\( -nouser -o -nogroup \\) -exec rm -rf {} +"
    _run_check_fix(
        section,
        desc,
        check_cmd + " | grep -q .",
        fix_cmd,
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
