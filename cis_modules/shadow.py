# cis_modules/shadow.py

from cis_modules import _run_check_fix
import pwd
from pathlib import Path

def run_section(verify_only, REPORT, log):
    section = "5.4 User Accounts and Environment"

    # 5.4.1.1 Ensure password expiration is configured (90 days)
    _run_check_fix(
        section,
        "Ensure password expiration is set to 90 days",
        "grep -E '^PASS_MAX_DAYS\\s+90' /etc/login.defs",
        "sed -i.bak -E 's/^PASS_MAX_DAYS\\s+[0-9]+/PASS_MAX_DAYS   90/' /etc/login.defs",
        verify_only, REPORT, log
    )

    # 5.4.1.3 Ensure password expiration warning days is configured (7 days)
    _run_check_fix(
        section,
        "Ensure password expiration warning days is set to 7",
        "grep -E '^PASS_WARN_AGE\\s+7' /etc/login.defs",
        "sed -i.bak -E 's/^PASS_WARN_AGE\\s+[0-9]+/PASS_WARN_AGE   7/' /etc/login.defs",
        verify_only, REPORT, log
    )

    # 5.4.1.5 Ensure inactive password lock is configured (30 days)
    _run_check_fix(
        section,
        "Ensure inactive password lock is set to 30 days",
        "grep -E '^INACTIVE\\s+30' /etc/default/useradd",
        "sed -i.bak -E 's/^INACTIVE\\s+[0-9]+/INACTIVE   30/' /etc/default/useradd",
        verify_only, REPORT, log
    )

    # 5.4.2.5 Ensure root path integrity
    root_profile = Path("/root/.bash_profile")
    if not (root_profile.exists() and "export PATH=" in root_profile.read_text()):
        _run_check_fix(
            section,
            "Ensure root PATH integrity",
            f"grep -E '^export PATH=.*(/s?bin)' {root_profile}",
            (
                "echo 'export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' "
                ">> /root/.bash_profile"
            ),
            verify_only, REPORT, log
        )
    else:
        log(f"[✔] {section} - root PATH already configured")

    # 5.4.2.7 Ensure system accounts do not have a valid login shell (exclude root)
    # Change filter from '$3 < 1000' to '$3 > 0 && $3 < 1000' so UID 0 (root) is skipped.
    _run_check_fix(
        section,
        "Ensure system accounts shell is set to /sbin/nologin (excluding root)",
        "awk -F: '$3 > 0 && $3 < 1000 {print $1}' /etc/passwd | "
        "xargs -I {} grep -E '^{}:.*:/sbin/nologin$' /etc/passwd",
        (
            "awk -F: '$3 > 0 && $3 < 1000 {print $1}' /etc/passwd | "
            "xargs -r -n1 usermod -s /sbin/nologin"
        ),
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
