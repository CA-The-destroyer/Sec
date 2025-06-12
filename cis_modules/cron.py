# cis_modules/cron.py

import subprocess
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.4 Cron & At"

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

    # 2.4.1.8 Ensure crontab is restricted to authorized users (cron.allow root only)
    _run_check_fix(
        section,
        "Ensure cron.allow is root only",
        "test -f /etc/cron.allow && grep -q '^root$' /etc/cron.allow",
        "echo root > /etc/cron.allow && chmod 600 /etc/cron.allow",
        verify_only, REPORT, log
    )

    # 2.4.1.8 Ensure cron.deny is empty or missing
    _run_check_fix(
        section,
        "Ensure cron.deny is empty or missing",
        "! test -f /etc/cron.deny || grep -q '^$' /etc/cron.deny",
        ": > /etc/cron.deny && chmod 644 /etc/cron.deny",
        verify_only, REPORT, log
    )

    # 2.4.2.1 Ensure at is restricted to authorized users (at.allow root only)
    _run_check_fix(
        section,
        "Ensure at.allow is root only",
        "test -f /etc/at.allow && grep -q '^root$' /etc/at.allow",
        "echo root > /etc/at.allow && chmod 600 /etc/at.allow",
        verify_only, REPORT, log
    )

    # 2.4.2.1 Ensure at.deny is empty or missing
    _run_check_fix(
        section,
        "Ensure at.deny is empty or missing",
        "! test -f /etc/at.deny || grep -q '^$' /etc/at.deny",
        ": > /etc/at.deny && chmod 644 /etc/at.deny",
        verify_only, REPORT, log
    )

    # 2.4.x Ensure no-owner files are removed under /tmp and /var/tmp (skip /opt/Citrix)
    cleanup_cmd = (
        "find /tmp /var/tmp -xdev "
        "\\( -nouser -o -nogroup \\) "
        "-not -path '/opt/Citrix/*' "
        "-exec rm -rf {} +"
    )
    _run_check_fix(
        section,
        "Ensure orphan files under /tmp and /var/tmp are removed (excl. /opt/Citrix)",
        "true",  # always runs the fix
        cleanup_cmd,
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
