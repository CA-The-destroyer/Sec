# cis_modules/network.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "3.1 Network Devices"

    # Remove and disable bluetooth (bluez)
    _run_check_fix(
        section,
        "Ensure bluetooth (bluez) is not installed or running",
        "! rpm -q bluez && ! systemctl is-enabled --quiet bluetooth.service && ! systemctl is-active --quiet bluetooth.service",
        "systemctl disable --now bluetooth.service || true && dnf remove -y bluez",
        verify_only, REPORT, log
    )
