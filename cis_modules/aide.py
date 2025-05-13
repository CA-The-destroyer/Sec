# cis_modules/aide.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "6.1 AIDE"

    # install & cron
    _run_check_fix(
        section,
        "Ensure AIDE is installed",
        "rpm -q aide",
        "dnf install -y aide",
        verify_only, REPORT, log
    )
    _run_check_fix(
        section,
        "Ensure AIDE cron job exists",
        "grep -q '/usr/sbin/aide --check' /etc/cron.d/aide",
        "echo '0 5 * * * root /usr/sbin/aide --check' > /etc/cron.d/aide && chmod 600 /etc/cron.d/aide",
        verify_only, REPORT, log
    )
    _run_check_fix(
        section,
        "Ensure /usr/sbin/aide is immutable",
        "lsattr /usr/sbin/aide | grep -q 'i'",
        "chattr +i /usr/sbin/aide",
        verify_only, REPORT, log
    )
