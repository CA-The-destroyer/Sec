# cis_modules/chrony.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.3 Time Sync"

    # 2.3.1 Ensure NTP is synchronized
    _run_check_fix(
        section,
        "Ensure NTP synchronized",
        "timedatectl show | grep -q 'NTPSynchronized=yes'",
        "timedatectl set-ntp yes",
        verify_only, REPORT, log
    )

    # 2.3.2 Ensure chrony is configured
    _run_check_fix(
        section,
        "Ensure chrony is installed",
        "rpm -q chrony",
        "yum install -y chrony",
        verify_only, REPORT, log
    )
    _run_check_fix(
        section,
        "Ensure chrony is running",
        "systemctl is-active --quiet chronyd",
        "systemctl enable --now chronyd",
        verify_only, REPORT, log
    )
