# cis_modules/pam_config.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.3 PAM Config"
    conf = "/etc/security/pwquality.conf"
    pam = "/etc/pam.d/system-auth"

    

    # 5.3.3.2.1 Ensure pam_pwquality minclass=4 (idempotent)
    _run_check_fix(
        section,
        "Ensure pam_pwquality minclass=4",
        f"grep -E '^\\s*minclass\\s*=\\s*4' {conf}",
        f"sed -i '/^\\s*minclass\\s*=/d' {conf} && echo 'minclass = 4' >> {conf}",
        verify_only, REPORT, log
    )

    # 5.3.3.2.2 Ensure pam_pwquality minlen=14 (idempotent)
    _run_check_fix(
        section,
        "Ensure pam_pwquality minlen=14",
        f"grep -E '^\\s*minlen\\s*=\\s*14' {conf}",
        f"sed -i '/^\\s*minlen\\s*=/d' {conf} && echo 'minlen = 14' >> {conf}",
        verify_only, REPORT, log
    )

    # 5.3.3.2.3 Ensure password complexity credits (idempotent)
    for opt, val in [("dcredit","-1"), ("ucredit","-1"), ("lcredit","-1"), ("ocredit","-1")]:
        _run_check_fix(
            section,
            f"Ensure pam_pwquality {opt}={val}",
            f"grep -E '^\\s*{opt}\\s*=\\s*{val}' {conf}",
            f"sed -i '/^\\s*{opt}\\s*=/d' {conf} && echo '{opt} = {val}' >> {conf}",
            verify_only, REPORT, log
        )

    # 5.3.3.2.7 Ensure pam_pwquality enforce_for_root (idempotent)
    _run_check_fix(
        section,
        "Ensure pam_pwquality enforce_for_root",
        f"grep -E '^\\s*enforce_for_root' {conf}",
        f"sed -i '/^\\s*enforce_for_root/d' {conf} && echo 'enforce_for_root' >> {conf}",
        verify_only, REPORT, log
    )

    # 5.3.3.3.1 Ensure pam_pwhistory remember=5 (idempotent)
    _run_check_fix(
        section,
        "Ensure pam_pwhistory remember=5",
        f"grep -E '^\\s*remember\\s*=\\s*5' {conf}",
        f"sed -i '/^\\s*remember\\s*=/d' {conf} && echo 'remember = 5' >> {conf}",
        verify_only, REPORT, log
    )

    # 5.3.3.4.1 Ensure pam_unix does not include nullok (idempotent)
    _run_check_fix(
        section,
        "Ensure pam_unix does not include nullok",
        f"grep -E 'pam_unix.*nullok' {pam}",
        f"sed -i 's/ nullok//g' {pam}",
        verify_only, REPORT, log
    )
