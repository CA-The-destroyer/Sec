# cis_modules/packages.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.2 Package Management"

    # 1.2.1.2 Ensure gpgcheck is globally activated
    _run_check_fix(
        section,
        "Ensure gpgcheck is globally activated",
        "grep -E '^gpgcheck=1' /etc/yum.conf",
        "sed -i 's/^gpgcheck=.*/gpgcheck=1/' /etc/yum.conf",
        verify_only, REPORT, log
    )

    # 1.2.2.1 Ensure package repositories are reachable (avoids hanging on 'yum check-update')
    _run_check_fix(
        section,
        "Ensure package repositories are reachable",
        "yum repolist enabled -q",
        None,
        verify_only, REPORT, log
    )
