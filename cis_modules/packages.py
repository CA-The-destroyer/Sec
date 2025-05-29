# cis_modules/packages.py

from cis_modules import _run_check_fix


def run_section(verify_only, REPORT, log):
    section = "1.2 Package Management"

    # 1.2.1.2 Ensure gpgcheck is globally activated
    _run_check_fix(
        section,
        "Ensure GPG package verification is enabled globally",
        "grep -Eqs '^\\s*gpgcheck\\s*=\\s*1' /etc/dnf/dnf.conf",
        # Replace or append gpgcheck=1
        "sed -i.bak -E 's/^\\s*gpgcheck\\s*=.*/gpgcheck=1/' /etc/dnf/dnf.conf || echo 'gpgcheck=1' >> /etc/dnf/dnf.conf",
        verify_only, REPORT, log
    )

    # 1.2.2.1 Ensure updates, patches, and additional security software are installed,
    #             but do NOT remove Citrix VDA RPMs under /opt/Citrix/VDA.
    _run_check_fix(
        section,
        "Ensure all packages are up to date (excluding Citrix VDA)",
        # Check no updates pending
        "dnf makecache -q && ! dnf check-update -q",
        # Upgrade excluding ctx-vda* and clean metadata
        "dnf -y upgrade --exclude=ctx-vda* --setopt=obsoletes=1 && dnf clean all",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
