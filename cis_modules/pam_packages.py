# cis_modules/pam_packages.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.3 Configure PAM Software Packages"

    # 5.3.1.1 Ensure latest version of pam is installed
    _run_check_fix(
        section,
        "Ensure latest pam is installed",
        "rpm -q pam",
        "dnf -y install pam",
        verify_only, REPORT, log
    )

    # 5.3.1.2 Ensure latest version of authselect is installed
    _run_check_fix(
        section,
        "Ensure latest authselect is installed",
        "rpm -q authselect",
        "dnf -y install authselect",
        verify_only, REPORT, log
    )

    # 5.3.1.3 Ensure latest version of libpwquality is installed
    _run_check_fix(
        section,
        "Ensure latest libpwquality is installed",
        "rpm -q libpwquality",
        "dnf -y install libpwquality",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
