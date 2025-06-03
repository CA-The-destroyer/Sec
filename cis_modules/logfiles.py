# cis_modules/logfiles.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "6.2 Configure Logfiles"

    # 6.2.4.1 Ensure access to all logfiles has been configured
    # We’ll ensure /var/log and its subdirectories are owned by root:root and not world-writable
    _run_check_fix(
        section,
        "Ensure ownership and permissions on /var/log/* are correct",
        "find /var/log -type f -exec stat -c '%U:%G %a %n' {} \\; | grep -Ev '^root:root (600|640|644) ' || true",
        "chown -R root:root /var/log && chmod -R 640 /var/log/* && chmod 750 /var/log",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
