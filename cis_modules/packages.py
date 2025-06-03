# cis_modules/packages.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.2 Packages & Updates"

    # 1.2.1.2 Ensure gpgcheck is globally activated
    _run_check_fix(
        section,
        "Ensure gpgcheck is globally activated",
        "grep -E '^gpgcheck=1' /etc/yum.conf",
        "sed -i.bak -E 's/^gpgcheck=.*/gpgcheck=1/' /etc/yum.conf",
        verify_only, REPORT, log
    )

    # 1.2.2.1 Ensure updates, patches, and additional security software are installed
    # We use 'dnf -y upgrade' to apply all available updates
    _run_check_fix(
        section,
        "Ensure updates are installed",
        "dnf check-update | grep -q '^[[:alnum:]]' || true",
        "dnf -y upgrade",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
