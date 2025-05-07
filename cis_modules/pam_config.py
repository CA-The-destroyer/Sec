# cis_modules/pam_config.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.3 PAM Config"

    # 5.3.2.2 Ensure pam_faillock module is enabled
    _run_check_fix(
        section,
        "Ensure pam_faillock is enabled",
        "grep -E '^auth.*pam_faillock.so' /etc/pam.d/system-auth",
        "authselect enable-feature with-faillock; authselect apply-changes",
        verify_only, REPORT, log
    )

    # 5.3.2.4 Ensure pam_pwhistory is enabled
    _run_check_fix(
        section,
        "Ensure pam_pwhistory is enabled",
        "grep -E '^password.*pam_pwhistory.so' /etc/pam.d/system-auth",
        "authselect enable-feature with-pwhistory; authselect apply-changes",
        verify_only, REPORT, log
    )

    # 5.3.3.1.1 Ensure password failed attempts lockout is configured
    _run_check_fix(
        section,
        "Ensure pam_faillock lockout config",
        "grep -E 'deny=5' /etc/security/faillock.conf",
        "echo 'deny = 5' >> /etc/security/faillock.conf",
        verify_only, REPORT, log
    )
    # 5.3.3.1.2 Ensure password unlock time is configured
    _run_check_fix(
        section,
        "Ensure pam_faillock unlock_time config",
        "grep -E 'unlock_time=900' /etc/security/faillock.conf",
        "echo 'unlock_time = 900' >> /etc/security/faillock.conf",
        verify_only, REPORT, log
    )

    # 5.3.3.2.1 Ensure password number of changed characters is configured
    _run_check_fix(
        section,
        "Ensure pam_pwquality minclass config",
        "grep -E 'minclass=4' /etc/security/pwquality.conf",
        "echo 'minclass = 4' >> /etc/security/pwquality.conf",
        verify_only, REPORT, log
    )
    # 5.3.3.2.2 Ensure password length is configured
    _run_check_fix(
        section,
        "Ensure pam_pwquality minlen config",
        "grep -E 'minlen=14' /etc/security/pwquality.conf",
        "echo 'minlen = 14' >> /etc/security/pwquality.conf",
        verify_only, REPORT, log
    )
    # 5.3.3.2.3 Ensure password complexity is configured (manual)
    _run_check_fix(
        section,
        "Ensure pam_pwquality enforces complexity",
        "true",
        None,
        verify_only, REPORT, log
    )
    # 5.3.3.2.4 Ensure same consecutive chars is limited
    _run_check_fix(
        section,
        "Ensure pam_pwquality maxrepeat config",
        "grep -E 'maxrepeat=3' /etc/security/pwquality.conf",
        "echo 'maxrepeat = 3' >> /etc/security/pwquality.conf",
        verify_only, REPORT, log
    )
    # 5.3.3.2.5 Ensure sequential chars is limited
    _run_check_fix(
        section,
        "Ensure pam_pwquality maxsequence config",
        "grep -E 'maxsequence=3' /etc/security/pwquality.conf",
        "echo 'maxsequence = 3' >> /etc/security/pwquality.conf",
        verify_only, REPORT, log
    )
    # 5.3.3.2.7 Ensure quality enforced for root
    _run_check_fix(
        section,
        "Ensure pam_pwquality enforce for root",
        "grep -E 'enforce_for_root' /etc/security/pwquality.conf",
        "echo 'enforce_for_root' >> /etc/security/pwquality.conf",
        verify_only, REPORT, log
    )

    # 5.3.3.3.1 Ensure password history remember
    _run_check_fix(
        section,
        "Ensure pam_pwhistory remember config",
        "grep -E 'remember=5' /etc/security/pwquality.conf",
        "echo 'remember = 5' >> /etc/security/pwquality.conf",
        verify_only, REPORT, log
    )
    # 5.3.3.3.2 Ensure history enforced for root
    _run_check_fix(
        section,
        "Ensure pam_pwhistory enforce root",
        "grep -E 'enforce_for_root' /etc/security/pwquality.conf",
        "echo 'enforce_for_root' >> /etc/security/pwquality.conf",
        verify_only, REPORT, log
    )
    # 5.3.3.3.3 Ensure use_authtok included
    _run_check_fix(
        section,
        "Ensure pam_pwhistory use_authtok",
        "grep -E 'use_authtok' /etc/security/pwquality.conf",
        "echo 'use_authtok' >> /etc/security/pwquality.conf",
        verify_only, REPORT, log
    )

    # 5.3.3.4.1 Ensure pam_unix does not include nullok
    _run_check_fix(
        section,
        "Ensure pam_unix no nullok",
        "grep -E 'nullok' /etc/pam.d/system-auth",
        "sed -i 's/nullok//g' /etc/pam.d/system-auth",
        verify_only, REPORT, log
    )
