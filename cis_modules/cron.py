# cis_modules/cron.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.4 Job Schedulers"

    # 2.4.1.2 Ensure permissions on /etc/crontab are configured
    _run_check_fix(
        section,
        "Ensure /etc/crontab permissions are 600 root:root",
        "stat -c '%a %U:%G' /etc/crontab | grep -q '^600 root:root$'",
        "chmod 600 /etc/crontab && chown root:root /etc/crontab",
        verify_only, REPORT, log
    )

    # 2.4.1.3 Ensure permissions on /etc/cron.hourly are configured
    _run_check_fix(
        section,
        "Ensure /etc/cron.hourly permissions are 700 root:root",
        "stat -c '%a %U:%G' /etc/cron.hourly | grep -q '^700 root:root$'",
        "chmod 700 /etc/cron.hourly && chown root:root /etc/cron.hourly",
        verify_only, REPORT, log
    )

    # 2.4.1.4 Ensure permissions on /etc/cron.daily are configured
    _run_check_fix(
        section,
        "Ensure /etc/cron.daily permissions are 700 root:root",
        "stat -c '%a %U:%G' /etc/cron.daily | grep -q '^700 root:root$'",
        "chmod 700 /etc/cron.daily && chown root:root /etc/cron.daily",
        verify_only, REPORT, log
    )

    # 2.4.1.5 Ensure permissions on /etc/cron.weekly are configured
    _run_check_fix(
        section,
        "Ensure /etc/cron.weekly permissions are 700 root:root",
        "stat -c '%a %U:%G' /etc/cron.weekly | grep -q '^700 root:root$'",
        "chmod 700 /etc/cron.weekly && chown root:root /etc/cron.weekly",
        verify_only, REPORT, log
    )

    # 2.4.1.6 Ensure permissions on /etc/cron.monthly are configured
    _run_check_fix(
        section,
        "Ensure /etc/cron.monthly permissions are 700 root:root",
        "stat -c '%a %U:%G' /etc/cron.monthly | grep -q '^700 root:root$'",
        "chmod 700 /etc/cron.monthly && chown root:root /etc/cron.monthly",
        verify_only, REPORT, log
    )

    # 2.4.1.7 Ensure permissions on /etc/cron.d are configured
    _run_check_fix(
        section,
        "Ensure /etc/cron.d permissions are 700 root:root",
        "stat -c '%a %U:%G' /etc/cron.d | grep -q '^700 root:root$'",
        "chmod 700 /etc/cron.d && chown root:root /etc/cron.d",
        verify_only, REPORT, log
    )

    # 2.4.1.8 Ensure cron is restricted to authorized users (using cron.allow)
    _run_check_fix(
        section,
        "Ensure only root is in /etc/cron.allow",
        "grep -Ex '^root$' /etc/cron.allow && [[ $(wc -l < /etc/cron.allow) -eq 1 ]]",
        "echo 'root' > /etc/cron.allow && chmod 600 /etc/cron.allow && chown root:root /etc/cron.allow",
        verify_only, REPORT, log
    )

