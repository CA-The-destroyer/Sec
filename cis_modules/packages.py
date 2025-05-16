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
        # Pass only if a line "gpgcheck=1" exists (ignoring whitespace)
        "grep -E '^\\s*gpgcheck\\s*=\\s*1' /etc/dnf/dnf.conf",
        # Remove any existing gpgcheck lines, then append the correct one
        "sed -i '/^\\s*gpgcheck\\s*=/d' /etc/dnf/dnf.conf && "
        "echo 'gpgcheck=1' >> /etc/dnf/dnf.conf",
        verify_only, REPORT, log
    )

    #
    # 1.2.2.1 Ensure updates, patches, and additional security software are installed
    #
    _run_check_fix(
        section,
        "Ensure no pending package updates",
        # Make the cache, then ensure "dnf check-update" returns non-zero if updates exist
        "dnf makecache -q && ! dnf check-update -q",
        # If updates exist, install them and clean up
        "dnf -y update --best --allowerasing && dnf clean all",
        verify_only, REPORT, log
    )
