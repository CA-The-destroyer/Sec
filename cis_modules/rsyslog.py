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
    # 6.2.3.6 Ensure rsyslog is configured to send logs to a remote host
    _run_check_fix(
        section,
        "Ensure remote log host configured",
        "grep -E '@@' /etc/rsyslog.conf",
        "echo '*.* @@loghost.example.com:514' >> /etc/rsyslog.conf && systemctl restart rsyslog",
        verify_only, REPORT, log
    )
