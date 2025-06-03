# cis_modules/banners.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.7 Banners"

    # 1.7.1 Ensure /etc/motd exists (even if empty)
    _run_check_fix(
        section,
        "Ensure /etc/motd exists",
        "test -f /etc/motd",
        "touch /etc/motd",
        verify_only, REPORT, log
    )

    # 1.7.2 Ensure local login warning banner is configured (/etc/issue)
    _run_check_fix(
        section,
        "Ensure /etc/issue configured",
        "test -s /etc/issue",
        "echo 'Unauthorized use is prohibited. All activity may be monitored.' > /etc/issue",
        verify_only, REPORT, log
    )

    # 1.7.3 Ensure remote login warning banner is configured (/etc/issue.net)
    _run_check_fix(
        section,
        "Ensure /etc/issue.net configured",
        "test -s /etc/issue.net",
        "echo 'Unauthorized use is prohibited. All activity may be monitored.' > /etc/issue.net",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
