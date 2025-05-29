# cis_modules/selinux.py

from cis_modules import _run_check_fix


def run_section(verify_only, REPORT, log):
    section = "1.3 Mandatory Access Control"

    # 1.3.1.1 Ensure SELinux is installed
    _run_check_fix(
        section,
        "Ensure SELinux packages are installed",
        "rpm -q libselinux policycoreutils selinux-policy-targeted",
        "dnf -y install libselinux policycoreutils selinux-policy-targeted",
        verify_only, REPORT, log
    )

    # 1.3.1.2 Ensure SELinux is not disabled in bootloader configuration
    _run_check_fix(
        section,
        "Ensure SELinux is not disabled in GRUB",
        "grep -E """\s*linux\S+.*\bselinux=0\b""" /etc/grub2.cfg",
        "sed -i.bak -E 's/\bselinux=0\b//' /etc/default/grub && grub2-mkconfig -o /etc/grub2.cfg",
        verify_only, REPORT, log
    )

    # 1.3.1.3 Ensure SELinux policy is configured
    _run_check_fix(
        section,
        "Ensure SELinux policy type is targeted",
        "grep -E '^SELINUXTYPE=targeted' /etc/selinux/config",
        "sed -i.bak -E 's/^SELINUXTYPE=.*/SELINUXTYPE=targeted/' /etc/selinux/config",
        verify_only, REPORT, log
    )

    # 1.3.1.4 Ensure SELinux mode is not disabled
    _run_check_fix(
        section,
        "Ensure SELinux mode is not disabled",
        "grep -E '^SELINUX=(enforcing|permissive)' /etc/selinux/config",
        "sed -i.bak -E 's/^SELINUX=disabled/SELINUX=enforcing/' /etc/selinux/config",
        verify_only, REPORT, log
    )

    # 1.3.1.5 Ensure SELinux mode is enforcing
    _run_check_fix(
        section,
        "Ensure SELinux is enforcing",
        "getenforce | grep -q Enforcing",
        "setenforce 1 && sed -i.bak -E 's/^SELINUX=.*/SELINUX=enforcing/' /etc/selinux/config",
        verify_only, REPORT, log
    )

    # 1.3.1.7 Ensure the MCS Translation Service (mcstrans) is not installed
    _run_check_fix(
        section,
        "Ensure mcstrans is not installed",
        "rpm -q mcstrans",
        "dnf -y remove mcstrans",
        verify_only, REPORT, log
    )

    # 1.3.1.8 Ensure SETroubleshoot is not installed
    _run_check_fix(
        section,
        "Ensure SETroubleshoot is not installed",
        "rpm -q setroubleshoot",
        "dnf -y remove setroubleshoot",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
