# cis_modules/journald.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "6.2 Configure journald"

    # 6.2.2.1.3 Ensure systemd-journal-upload is installed, enabled, active
    _run_check_fix(
        section,
        "Ensure systemd-journal-upload is installed",
        "rpm -q systemd-journal-upload",
        "dnf -y install systemd-journal-upload",
        verify_only, REPORT, log
    )
    _run_check_fix(
        section,
        "Ensure systemd-journal-upload is enabled and active",
        "systemctl is-enabled systemd-journal-upload | grep -q 'enabled' && systemctl is-active systemd-journal-upload | grep -q 'active'",
        "systemctl enable systemd-journal-upload && systemctl start systemd-journal-upload",
        verify_only, REPORT, log
    )

    # 6.2.2.2 Ensure journald ForwardToSyslog is disabled
    _run_check_fix(
        section,
        "Ensure journald ForwardToSyslog is disabled",
        "grep -E '^ForwardToSyslog=no' /etc/systemd/journald.conf",
        "sed -i.bak -E 's/^#?ForwardToSyslog=.*/ForwardToSyslog=no/' /etc/systemd/journald.conf && systemctl restart systemd-journald",
        verify_only, REPORT, log
    )

    # 6.2.2.3 Ensure journald Compress is configured
    _run_check_fix(
        section,
        "Ensure journald Compress is configured",
        "grep -E '^Compress=yes' /etc/systemd/journald.conf",
        "sed -i.bak -E 's/^#?Compress=.*/Compress=yes/' /etc/systemd/journald.conf && systemctl restart systemd-journald",
        verify_only, REPORT, log
    )

    # 6.2.2.4 Ensure journald Storage is configured (persistent)
    _run_check_fix(
        section,
        "Ensure journald Storage is persistent",
        "grep -E '^Storage=persistent' /etc/systemd/journald.conf",
        "sed -i.bak -E 's/^#?Storage=.*/Storage=persistent/' /etc/systemd/journald.conf && systemctl restart systemd-journald",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
