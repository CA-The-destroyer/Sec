# cis_modules/selinux.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.3 SELinux"

    # 1.3.1.1 Ensure SELinux is installed
    _run_check_fix(
        section,
        "Ensure SELinux policy package is installed",
        "rpm -q selinux-policy-targeted",
        "dnf -y install selinux-policy-targeted",
        verify_only, REPORT, log
    )

    # 1.3.1.3 Ensure SELinux policy is configured (enforcing or permissive)
    _run_check_fix(
        section,
        "Ensure SELinux configuration file exists",
        "test -f /etc/selinux/config",
        None,  # no single‐line fix; assume the package provides it
        verify_only, REPORT, log
    )

    # 1.3.1.4 Ensure the SELinux mode is not disabled
    _run_check_fix(
        section,
        "Ensure SELinux is not disabled in /etc/selinux/config",
        "grep -E '^SELINUX=(enforcing|permissive)' /etc/selinux/config",
        "sed -i.bak -E 's/^SELINUX=.*/SELINUX=permissive/' /etc/selinux/config && setenforce 0",
        verify_only, REPORT, log
    )

    # 1.3.1.8 Ensure SETroubleshoot is not installed
    _run_check_fix(
        section,
        "Ensure SETroubleshoot is not installed",
        "rpm -q setroubleshoot-server",
        "dnf -y remove setroubleshoot-server",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
