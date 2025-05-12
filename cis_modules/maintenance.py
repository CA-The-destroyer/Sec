# cis_modules/maintenance.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "7.1 Maintenance"

    # 7.1.12 Ensure no files or directories without owner/group exist
    _run_check_fix(
        section,
        "Ensure no files or directories without owner/group exist",
        "bash -c \"find / -xdev \\( -nouser -o -nogroup \\) | grep -q . && exit 1 || exit 0\"",
        None,
        verify_only, REPORT, log
    )
