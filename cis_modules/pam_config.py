# cis_modules/pam_config.py

from cis_modules import _run_check_fix

PAM_SYSTEM_AUTH = "/etc/pam.d/system-auth"
PAM_PASSWORD_AUTH = "/etc/pam.d/password-auth"


def run_section(verify_only, REPORT, log):
    section = "5.3 Configure PAM Arguments"

    # 5.3.2.2 Ensure pam_faillock module is enabled
    _run_check_fix(
        section,
        "Ensure pam_faillock is enabled in authfail",
        f"grep -E '^auth\s+required\s+pam_faillock.so' {PAM_SYSTEM_AUTH}",
        (
            f"sed -i.bak -E '/^auth\s+required\s+pam_unix.so/ i auth required pam_faillock.so preauth silent audit deny=5 unlock_time=900' {PAM_SYSTEM_AUTH} && "
            f"sed -i -E '/^auth\s+\[default=die\]/ i auth \[default=die\] pam_faillock.so authfail audit deny=5 unlock_time=900' {PAM_SYSTEM_AUTH}
        ),
        verify_only, REPORT, log
    )

    # 5.3.2.4 Ensure pam_pwhistory module is enabled
    _run_check_fix(
        section,
        "Ensure pam_pwhistory is enabled",
        f"grep -E '^password\s+required\s+pam_pwhistory.so' {PAM_SYSTEM_AUTH}",
        (
            f"sed -i.bak -E '/^password\s+requisite\s+pam_pwquality.so/ a password required pam_pwhistory.so use_authtok remember=5' {PAM_SYSTEM_AUTH}"
        ),
        verify_only, REPORT, log
    )

    # 5.3.3.2.1 Ensure password number of changed characters is configured
    _run_check_fix(
        section,
        "Ensure pam_pwquality retry=<3> minlen=<14>",
        f"grep -E 'pam_pwquality.so.*retry=3' {PAM_PASSWORD_AUTH} && grep -E 'pam_pwquality.so.*minlen=14' {PAM_PASSWORD_AUTH}",
        (
            f"sed -i.bak -E 's/pam_pwquality.so.*/pam_pwquality.so retry=3 minlen=14 dcredit=-1 ucredit=-1 ocredit=-1 lcredit=-1/' {PAM_PASSWORD_AUTH}"
        ),
        verify_only, REPORT, log
    )

    # 5.3.3.4.1 Ensure pam_unix does not include nullok
    _run_check_fix(
        section,
        "Ensure pam_unix does not include nullok",
        f"grep -E '^password\s+requisite\s+pam_unix.so' {PAM_PASSWORD_AUTH} | grep -vq nullok",
        (
            f"sed -i.bak -E 's/(pam_unix.so.*)nullok/\1/' {PAM_PASSWORD_AUTH}"
        ),
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
