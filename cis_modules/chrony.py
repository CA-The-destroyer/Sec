# cis_modules/chrony.py

import subprocess
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.3 Configure Time Synchronization"

    # 2.3.1 Ensure time synchronization is in use (chronyd installed & running)
    _run_check_fix(
        section,
        "Ensure chrony is installed",
        "rpm -q chrony",
        "dnf -y install chrony",
        verify_only, REPORT, log
    )

    _run_check_fix(
        section,
        "Ensure chronyd service is enabled and running",
        "systemctl is-enabled chronyd && systemctl is-active chronyd",
        "systemctl enable chronyd && systemctl start chronyd",
        verify_only, REPORT, log
    )

    # 2.3.2 Ensure chrony is configured (at least one NTP server defined)
    #    Check for "server" or "pool" directives in /etc/chrony.conf
    check_conf = (
        "grep -E '^(server|pool)\s+' /etc/chrony.conf | grep -q '[[:alnum:]]'"
    )
    fix_conf = (
        # If no server/pool lines found, append a known public pool
        "grep -E '^(server|pool)\\s+' /etc/chrony.conf || "
        "(echo 'pool 2.centos.pool.ntp.org iburst' >> /etc/chrony.conf && systemctl restart chronyd)"
    )
    _run_check_fix(
        section,
        "Ensure chrony has at least one NTP server configured",
        check_conf,
        fix_conf,
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
