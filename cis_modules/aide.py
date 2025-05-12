# cis_modules/aide.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "6.1 AIDE"

    # 6.1.2 Ensure AIDE cron job exists
    _run_check_fix(
        section,
        "Ensure AIDE cron job exists",
        "grep -q '/usr/sbin/aide --check' /etc/cron.d/aide",
        "sed -i '/\\/usr\\/sbin\\/aide --check/d' /etc/cron.d/aide && echo '0 5 * * * root /usr/sbin/aide --check' > /etc/cron.d/aide && chmod 600 /etc/cron.d/aide",
        verify_only, REPORT, log
    )

    # 6.1.3 Ensure /usr/sbin/aide is immutable
    _run_check_fix(
        section,
        "Ensure /usr/sbin/aide is immutable",
        "lsattr /usr/sbin/aide | grep -q 'i'",
        "chattr +i /usr/sbin/aide",
        verify_only, REPORT, log
    )
