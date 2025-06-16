# cis_modules/auth_and_account_policies.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.2–5.4 PAM & Account Policies"

    # 5.2.7 Ensure access to the su command is restricted (pam_wheel)
    _run_check_fix(
        section,
        "Ensure 'su' is restricted to wheel group",
        "grep -Eq '^auth\\s+required\\s+pam_wheel\\.so' /etc/pam.d/su",
        "grep -Eq '^auth\\s+required\\s+pam_wheel\\.so' /etc/pam.d/su || "
        "echo 'auth required pam_wheel.so use_uid' >> /etc/pam.d/su",
        verify_only, REPORT, log
    )

    # 5.3.3.4.1 Ensure pam_unix does not include nullok
    _run_check_fix(
        section,
        "Ensure pam_unix.so does not include nullok",
        "! grep -E 'pam_unix\\.so.*nullok' /etc/pam.d/system-auth",
        "sed -i.bak -E 's@(pam_unix\\.so[^ ]*) nullok@\\1@' /etc/pam.d/system-auth",
        verify_only, REPORT, log
    )

    # 5.3.3.1.x Ensure pam_faillock is configured on preauth
    _run_check_fix(
        section,
        "Ensure pam_faillock.so preauth is configured",
        "grep -E '^auth \\[success=1 default=ignore\\] pam_succeed_if.so uid >= 1000' /etc/pam.d/system-auth",
        "sed -i.bak -E '/pam_faillock\\.so preauth/ i auth [success=1 default=ignore] pam_succeed_if.so uid >= 1000 quiet' /etc/pam.d/system-auth",
        verify_only, REPORT, log
    )

    # 5.3.3.1.x Ensure pam_faillock is configured on authfail
    _run_check_fix(
        section,
        "Ensure pam_faillock.so authfail is configured",
        "grep -E '^auth \\[success=1 default=ignore\\] pam_succeed_if.so uid >= 1000' /etc/pam.d/system-auth",
        "sed -i.bak -E '/pam_faillock\\.so authfail/ i auth [success=1 default=ignore] pam_succeed_if.so uid >= 1000 quiet' /etc/pam.d/system-auth",
        verify_only, REPORT, log
    )

    # 5.4.1.1 Ensure password expiration is configured (PASS_MAX_DAYS=90)
    _run_check_fix(
        section,
        "Ensure PASS_MAX_DAYS is 90",
        "grep -E '^PASS_MAX_DAYS\\s+90' /etc/login.defs",
        "sed -i.bak -E 's|^PASS_MAX_DAYS\\s+.*|PASS_MAX_DAYS   90|' /etc/login.defs",
        verify_only, REPORT, log
    )

    # 5.4.1.3 Ensure password expiration warning days is configured (PASS_WARN_AGE=7)
    _run_check_fix(
        section,
        "Ensure PASS_WARN_AGE is 7",
        "grep -E '^PASS_WARN_AGE\\s+7' /etc/login.defs",
        "sed -i.bak -E 's|^PASS_WARN_AGE\\s+.*|PASS_WARN_AGE   7|' /etc/login.defs",
        verify_only, REPORT, log
    )

    # 5.4.1.5 Ensure inactive password lock is configured (INACTIVE=30)
    _run_check_fix(
        section,
        "Ensure INACTIVE is 30",
        "grep -E '^INACTIVE\\s+30' /etc/default/useradd",
        "grep -q '^INACTIVE' /etc/default/useradd && "
        "sed -i.bak -E 's|^INACTIVE\\s+.*|INACTIVE   30|' /etc/default/useradd || "
        "echo 'INACTIVE   30' >> /etc/default/useradd",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
