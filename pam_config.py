# cis_modules/pam_config.py

from cis_modules import _run_check_fix

PAM_SYSTEM_AUTH   = "/etc/pam.d/system-auth"
PAM_PASSWORD_AUTH = "/etc/pam.d/password-auth"

def run_section(verify_only, REPORT, log):
    section = "5.3 Configure PAM Arguments"

    # 5.3.2.2 Ensure pam_faillock module is enabled (preauth)
    _run_check_fix(
        section,
        "Ensure pam_faillock is enabled (preauth)",
        f"grep -E '^auth\\s+required\\s+pam_faillock.so preauth' {PAM_SYSTEM_AUTH}",
        (
            # insert before pam_unix preauth
            f"sed -i.bak -E '/^auth\\s+required\\s+pam_unix\\.so/ i auth required pam_faillock.so preauth silent audit deny=5 unlock_time=900' {PAM_SYSTEM_AUTH}"
        ),
        verify_only, REPORT, log
    )

    # 5.3.2.2 Ensure pam_faillock module is enabled (authfail)
    _run_check_fix(
        section,
        "Ensure pam_faillock is enabled (authfail)",
        f"grep -E '^auth\\[default=die\\]\\s+pam_faillock.so authfail' {PAM_SYSTEM_AUTH}",
        (
            f"sed -i.bak -E '/^auth\\[default=die\\]/ i auth [default=die] pam_faillock.so authfail audit deny=5 unlock_time=900' {PAM_SYSTEM_AUTH}"
        ),
        verify_only, REPORT, log
    )

    # 5.3.2.4 Ensure pam_pwhistory module is enabled for interactive only
    # We wrap in: only for service in login or sshd
    _run_check_fix(
        section,
        "Ensure pam_pwhistory is enabled for interactive logins",
        f"grep -E 'password\\s+required\\s+pam_pwhistory.so use_authtok remember=5' {PAM_PASSWORD_AUTH}",
        (
            # add a conditional so only login and sshd hit this
            f"sed -i.bak -E '/^password\\s+requisite\\s+pam_pwquality.so/ a password [success=2 default=ignore] pam_succeed_if.so service in login sshd quiet_use_uid\\n"
            f"password requisite pam_pwhistory.so use_authtok remember=5' {PAM_PASSWORD_AUTH}"
        ),
        verify_only, REPORT, log
    )

    # 5.3.3.2.1 Ensure pam_pwquality parameters for interactive only
    _run_check_fix(
        section,
        "Ensure pam_pwquality retry=3 minlen=14 for interactive logins",
        f"grep -E 'password\\s+requisite\\s+pam_pwquality.so.*retry=3.*minlen=14' {PAM_PASSWORD_AUTH}",
        (
            # prepend a service filter, then enforce parameters
            f"sed -i.bak -E 's/^password\\s+requisite\\s+pam_pwquality.so.*/"
            f"password [success=1 default=ignore] pam_succeed_if.so service in login sshd quiet_use_uid\\n"
            f"password requisite pam_pwquality.so retry=3 minlen=14 dcredit=-1 ucredit=-1 ocredit=-1 lcredit=-1/' {PAM_PASSWORD_AUTH}"
        ),
        verify_only, REPORT, log
    )

    # 5.3.3.4.1 Ensure pam_unix does not include nullok
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
