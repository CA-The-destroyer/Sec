# cis_modules/banners.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.7 Banners"

    # 1.7.2 Ensure local login banner (/etc/issue) 
    _run_check_fix(
        section,
        "Ensure /etc/issue is configured properly",
        "grep -q 'Authorized users only' /etc/issue",
        "echo 'Authorized users only. All activity may be monitored.' > /etc/issue",
        verify_only, REPORT, log
    )

    # 1.7.3 Ensure remote login banner (/etc/issue.net)
    _run_check_fix(
        section,
        "Ensure /etc/issue.net is configured properly",
        "grep -q 'Authorized users only' /etc/issue.net",
        "echo 'Authorized users only. All activity may be monitored.' > /etc/issue.net",
        verify_only, REPORT, log
    )
