# cis_modules/banners.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.7 Banners"

    # Local login banner (/etc/issue)
    _run_check_fix(
        section,
        "Ensure local login warning banner is configured properly",
        "grep -q 'Authorized users only' /etc/issue",
        "echo 'Authorized users only. All activity may be monitored.' > /etc/issue",
        verify_only, REPORT, log
    )

    # Remote login banner (/etc/issue.net)
    _run_check_fix(
        section,
        "Ensure remote login warning banner is configured properly",
        "grep -q 'Authorized users only' /etc/issue.net",
        "echo 'Authorized users only. All activity may be monitored.' > /etc/issue.net",
        verify_only, REPORT, log
    )
