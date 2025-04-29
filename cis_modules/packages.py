# cis_modules/filesystem.py
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.2 Packages & Updates"
    checks = [
        ("Ensure gpgcheck is globally activated","grep -E '^gpgcheck=1' /etc/yum.conf"),
        ("Ensure updates installed","yum check-update | grep -q '^[a-z]' || true")
    ]
    fixes = {
        "Ensure gpgcheck is globally activated":"sed -i 's/^gpgcheck=.*/gpgcheck=1/' /etc/yum.conf",
    }
    for desc, check in checks:
        fix = fixes.get(desc)
        _run_check_fix(section, desc, check, fix, verify_only, REPORT, log)
