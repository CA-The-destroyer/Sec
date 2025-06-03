# cis_modules/cron.py

import subprocess
from pathlib import Path
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.4 Job Schedulers (cron/at)"

    # 2.4.1.2 Ensure permissions on /etc/crontab are configured (644)
    _run_check_fix(
        section,
        "Ensure permissions on /etc/crontab are configured",
        "stat -c '%a' /etc/crontab | grep -q '^644$'",
        "chmod 644 /etc/crontab",
        verify_only, REPORT, log
    )

    # 2.4.1.3 Ensure permissions on /etc/cron.hourly are configured (755)
    _run_check_fix(
        section,
        "Ensure permissions on /etc/cron.hourly are configured",
        "stat -c '%a' /etc/cron.hourly | grep -q '^755$'",
        "chmod 755 /etc/cron.hourly",
        verify_only, REPORT, log
    )

    # 2.4.1.4 Ensure permissions on /etc/cron.daily are configured (755)
    _run_check_fix(
        section,
        "Ensure permissions on /etc/cron.daily are configured",
        "stat -c '%a' /etc/cron.daily | grep -q '^755$'",
        "chmod 755 /etc/cron.daily",
        verify_only, REPORT, log
    )

    # 2.4.1.5 Ensure permissions on /etc/cron.weekly are configured (755)
    _run_check_fix(
        section,
        "Ensure permissions on /etc/cron.weekly are configured",
        "stat -c '%a' /etc/cron.weekly | grep -q '^755$'",
        "chmod 755 /etc/cron.weekly",
        verify_only, REPORT, log
    )

    # 2.4.1.6 Ensure permissions on /etc/cron.monthly are configured (755)
    _run_check_fix(
        section,
        "Ensure permissions on /etc/cron.monthly are configured",
        "stat -c '%a' /etc/cron.monthly | grep -q '^755$'",
        "chmod 755 /etc/cron.monthly",
        verify_only, REPORT, log
    )

    # 2.4.1.7 Ensure permissions on /etc/cron.d are configured (755)
    _run_check_fix(
        section,
        "Ensure permissions on /etc/cron.d are configured",
        "stat -c '%a' /etc/cron.d | grep -q '^755$'",
        "chmod 755 /etc/cron.d",
        verify_only, REPORT, log
    )

    # 2.4.1.8 Ensure crontab is restricted to authorized users
    #    cron.allow should exist (and contain at least 'root'), cron.deny should either not exist or be mode 644 with minimal contents
    cron_allow = Path("/etc/cron.allow")
    cron_deny = Path("/etc/cron.deny")

    # If cron.allow exists, ensure root is in it; if not, create it
    if not cron_allow.exists() or not subprocess.run("grep -q '^root$' /etc/cron.allow", shell=True).returncode == 0:
        fix_cmd = (
            "echo 'root' >> /etc/cron.allow && "
            "chmod 600 /etc/cron.allow"
        )
    else:
        fix_cmd = None

    _run_check_fix(
        section,
        "Ensure cron.allow exists and only contains authorized users",
        "test -f /etc/cron.allow && grep -q '^root$' /etc/cron.allow",
        fix_cmd,
        verify_only, REPORT, log
    )

    # Ensure cron.deny either does not exist or is empty and mode 644
    if cron_deny.exists():
        fix_cron_deny = "truncate -s 0 /etc/cron.deny && chmod 644 /etc/cron.deny"
    else:
        fix_cron_deny = None

    _run_check_fix(
        section,
        "Ensure cron.deny is empty or does not exist",
        "test ! -f /etc/cron.deny || (grep -q '^$' /etc/cron.deny && stat -c '%a' /etc/cron.deny | grep -q '^644$')",
        fix_cron_deny,
        verify_only, REPORT, log
    )

    # 2.4.2.1 Ensure at is restricted to authorized users
    #    at.allow should exist with 'root'; at.deny should not exist or be empty.
    at_allow = Path("/etc/at.allow")
    at_deny = Path("/etc/at.deny")

    if not at_allow.exists() or not subprocess.run("grep -q '^root$' /etc/at.allow", shell=True).returncode == 0:
        fix_at_allow = "echo 'root' >> /etc/at.allow && chmod 600 /etc/at.allow"
    else:
        fix_at_allow = None

    _run_check_fix(
        section,
        "Ensure at.allow exists and only contains authorized users",
        "test -f /etc/at.allow && grep -q '^root$' /etc/at.allow",
        fix_at_allow,
        verify_only, REPORT, log
    )

    if at_deny.exists():
        fix_at_deny = "truncate -s 0 /etc/at.deny && chmod 644 /etc/at.deny"
    else:
        fix_at_deny = None

    _run_check_fix(
        section,
        "Ensure at.deny is empty or does not exist",
        "test ! -f /etc/at.deny || (grep -q '^$' /etc/at.deny && stat -c '%a' /etc/at.deny | grep -q '^644$')",
        fix_at_deny,
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
