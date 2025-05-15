# cis_modules/chrony.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.3 Time Synchronization"

    # 1) Install chrony, enable & start, remove ntp
    _run_check_fix(
        section,
        "Ensure chrony is installed, enabled, running, and ntp is removed",
        # Pass only if chrony present + service on + service active + ntp absent
        "rpm -q chrony && systemctl is-enabled --quiet chronyd.service "
        "&& systemctl is-active --quiet chronyd.service && ! rpm -q ntp",
        # Otherwise install/start and remove
        "dnf install -y chrony && systemctl enable --now chronyd.service && dnf remove -y ntp",
        verify_only, REPORT, log
    )

    # 2) Ensure at least one NTP server is configured in /etc/chrony.conf
    _run_check_fix(
        section,
        "Ensure chrony.conf has at least one 'server' entry",
        "grep -E '^[[:space:]]*server[[:space:]]+' /etc/chrony.conf",
        # No real remediation can guess a server—just insert a common public pool
        "sed -i '/^#.*pool 2.rhel.pool.ntp.org/!a pool 2.rhel.pool.ntp.org iburst' /etc/chrony.conf && systemctl restart chronyd.service",
        verify_only, REPORT, log
    )
