# cis_modules/chrony.py

from cis_modules import _run_check_fix


def run_section(verify_only, REPORT, log):
    section = "2.3 Configure Time Synchronization"

    # 2.3.1 Ensure time synchronization is in use (chrony)
    _run_check_fix(
        section,
        "Ensure chrony is installed",
        "rpm -q chrony",
        "dnf -y install chrony",
        verify_only, REPORT, log
    )

    # 2.3.2 Ensure chrony service is enabled and active
    _run_check_fix(
        section,
        "Ensure chrony service is enabled and running",
        "systemctl is-enabled chronyd && systemctl is-active chronyd",
        "systemctl enable chronyd && systemctl start chronyd",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
