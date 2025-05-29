# cis_modules/banners.py

from cis_modules import _run_check_fix


def run_section(verify_only, REPORT, log):
    section = "1.7 Configure Command Line Warning Banners"

    # 1.7.2 Ensure local login warning banner is configured properly (/etc/issue)
    _run_check_fix(
        section,
        "Ensure local login warning banner is configured properly",
        "grep -Eq '^\\n?Authorized uses only\\.!' /etc/issue",
        "echo -e '
Authorized uses only. All activity may be monitored and reported.' | sudo tee /etc/issue",
        verify_only, REPORT, log
    )

    # 1.7.3 Ensure remote login warning banner is configured properly (/etc/issue.net)
    _run_check_fix(
        section,
        "Ensure remote login warning banner is configured properly",
        "grep -Eq '^\\n?Authorized uses only\\.!' /etc/issue.net",
        "echo -e '
Authorized uses only. All activity may be monitored and reported.' | sudo tee /etc/issue.net",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
