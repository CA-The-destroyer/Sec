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

    # 5.4.2.5 Ensure root PATH integrity
    root_profile = Path("/root/.bash_profile")
    has_path = root_profile.exists() and "export PATH=" in root_profile.read_text()
    if not has_path:
        _run_check_fix(
            section,
            "Ensure root PATH integrity",
            f"grep -E '^export PATH=.*(/s?bin)' {root_profile}",
            "echo \"export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\" >> /root/.bash_profile",
            verify_only, REPORT, log
        )
    else:
        log(f"[✔] {section} - root PATH already configured")

    # 5.4.2.7 Ensure system accounts do not have a valid login shell (excluding root & real users)
    # We'll treat UIDs < 1000 but > 100 as true system accounts (adjust threshold if needed)
    bad_shells = []
    for p in pwd.getpwall():
        if 100 < p.pw_uid < 1000 and p.pw_name != "root":
            if p.pw_shell not in ("/sbin/nologin", "/usr/sbin/nologin"):
                bad_shells.append(p.pw_name)

    if bad_shells:
        _run_check_fix(
            section,
            f"Set nologin shell for system accounts: {','.join(bad_shells)}",
            "echo OK",  # dummy: existence of bad_shells signals fix
            f"usermod -s /sbin/nologin {' '.join(bad_shells)}",
            verify_only, REPORT, log
        )
    else:
        log(f"[✔] {section} - all system accounts already nologin")

    log(f"[✔] {section} completed")
