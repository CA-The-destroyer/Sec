# cis_modules/pam_config.py

from cis_modules import _run_check_fix

PAM_SYSTEM_AUTH   = "/etc/pam.d/system-auth"
PAM_PASSWORD_AUTH = "/etc/pam.d/password-auth"

def run_section(verify_only, REPORT, log):
    section = "5.3 Configure PAM Arguments"

    # 0) Insert pam_sss.so forward_pass for FAS/SSSD before any lockout / quality checks
    _run_check_fix(
        section,
        "Insert pam_sss.so forward_pass for FAS-enabled VDA",
        f"grep -E '^auth\\s+sufficient\\s+pam_sss\\.so forward_pass' {PAM_SYSTEM_AUTH}",
        f"sed -i.bak -E '1 i auth sufficient pam_sss.so forward_pass' {PAM_SYSTEM_AUTH}",
        verify_only, REPORT, log
    )

    # 1) Scope pam_faillock preauth to non-root users
    _run_check_fix(
        section,
        "Scope pam_faillock preauth to non-root users",
        f"grep -E '^auth\\s+required\\s+pam_faillock\\.so preauth' {PAM_SYSTEM_AUTH}",
        (
            f"sed -i.bak -E '/^auth\\s+sufficient\\s+pam_sss\\.so forward_pass/ a "
            f"auth [success=1 default=ignore] pam_succeed_if.so uid >= 1 quiet' {PAM_SYSTEM_AUTH} && "
            f"sed -i -E '/^auth\\s+sufficient\\s+pam_sss\\.so forward_pass/ a "
            f"auth required pam_faillock.so preauth silent audit deny=5 unlock_time=900' {PAM_SYSTEM_AUTH}"
        ),
        verify_only, REPORT, log
    )

    # 2) Scope pam_faillock authfail to non-root users
    _run_check_fix(
        section,
        "Scope pam_faillock authfail to non-root users",
        f"grep -E '^auth\\[default=die\\]\\s+pam_faillock\\.so authfail' {PAM_SYSTEM_AUTH}",
        (
            f"sed -i.bak -E '/^auth     \\[success=1 default=ignore\\] pam_succeed_if.so uid >= 1 quiet/ a "
            f"auth [default=die] pam_faillock.so authfail audit deny=5 unlock_time=900' {PAM_SYSTEM_AUTH}"
        ),
        verify_only, REPORT, log
    )

    # 3) Scope pam_pwquality to real users (UID >= 1000)
    _run_check_fix(
        section,
        "Scope pam_pwquality to real users (UID >= 1000)",
        f"grep -E 'pam_succeed_if\\.so uid >= 1000' {PAM_PASSWORD_AUTH}",
        (
            f"sed -i.bak -E '/^password\\s+requisite\\s+pam_pwquality.so/ i "
            f"auth     [success=1 default=ignore] pam_succeed_if.so uid >= 1000 quiet' "
            f"{PAM_PASSWORD_AUTH}"
        ),
        verify_only, REPORT, log
    )
    _run_check_fix(
        section,
        "Ensure pam_pwquality retry=3 minlen=14",
        f"grep -E 'password\\s+requisite\\s+pam_pwquality.so.*retry=3.*minlen=14' {PAM_PASSWORD_AUTH}",
        (
            f"sed -i.bak -E 's/^password\\s+requisite\\s+pam_pwquality.so.*/"
            f"password requisite pam_pwquality.so retry=3 minlen=14 dcredit=-1 ucredit=-1 ocredit=-1 lcredit=-1/' "
            f"{PAM_PASSWORD_AUTH}"
        ),
        verify_only, REPORT, log
    )

    # 4) Scope pam_pwhistory to real users (UID >= 1000)
    _run_check_fix(
        section,
        "Scope pam_pwhistory to real users (UID >= 1000)",
        f"grep -E 'pam_pwhistory.so use_authtok remember=5' {PAM_PASSWORD_AUTH}",
        (
            f"sed -i.bak -E '/^password\\s+requisite\\s+pam_pwquality.so/ a "
            f"password required pam_pwhistory.so use_authtok remember=5' "
            f"{PAM_PASSWORD_AUTH}"
        ),
        verify_only, REPORT, log
    )

    # 5) Ensure pam_unix does not include nullok (only for real users)
    _run_check_fix(
        section,
        "Ensure pam_unix does not include nullok",
        f"grep -E '^password\\s+requisite\\s+pam_unix.so' {PAM_PASSWORD_AUTH} | grep -vq nullok",
        (
            f"sed -i.bak -E 's/(pam_unix.so.*)nullok/\\1/' {PAM_PASSWORD_AUTH}"
        ),
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
