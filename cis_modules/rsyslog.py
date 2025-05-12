# cis_modules/rsyslog.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "6.2 Rsyslog"

    # 6.2.3.1 Ensure rsyslog is installed
    _run_check_fix(
        section,
        "Ensure rsyslog is installed",
        "rpm -q rsyslog",
        "yum install -y rsyslog",
        verify_only, REPORT, log
    )

    # 6.2.3.5 Ensure rsyslog logs to /var/log/messages
    _run_check_fix(
        section,
        "Ensure rsyslog logs to /var/log/messages",
        "grep -E '^\\*\\.\\*\\s+[^#].*/var/log/messages' /etc/rsyslog.conf",
        "sed -i '/\\*\\.\\*.*\\/var\\/log\\/messages/d' /etc/rsyslog.conf && echo '*.*   /var/log/messages' >> /etc/rsyslog.conf && systemctl restart rsyslog",
        verify_only, REPORT, log
    )

    # 6.2.3.6 Ensure rsyslog sends logs to a remote log host
    _run_check_fix(
        section,
        "Ensure rsyslog sends logs to a remote log host",
        "grep -E '^@@' /etc/rsyslog.conf",
        "sed -i '/@@/d' /etc/rsyslog.conf && echo '*.* @@loghost.example.com:514' >> /etc/rsyslog.conf && systemctl restart rsyslog",
        verify_only, REPORT, log
    )
