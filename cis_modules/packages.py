# cis_modules/packages.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.2 Package Management"

    # 1.2.1.2 Ensure gpgcheck is globally activated
    _run_check_fix(
        section,
        "Ensure gpgcheck=1 in /etc/yum.conf",
        "grep -E '^\\s*gpgcheck\\s*=\\s*1' /etc/yum.conf",
        "sed -i '/^\\s*gpgcheck\\s*=\\s*/d' /etc/yum.conf && echo 'gpgcheck=1' >> /etc/yum.conf",
        verify_only, REPORT, log
    )

    # 1.2.2.1 Ensure updates, patches, and additional security software are installed
    _run_check_fix(
        section,
        "Ensure yum check-update returns no errors",
        "yum makecache -q && yum check-update -q",
        "yum -y update && yum clean all",
        verify_only, REPORT, log
    )
