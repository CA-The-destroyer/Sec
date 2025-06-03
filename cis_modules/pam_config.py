# cis_modules/pam_config.py

from cis_modules import _run_check_fix
import fileinput
import re

def run_section(verify_only, REPORT, log):
    section = "5.3 Configure PAM Arguments"

    # 5.3.3.2.1 Ensure password number of changed characters is configured
    _run_check_fix(
        section,
        "Ensure password changed characters (difok) ≥ 4",
        "grep -E '^password\\s+requisite\\s+pam_pwquality\\.so.*difok=4' /etc/pam.d/system-auth",
        "sed -i.bak -r 's/^(password\\s+requisite\\s+pam_pwquality\\.so.*)/\\1 difok=4/' /etc/pam.d/system-auth",
        verify_only, REPORT, log
    )

    # 5.3.3.2.2 Ensure password length is configured (minlen=14)
    _run_check_fix(
        section,
        "Ensure password length (minlen) ≥ 14",
        "grep -E '^password\\s+requisite\\s+pam_pwquality\\.so.*minlen=14' /etc/pam.d/system-auth",
        "sed -i.bak -r 's/^(password\\s+requisite\\s+pam_pwquality\\.so.*)/\\1 minlen=14/' /etc/pam.d/system-auth",
        verify_only, REPORT, log
    )

    # 5.3.3.3.1 Ensure password history remember is configured (remember=5)
    _run_check_fix(
        section,
        "Ensure password history (remember) ≥ 5",
        "grep -E '^password\\s+requisite\\s+pam_pwquality\\.so.*remember=5' /etc/pam.d/system-auth",
        "sed -i.bak -r 's/^(password\\s+requisite\\s+pam_pwquality\\.so.*)/\\1 remember=5/' /etc/pam.d/system-auth",
        verify_only, REPORT, log
    )

    # 5.3.3.3.2 Ensure password history is enforced for root user
    _run_check_fix(
        section,
        "Ensure password history is enforced for root user",
        "grep -E '^password\\s+required\\s+pam_pwhistory\\.so.*use_authtok.*enforce_for_root' /etc/pam.d/password-auth",
        "sed -i.bak -r 's/^(password\\s+required\\s+pam_pwhistory\\.so.*)/\\1 enforce_for_root/' /etc/pam.d/password-auth",
        verify_only, REPORT, log
    )

    # 5.3.3.4.1 Ensure pam_unix does not include nullok
    _run_check_fix(
        section,
        "Ensure pam_unix does not include nullok",
        "grep -E '^password\\s+requisite\\s+pam_unix\\.so(?!.*nullok)' /etc/pam.d/system-auth",
        "sed -i.bak -r 's/^(password\\s+requisite\\s+pam_unix\\.so.*)nullok(.*)/\\1\\2/' /etc/pam.d/system-auth",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
