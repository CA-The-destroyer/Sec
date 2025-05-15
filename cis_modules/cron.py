# cis_modules/cron.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.4 Job Schedulers"

    # Ensure /etc/cron.allow exists, contains only root, perms 600
    _run_check_fix(
        section,
        "Ensure only root is in /etc/cron.allow and perms are 600",
        "grep -xq 'root' /etc/cron.allow && [[ $(wc -l < /etc/cron.allow) -eq 1 ]] && stat -c '%a' /etc/cron.allow | grep -qx '600'",
        "echo 'root' > /etc/cron.allow && chmod 600 /etc/cron.allow && chown root:root /etc/cron.allow",
        verify_only, REPORT, log
    )

    # Ensure /etc/cron.deny exists and is empty, perms 600
    _run_check_fix(
        section,
        "Ensure /etc/cron.deny exists and is empty with perms 600",
        "[ -f /etc/cron.deny ] && [[ ! -s /etc/cron.deny ]] && stat -c '%a' /etc/cron.deny | grep -qx '600'",
        "touch /etc/cron.deny && > /etc/cron.deny && chmod 600 /etc/cron.deny && chown root:root /etc/cron.deny",
        verify_only, REPORT, log
    )

    # Ensure /etc/at.allow exists, contains only root, perms 600
    _run_check_fix(
        section,
        "Ensure only root is in /etc/at.allow and perms are 600",
        "grep -xq 'root' /etc/at.allow && [[ $(wc -l < /etc/at.allow) -eq 1 ]] && stat -c '%a' /etc/at.allow | grep -qx '600'",
        "echo 'root' > /etc/at.allow && chmod 600 /etc/at.allow && chown root:root /etc/at.allow",
        verify_only, REPORT, log
    )

    # Ensure /etc/at.deny exists and is empty, perms 600
    _run_check_fix(
        section,
        "Ensure /etc/at.deny exists and is empty with perms 600",
        "[ -f /etc/at.deny ] && [[ ! -s /etc/at.deny ]] && stat -c '%a' /etc/at.deny | grep -qx '600'",
        "touch /etc/at.deny && > /etc/at.deny && chmod 600 /etc/at.deny && chown root:root /etc/at.deny",
        verify_only, REPORT, log
    )
