# cis_modules/sudo.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.2 Sudo"

    # === ORIGINAL IMPLEMENTATION ===
    _run_check_fix(
        section, "Ensure sudo requiretty",
        "grep -E '^Defaults\\s+requiretty' /etc/sudoers",
        "echo 'Defaults requiretty' >> /etc/sudoers",
        verify_only, REPORT, log
    )
    _run_check_fix(
        section, "Ensure sudo log file exists",
        "grep -E '^Defaults\\s+logfile' /etc/sudoers",
        "echo 'Defaults logfile=\"/var/log/sudo.log\"' >> /etc/sudoers && touch /var/log/sudo.log && chmod 600 /var/log/sudo.log",
        verify_only, REPORT, log
    )
    _run_check_fix(
        section, "Ensure su restricted to wheel",
        "grep -E '^auth.*pam_wheel.so use_uid' /etc/pam.d/su",
        "echo 'auth required pam_wheel.so use_uid' >> /etc/pam.d/su",
        verify_only, REPORT, log
    )

    # === UPDATED IMPLEMENTATION ===
    _run_check_fix(
        section, "Ensure sudo requiretty (idempotent)",
        "grep -E '^Defaults\\s+requiretty' /etc/sudoers",
        "sed -i '/^Defaults\\s\\+requiretty/d' /etc/sudoers && echo 'Defaults requiretty' >> /etc/sudoers",
        verify_only, REPORT, log
    )
    _run_check_fix(
        section, "Ensure sudo logfile (idempotent)",
        "grep -E '^Defaults\\s+logfile' /etc/sudoers",
        "sed -i '/^Defaults\\s\\+logfile/d' /etc/sudoers && echo 'Defaults logfile=\"/var/log/sudo.log\"' >> /etc/sudoers && touch /var/log/sudo.log && chmod 600 /var/log/sudo.log",
        verify_only, REPORT, log
    )
    _run_check_fix(
        section, "Ensure su restricted to wheel (idempotent)",
        "grep -E '^auth.*pam_wheel.so use_uid' /etc/pam.d/su",
        "sed -i '/pam_wheel.so use_uid/d' /etc/pam.d/su && echo 'auth required pam_wheel.so use_uid' >> /etc/pam.d/su",
        verify_only, REPORT, log
    )
