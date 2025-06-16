# cis_modules/service_cleanup.py

import subprocess
from cis_modules import _run_check_fix

def _package_installed(pkg: str) -> bool:
    return subprocess.run(
        ["rpm", "-q", pkg],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode == 0

def run_section(verify_only, REPORT, log):
    section = "2.1–2.2 Service Cleanup"

    # 2.2.4 Ensure telnet client is not installed
    _run_check_fix(
        section,
        "Ensure telnet client is not installed",
        "rpm -q telnet",
        "dnf remove -y --noautoremove telnet",
        verify_only, REPORT, log
    )

    # 2.2.x Remove other unnecessary client packages
    for pkg in ("setroubleshoot-server", "openldap-clients", "ypbind", "tftp"):
        desc = f"Ensure {pkg} is not installed"
        check_cmd = f"rpm -q {pkg}"
        fix_cmd = f"dnf remove -y --noautoremove {pkg}"
        _run_check_fix(
            section,
            desc,
            check_cmd,
            fix_cmd,
            verify_only, REPORT, log
        )

    # 2.1.11 Ensure CUPS (print server) service is disabled and stopped
    _run_check_fix(
        section,
        "Ensure CUPS (print server) is disabled and stopped",
        "! systemctl is-enabled --quiet cups.service && ! systemctl is-active --quiet cups.service",
        "systemctl disable --now cups.service || true",
        verify_only, REPORT, log
    )

    # 3.1.3 Ensure Bluetooth service is disabled and stopped
    _run_check_fix(
        section,
        "Ensure Bluetooth service is disabled and stopped",
        "! systemctl is-enabled --quiet bluetooth.service && ! systemctl is-active --quiet bluetooth.service",
        "systemctl disable --now bluetooth.service || true",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
