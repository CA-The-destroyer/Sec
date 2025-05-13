# cis_modules/network.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "3.1 Network"

    # 3.1.3 Ensure bluetooth services are not in use
    _run_check_fix(
        section,
        "Ensure bluetooth is disabled",
        "systemctl is-enabled --quiet bluetooth",
        "dnf remove -y bluez",
        verify_only, REPORT, log
    )
