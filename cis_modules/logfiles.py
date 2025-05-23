# cis_modules/logfiles.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "6.2 File Access"

    # 6.2.4.1 Ensure all files in /var/log are mode 600
    _run_check_fix(
        section,
        "Ensure all files in /var/log are mode 600",
        "bash -c \"find /var/log -type f ! -perm 600 | grep -q . && exit 1 || exit 0\"",
        "find /var/log -type f ! -perm 600 -exec chmod 600 {} +",
        verify_only, REPORT, log
    )
