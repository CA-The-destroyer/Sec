# cis_modules/sudo.py

from cis_modules import _run_check_fix


def run_section(verify_only, REPORT, log):
    section = "5.2 Configure Sudo"

    # 5.2.1 Ensure sudo package is installed
    _run_check_fix(
        section,
        "Ensure sudo package is installed",
        "rpm -q sudo",
        "dnf -y install sudo",
        verify_only, REPORT, log
    )

    # 5.2.2 Ensure sudo commands use pty
    _run_check_fix(
        section,
        "Ensure sudo commands use pty",
        "grep -E '^\\s*Defaults\\s+.*use_pty' /etc/sudoers",
        "echo 'Defaults use_pty' >> /etc/sudoers",
        verify_only, REPORT, log
    )

    # 5.2.3 Ensure sudo log file exists
    _run_check_fix(
        section,
        "Ensure sudo log file exists and sudoers configured",
        "grep -E '^\\s*Defaults\\s+.*logfile=/var/log/sudo.log' /etc/sudoers && test -f /var/log/sudo.log",
        (
            "touch /var/log/sudo.log && chmod 600 /var/log/sudo.log && "
            "echo 'Defaults logfile=/var/log/sudo.log' >> /etc/sudoers"
        ),
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
