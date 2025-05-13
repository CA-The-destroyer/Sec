# cis_modules/selinux.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.3 SELinux"

    # … (other SELinux checks) …

    # 1.3.1.8 Ensure setroubleshoot-server is not installed
    _run_check_fix(
        section,
        "Ensure setroubleshoot-server is not installed",
        "rpm -q setroubleshoot-server",
        "dnf remove -y setroubleshoot-server",
        verify_only, REPORT, log
    )
