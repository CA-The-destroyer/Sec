# cis_modules/packages.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.2 Package Management"

    # 1.2.1.2 Ensure gpgcheck=1 in /etc/dnf/dnf.conf
    _run_check_fix(
        section,
        "Ensure gpgcheck=1 in /etc/dnf/dnf.conf",
        "grep -E '^\\s*gpgcheck\\s*=\\s*1' /etc/dnf/dnf.conf",
        "sed -i '/^\\s*gpgcheck\\s*=\\s*/d' /etc/dnf/dnf.conf && echo 'gpgcheck=1' >> /etc/dnf/dnf.conf",
        verify_only, REPORT, log
    )

    # 1.2.2.1 Ensure no pending updates
    _run_check_fix(
        section,
        "Ensure no pending updates (dnf check-update)",
        "dnf makecache -q && dnf check-update -q",
        "dnf -y update && dnf clean all",
        verify_only, REPORT, log
    )
