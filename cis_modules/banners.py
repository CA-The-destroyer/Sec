# cis_modules/filesystem.py
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.7 Banners"
    banners = [
        ("Ensure /etc/motd exists","test -f /etc/motd"),
        ("Ensure /etc/issue configured","test -f /etc/issue"),
        ("Ensure /etc/issue.net configured","test -f /etc/issue.net")
    ]
    fixes = {
        "Ensure /etc/issue configured":"echo 'Authorized uses only' > /etc/issue",
        "Ensure /etc/issue.net configured":"echo 'Authorized uses only' > /etc/issue.net"
    }
    for desc, check in banners:
        fix = fixes.get(desc)
        _run_check_fix(section, desc, check, fix, verify_only, REPORT, log)
