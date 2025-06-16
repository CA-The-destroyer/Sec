# cis_modules/cron_at.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.4 Cron & At"

    # 2.4.1.8 Ensure cron.allow is root only
    _run_check_fix(
        section,
        "Ensure /etc/cron.allow exists and contains only 'root'",
        # check: file exists, exactly one line 'root'
        "test -f /etc/cron.allow && grep -xq 'root' /etc/cron.allow && [ \"$(wc -l < /etc/cron.allow)\" -eq 1 ]",
        # fix: overwrite file, set permissions
        "printf 'root\n' > /etc/cron.allow && chmod 600 /etc/cron.allow",
        verify_only, REPORT, log
    )

    # 2.4.1.8 Ensure cron.deny is empty or absent
    _run_check_fix(
        section,
        "Ensure /etc/cron.deny is empty or absent",
        # check: either missing or zero‐length
        "! test -s /etc/cron.deny",
        # fix: truncate or create, set perms
        "printf '' > /etc/cron.deny && chmod 644 /etc/cron.deny",
        verify_only, REPORT, log
    )

    # 2.4.2.1 Ensure at.allow is root only
    _run_check_fix(
        section,
        "Ensure /etc/at.allow exists and contains only 'root'",
        "test -f /etc/at.allow && grep -xq 'root' /etc/at.allow && [ \"$(wc -l < /etc/at.allow)\" -eq 1 ]",
        "printf 'root\n' > /etc/at.allow && chmod 600 /etc/at.allow",
        verify_only, REPORT, log
    )

    # 2.4.2.1 Ensure /etc/at.deny is empty or absent
    _run_check_fix(
        section,
        "Ensure /etc/at.deny is empty or absent",
        "! test -s /etc/at.deny",
        "printf '' > /etc/at.deny && chmod 644 /etc/at.deny",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
