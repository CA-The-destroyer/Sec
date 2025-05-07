# cis_modules/sudo.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.2 Sudo"

    # 5.2.1 Ensure sudo is installed
    _run_check_fix(
        section,
        "Ensure sudo is installed",
        "rpm -q sudo",
        "yum install -y sudo",
        verify_only, REPORT, log
    )

    # 5.2.2 Ensure sudo commands use a pty
    _run_check_fix(
        section,
        "Ensure sudo requires a pty",
        "grep -E '^Defaults.*requiretty' /etc/sudoers",
        "echo 'Defaults requiretty' >> /etc/sudoers",
        verify_only, REPORT, log
    )

    # 5.2.7 Ensure su access is restricted
    _run_check_fix(
        section,
        "Ensure su is restricted to wheel group",
        "grep -E '^auth.*pam_wheel.so use_uid' /etc/pam.d/su",
        "echo 'auth required pam_wheel.so use_uid' >> /etc/pam.d/su",
        verify_only, REPORT, log
    )
