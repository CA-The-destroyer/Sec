# cis_modules/packages.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.2 Package Management"

    #
    # 1.2.1.2 Ensure gpgcheck is globally activated
    #
    _run_check_fix(
        section,
        "Ensure gpgcheck=1 in /etc/dnf/dnf.conf",
        "grep -E '^\\s*gpgcheck\\s*=\\s*1' /etc/dnf/dnf.conf",
        # Remove all gpgcheck lines and enforce gpgcheck=1
        "sed -i '/^\\s*gpgcheck\\s*=\\s*/d' /etc/dnf/dnf.conf && "
        "echo 'gpgcheck=1' >> /etc/dnf/dnf.conf",
        verify_only, REPORT, log
    )

    #
    # 1.2.2.1 Ensure updates, patches, and additional security software are installed
    #
    _run_check_fix(
        section,
        "Ensure all packages are up to date",
        # Check-update returns non-zero when no updates are available
        "dnf makecache -q && ! dnf check-update -q",
        # Apply all updates (including security), then clean cache
        "dnf -y upgrade --setopt=obsoletes=1 && dnf clean all",
        verify_only, REPORT, log
    )
