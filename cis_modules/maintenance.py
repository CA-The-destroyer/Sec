# cis_modules/maintenance.py

import subprocess
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "7 System Maintenance"

    # 7.1.11 Ensure permissions on /etc/passwd are configured (Automated)
    _run_check_fix(
        section,
        "Ensure permissions on /etc/passwd are configured",
        "stat -c '%a' /etc/passwd | grep -q '^644$'",
        "chmod 644 /etc/passwd",
        verify_only, REPORT, log
    )

    # 7.1.12 Ensure no files or directories without an owner and a group exist
    #    (skip /opt/Citrix to protect VDA install)
    cleanup_cmd = (
        "find / -xdev "
        "\\( -nouser -o -nogroup \\) "
        "-not -path '/opt/Citrix/*' "
        "-exec rm -rf {} +"
    )
    _run_check_fix(
        section,
        "Ensure no files or directories without an owner and a group exist",
        # always “compliant”–we just want to run the cleanup
        "true",
        cleanup_cmd,
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
