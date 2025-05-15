from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.2 Package Management"

    # Original checks
    _run_check_fix(
        section,
        "Ensure gpgcheck is globally activated",
        "grep -E '^\\s*gpgcheck\\s*=\\s*1' /etc/dnf/dnf.conf",
        "sed -i '/^gpgcheck/d' /etc/dnf/dnf.conf && echo 'gpgcheck=1' >> /etc/dnf/dnf.conf",
        verify_only, REPORT, log
    )

    # Aggressive update enforcement
    _run_check_fix(
        section,
        "Ensure updates, patches, and additional security software are installed",
        "dnf makecache -q && ! dnf check-update -q",
        "dnf -y update && dnf clean all",
        verify_only, REPORT, log
    )
