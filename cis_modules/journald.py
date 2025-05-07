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
        "Ensure systemd-journal-upload is enabled",
        "systemctl is-enabled --quiet systemd-journal-upload",
        "systemctl enable --now systemd-journal-upload",
        verify_only, REPORT, log
    )
    # 6.2.2.2 Ensure journald ForwardToSyslog is disabled
    _run_check_fix(
        section,
        "Ensure ForwardToSyslog=no in journald.conf",
        "grep -E 'ForwardToSyslog=no' /etc/systemd/journald.conf",
        "sed -i 's/^#ForwardToSyslog=.*/ForwardToSyslog=no/' /etc/systemd/journald.conf && systemctl restart systemd-journald",
        verify_only, REPORT, log
    )
    # 6.2.2.3 Ensure journald Compress is configured
    _run_check_fix(
        section,
        "Ensure Compress=yes in journald.conf",
        "grep -E 'Compress=yes' /etc/systemd/journald.conf",
        "sed -i 's/^#Compress=.*/Compress=yes/' /etc/systemd/journald.conf && systemctl restart systemd-journald",
        verify_only, REPORT, log
    )
    # 6.2.2.4 Ensure journald Storage is configured
    _run_check_fix(
        section,
        "Ensure Storage=persistent in journald.conf",
        "grep -E 'Storage=persistent' /etc/systemd/journald.conf",
        "sed -i 's/^#Storage=.*/Storage=persistent/' /etc/systemd/journald.conf && systemctl restart systemd-journald",
        verify_only, REPORT, log
    )
