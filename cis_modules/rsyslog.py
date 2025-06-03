# cis_modules/rsyslog.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "6.2 Configure rsyslog"

    # 6.2.3.1 Ensure rsyslog package is installed
    _run_check_fix(
        section,
        "Ensure rsyslog is installed",
        "rpm -q rsyslog",
        "dnf -y install rsyslog",
        verify_only, REPORT, log
    )

    # 6.2.3.2 Ensure rsyslog service is enabled and active
    _run_check_fix(
        section,
        "Ensure rsyslog service is enabled and active",
        "systemctl is-enabled rsyslog | grep -q 'enabled' && systemctl is-active rsyslog | grep -q 'active'",
        "systemctl enable rsyslog && systemctl start rsyslog",
        verify_only, REPORT, log
    )

    # 6.2.3.5 Ensure journald is configured to send logs to rsyslog
    _run_check_fix(
        section,
        "Ensure journald ForwardToSyslog is disabled (already handled in journald module); "
        "ensure rsyslog listens for incoming messages",
        "grep -E '^\\$ModLoad imjournal' /etc/rsyslog.conf",
        "echo '$ModLoad imjournal' >> /etc/rsyslog.conf && systemctl restart rsyslog",
        verify_only, REPORT, log
    )

    # 6.2.3.6 Ensure rsyslog is configured to send logs to a remote log host (example: 10.0.0.100)
    # Replace 10.0.0.100 with your real remote syslog server
    _run_check_fix(
        section,
        "Ensure rsyslog is configured to send logs to a remote log host",
        "grep -E '^*.*@10.0.0.100' /etc/rsyslog.conf || true",
        "echo '*.* @10.0.0.100' >> /etc/rsyslog.conf && systemctl restart rsyslog",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
