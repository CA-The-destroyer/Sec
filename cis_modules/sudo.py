# cis_modules/sudo.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.2 Sudo"

    # 5.2.2 Ensure sudo commands use a pty
    _run_check_fix(
        section,
        "Ensure sudo commands use a pty",
        "grep -E '^Defaults\\s+requiretty' /etc/sudoers",
        "sed -i '/^Defaults\\s\\+requiretty/d' /etc/sudoers && echo 'Defaults    requiretty' >> /etc/sudoers",
        verify_only, REPORT, log
    )

    # 5.2.3 Ensure sudo log file exists
    _run_check_fix(
        section,
        "Ensure sudo logfile is defined and exists",
        "grep -E '^Defaults.*logfile=' /etc/sudoers",
        "sed -i '/^Defaults.*logfile=/d' /etc/sudoers && "
        "echo 'Defaults    logfile=\"/var/log/sudo.log\"' >> /etc/sudoers && "
        "touch /var/log/sudo.log && chmod 600 /var/log/sudo.log",
        verify_only, REPORT, log
    )

    # 5.2.7 Ensure access to the su command is restricted
    _run_check_fix(
        section,
        "Ensure su is restricted to wheel group",
        "grep -E '^auth.*pam_wheel.so use_uid' /etc/pam.d/su",
        "sed -i '/pam_wheel.so use_uid/d' /etc/pam.d/su && echo 'auth    required pam_wheel.so use_uid' >> /etc/pam.d/su",
        verify_only, REPORT, log
    )
