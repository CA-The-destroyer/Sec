# cis_modules/pam_packages.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.3 PAM Packages"

    # 5.3.1.1 Ensure pam is installed
    _run_check_fix(
        section,
        "Ensure latest pam is installed",
        "rpm -q pam",
        "yum install -y pam",
        verify_only, REPORT, log
    )

    # 5.3.1.2 Ensure authselect is installed
    _run_check_fix(
        section,
        "Ensure authselect is installed",
        "rpm -q authselect",
        "yum install -y authselect",
        verify_only, REPORT, log
    )

    # 5.3.1.3 Ensure libpwquality is installed
    _run_check_fix(
        section,
        "Ensure libpwquality is installed",
        "rpm -q libpwquality",
        "yum install -y libpwquality",
        verify_only, REPORT, log
    )
