# cis_modules/rsyslog.py

from cis_modules import _run_check_fix

RSYSLOG_CONF = "/etc/rsyslog.conf"


def run_section(verify_only, REPORT, log):
    section = "6.2 System Logging (rsyslog)"

    # 6.2.3.1 Ensure rsyslog is installed
    _run_check_fix(
        section,
        "Ensure rsyslog package is installed",
        "rpm -q rsyslog",
        "dnf -y install rsyslog",
        verify_only, REPORT, log
    )

    # 6.2.3.3 Ensure journald is configured to send logs to rsyslog
    _run_check_fix(
        section,
        "Ensure journald forwards logs to rsyslog",
        "grep -E '^ForwardToSyslog=yes' /etc/systemd/journald.conf",
        "sed -i.bak -E 's/^#?ForwardToSyslog=.*/ForwardToSyslog=yes/' /etc/systemd/journald.conf && systemctl restart systemd-journald",
        verify_only, REPORT, log
    )

    # 6.2.3.5 Ensure rsyslog logging is configured
    _run_check_fix(
        section,
        "Ensure rsyslog internal logging level is set",
        "grep -E '^\$ActionFileDefaultTemplate' {RSYSLOG_CONF}".format(RSYSLOG_CONF=RSYSLOG_CONF),
        "# No remediation: manual review required",
        verify_only, REPORT, log
    )

    # 6.2.3.6 Ensure rsyslog is configured to send logs to a remote log host
    _run_check_fix(
        section,
        "Ensure rsyslog sends logs to a remote host",
        "grep -E '^\*.*@@' {RSYSLOG_CONF}".format(RSYSLOG_CONF=RSYSLOG_CONF),
        "# No remediation: manual configuration required",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
