from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.3 SELinux"

    # Original SELinux checks would go here…

    # Aggressive removal of SETroubleshoot
    _run_check_fix(
        section,
        "Ensure setroubleshoot-server is not installed",
        "! rpm -q setroubleshoot-server",
        "systemctl disable --now setroubleshoot-server.service || true && dnf remove -y setroubleshoot-server",
        verify_only, REPORT, log
    )
