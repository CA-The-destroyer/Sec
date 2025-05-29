# cis_modules/aide.py

from cis_modules import _run_check_fix


def run_section(verify_only, REPORT, log):
    section = "6.1 Configure Integrity Checking"

    # 6.1.1 Ensure AIDE is installed
    _run_check_fix(
        section,
        "Ensure AIDE is installed",
        "rpm -q aide",
        "dnf -y install aide",
        verify_only, REPORT, log
    )

    # 6.1.2 Ensure filesystem integrity is regularly checked
    # Check for a cron or systemd timer for aide
    _run_check_fix(
        section,
        "Ensure AIDE integrity check is scheduled",
        "grep -E '^0 5 \* \* \* root /usr/sbin/aide --check' /etc/crontab",
        (
            "echo '0 5 * * * root /usr/sbin/aide --check' >> /etc/crontab"
        ),
        verify_only, REPORT, log
    )

    # 6.1.3 Ensure cryptographic mechanisms are used to protect the integrity of audit tools
    _run_check_fix(
        section,
        "Ensure AIDE uses cryptographic checksums",
        "grep -E '^Checksums *=.*sha512' /etc/aide.conf",
        (
            "sed -i.bak -E 's/^Checksums *=.*/Checksums = sha512/' /etc/aide.conf"
        ),
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
