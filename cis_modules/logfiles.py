# cis_modules/logfiles.py

from cis_modules import _run_check_fix

LOGFILES_DIR = "/var/log"


def run_section(verify_only, REPORT, log):
    section = "6.2 System Logging (Logfiles)"

    # 6.2.4.1 Ensure access to all logfiles has been configured
    # Check for permissive permissions
    _run_check_fix(
        section,
        "Ensure log directory permissions are not more permissive than 750",
        f"stat -c '%a' {LOGFILES_DIR} | grep -E '^[0-7][0-4][0-0]$'",
        # Set directory to 750
        f"chmod 750 {LOGFILES_DIR}",
        verify_only, REPORT, log
    )

    # Ensure individual log files are not world writable
    _run_check_fix(
        section,
        "Ensure no log file is world-writable",
        f"find {LOGFILES_DIR} -type f -perm /o=w | grep -q ''",
        # Remove world write
        f"find {LOGFILES_DIR} -type f -perm /o=w -exec chmod o-w {{}} +",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
