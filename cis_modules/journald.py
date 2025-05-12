# cis_modules/journald.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "6.2 Journald"

    # 6.2.2.1.1 Ensure systemd-journal-remote is installed
    _run_check_fix(
        section,
        "Ensure systemd-journal-remote is installed",
        "rpm -q systemd-journal-remote",
        "yum install -y systemd-journal-remote",
        verify_only, REPORT, log
    )

    # 6.2.2.1.3 Ensure systemd-journal-upload is enabled and active
    _run_check_fix(
        section,
        "Ensure systemd-journal-upload is enabled and active",
        "systemctl is-enabled --quiet systemd-journal-upload && systemctl is-active --quiet systemd-journal-upload",
        "systemctl enable --now systemd-journal-upload",
        verify_only, REPORT, log
    )

    # 6.2.2.2 Ensure journald ForwardToSyslog is disabled
    _run_check_fix(
        section,
        "Ensure journald ForwardToSyslog is disabled",
        "grep -E '^\\s*ForwardToSyslog=no' /etc/systemd/journald.conf",
        "sed -i '/^\\s*ForwardToSyslog\\s*=\\s*/d' /etc/systemd/journald.conf && echo 'ForwardToSyslog=no' >> /etc/systemd/journald.conf && systemctl restart systemd-journald",
        verify_only, REPORT, log
    )

    # 6.2.2.3 Ensure journald Compress is configured
    _run_check_fix(
        section,
        "Ensure journald Compress is configured",
        "grep -E '^\\s*Compress=yes' /etc/systemd/journald.conf",
        "sed -i '/^\\s*Compress\\s*=\\s*/d' /etc/systemd/journald.conf && echo 'Compress=yes' >> /etc/systemd/journald.conf && systemctl restart systemd-journald",
        verify_only, REPORT, log
    )

    # 6.2.3.3 Ensure journald sends to rsyslog
    _run_check_fix(
        section,
        "Ensure journald ForwardToSyslog=yes",
        "grep -E '^\\s*ForwardToSyslog=yes' /etc/systemd/journald.conf",
        "sed -i '/^\\s*ForwardToSyslog\\s*=\\s*/d' /etc/systemd/journald.conf && echo 'ForwardToSyslog=yes' >> /etc/systemd/journald.conf && systemctl restart systemd-journald",
        verify_only, REPORT, log
    )
