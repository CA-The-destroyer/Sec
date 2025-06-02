# cis_modules/pam_config.py

from cis_modules import _run_check_fix

PAM_SYSTEM_AUTH   = "/etc/pam.d/system-auth"
PAM_PASSWORD_AUTH = "/etc/pam.d/password-auth"

def run_section(verify_only, REPORT, log):
    section = "5.3 Configure PAM Arguments"

    # --- 0) Citrix FAS / SSSD forward_pass first ---
    _run_check_fix(
        section,
        "Insert pam_sss.so forward_pass for FAS-enabled VDA",
        f"grep -E '^auth\\s+sufficient\\s+pam_sss\\.so forward_pass' {PAM_SYSTEM_AUTH}",
        (
            # Insert at top of system-auth
            f"sed -i.bak -E '1 i auth sufficient pam_sss.so forward_pass' {PAM_SYSTEM_AUTH}"
        ),
        verify_only, REPORT, log
    )

    # --- 1) pam_faillock preauth/authfail only after SSSD ---
    _run_check_fix(
        section,
        "Enable pam_faillock preauth (post-SSSD)",
        f"grep -E '^auth\\s+required\\s+pam_faillock.so preauth' {PAM_SYSTEM_AUTH}",
        (
            f"sed -i.bak -E '/^auth\\s+sufficient\\s+pam_sss\\.so\\s+forward_pass/ a "
            f"auth required pam_faillock.so preauth silent audit deny=5 unlock_time=900' {PAM_SYSTEM_AUTH}"
        ),
        verify_only, REPORT, log
    )
    _run_check_fix(
        section,
        "Enable pam_faillock authfail (post-SSSD)",
        f"grep -E '^auth\\[default=die\\]\\s+pam_faillock.so authfail' {PAM_SYSTEM_AUTH}",
        (
            f"sed -i.bak -E '/^auth\\s+required\\s+pam_faillock.so preauth/ a "
            f"auth [default=die] pam_faillock.so authfail audit deny=5 unlock_time=900' {PAM_SYSTEM_AUTH}"
        ),
        verify_only, REPORT, log
    )

    # --- 2) pam_pwquality & pam_pwhistory only for UID >=1000 (real users) ---
    # Insert a UID check before pwquality
    _run_check_fix(
        section,
        "Scope pam_pwquality to real users",
        f"grep -E 'pam_succeed_if.so uid >= 1000' {PAM_PASSWORD_AUTH}",
        (
            f"sed -i.bak -E '/^password\\s+requisite\\s+pam_pwquality.so/ i "
            f"auth [success=1 default=ignore] pam_succeed_if.so uid >= 1000 quiet' {PAM_PASSWORD_AUTH}"
        ),
        verify_only, REPORT, log
    )
    # Enforce pwquality parameters
    _run_check_fix(
        section,
        "Ensure pam_pwquality retry=3 minlen=14",
        f"grep -E 'password\\s+requisite\\s+pam_pwquality.so.*retry=3.*minlen=14' {PAM_PASSWORD_AUTH}",
        (
            f"sed -i.bak -E 's/^password\\s+requisite\\s+pam_pwquality.so.*/"
            f"password requisite pam_pwquality.so retry=3 minlen=14 dcredit=-1 ucredit=-1 ocredit=-1 lcredit=-1/' {PAM_PASSWORD_AUTH}"
        ),
        verify_only, REPORT, log
    )
    # Scope pam_pwhistory similarly
    _run_check_fix(
        section,
        "Scope pam_pwhistory to real users",
        f"grep -E 'pam_pwhistory.so.*remember=5' {PAM_PASSWORD_AUTH}",
        (
            f"sed -i.bak -E '/^password\\s+requisite\\s+pam_pwquality.so/ a "
            f"password required pam_pwhistory.so use_authtok remember=5' {PAM_PASSWORD_AUTH}"
        ),
        verify_only, REPORT, log
    )

    # --- 3) Remove nullok from pam_unix ---
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
