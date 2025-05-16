# cis_modules/shadow.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.4 Shadow Password Suite"

    #
    # 5.4.1.1 Ensure password expiration is configured (max 90 days)
    #
    _run_check_fix(
        section,
        "Ensure password expiration is configured (maxdays=90)",
        "grep -E '^PASS_MAX_DAYS\s+90' /etc/login.defs",
        "sed -i '/^PASS_MAX_DAYS/s/[0-9]\\+/90/' /etc/login.defs",
        verify_only, REPORT, log
    )

    #
    # 5.4.1.3 Ensure password warning days is configured (warn_age=7)
    #
    _run_check_fix(
        section,
        "Ensure password expiration warning days is configured (WARN_AGE=7)",
        "grep -E '^WARN_AGE\s+7' /etc/login.defs",
        "sed -i '/^WARN_AGE/s/[0-9]\\+/7/' /etc/login.defs",
        verify_only, REPORT, log
    )

    #
    # 5.4.1.5 Ensure inactive password lock is configured (INACTIVE=30)
    #
    _run_check_fix(
        section,
        "Ensure inactive password lock is configured (INACTIVE=30)",
        "grep -E '^INACTIVE\s+30' /etc/login.defs",
        "sed -i '/^INACTIVE/s/[0-9]\\+/30/' /etc/login.defs",
        verify_only, REPORT, log
    )
