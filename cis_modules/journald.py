# cis_modules/journald.py

from cis_modules import _run_check_fix

JOURNALD_CONF = "/etc/systemd/journald.conf"


def run_section(verify_only, REPORT, log):
    section = "6.2 System Logging (journald)"

    # 6.2.2.1.1 Ensure systemd-journal-remote is installed
    _run_check_fix(
        section,
        "Ensure systemd-journal-remote is installed",
        "rpm -q systemd-journal-remote",
        "dnf -y install systemd-journal-remote",
        verify_only, REPORT, log
    )

    # 6.2.2.1.3 Ensure systemd-journal-upload is enabled and active
    _run_check_fix(
        section,
        "Ensure systemd-journal-upload service is enabled and running",
        "systemctl is-enabled systemd-journal-upload && systemctl is-active systemd-journal-upload",
        "systemctl enable systemd-journal-upload && systemctl start systemd-journal-upload",
        verify_only, REPORT, log
    )

    # 6.2.2.2 Ensure journald ForwardToSyslog is disabled
    _run_check_fix(
        section,
        "Ensure journald ForwardToSyslog is disabled",
        f"grep -E '^ForwardToSyslog=no' {JOURNALD_CONF}",
        f"sed -i.bak -E 's/^#?ForwardToSyslog=.*/ForwardToSyslog=no/' {JOURNALD_CONF} && systemctl restart systemd-journald",
        verify_only, REPORT, log
    )

    # 6.2.2.3 Ensure journald Compress is configured
    _run_check_fix(
        section,
        "Ensure journald compression is enabled",
        f"grep -E '^Compress=yes' {JOURNALD_CONF}",
        f"sed -i.bak -E 's/^#?Compress=.*/Compress=yes/' {JOURNALD_CONF} && systemctl restart systemd-journald",
        verify_only, REPORT, log
    )

    # 6.2.2.4 Ensure journald Storage is configured
    _run_check_fix(
        section,
        "Ensure journald storage is persistent",
        f"grep -E '^Storage=persistent' {JOURNALD_CONF}",
        f"sed -i.bak -E 's/^#?Storage=.*/Storage=persistent/' {JOURNALD_CONF} && systemctl restart systemd-journald",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
