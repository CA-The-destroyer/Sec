# cis_modules/banners.py
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.7 Banners"
    # 1.7.2 Ensure local login warning banner is configured
    _run_check_fix(section,
                   "Ensure /etc/issue is configured",
                   "test -f /etc/issue",
                   "echo 'Authorized uses only' > /etc/issue",
                   verify_only, REPORT, log)
    # 1.7.3 Ensure remote login warning banner is configured
    _run_check_fix(section,
                   "Ensure /etc/issue.net is configured",
                   "test -f /etc/issue.net",
                   "echo 'Authorized uses only' > /etc/issue.net",
                   verify_only, REPORT, log)