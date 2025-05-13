# cis_modules/clients.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.2 Client Services"

    for pkg in ("ftp", "telnet", "nis", "ldap"): 
        _run_check_fix(
            section,
            f"Ensure {pkg} client is not installed",
            f"rpm -q {pkg}",
            f"dnf remove -y {pkg}",
            verify_only, REPORT, log
        )
