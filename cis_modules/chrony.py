# cis_modules/cron.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.4 Job Schedulers"

    # 2.4.1.2–2.4.1.7 permissions
    for target, mode in [
        ("/etc/crontab",       "600"),
        ("/etc/cron.hourly",   "700"),
        ("/etc/cron.daily",    "700"),
        ("/etc/cron.weekly",   "700"),
        ("/etc/cron.monthly",  "700"),
        ("/etc/cron.d",        "700")
    ]:
        _run_check_fix(
            section,
            f"Ensure {target} permissions are {mode} root:root",
            f"stat -c '%a %U:%G' {target} | grep -q '^{mode} root:root$'",
            f"chmod {mode} {target} && chown root:root {target}",
            verify_only, REPORT, log
        )

    # 2.4.1.8 restrict to root
    _run_check_fix(
        section,
        "Ensure only root in /etc/cron.allow",
        "grep -Ex '^root$' /etc/cron.allow && [[ $(wc -l < /etc/cron.allow) -eq 1 ]]",
        "echo 'root' > /etc/cron.allow && chmod 600 /etc/cron.allow && chown root:root /etc/cron.allow",
        verify_only, REPORT, log
    )
