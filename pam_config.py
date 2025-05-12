# Updated cis_modules/pam_config.py with idempotent edits

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.3 PAM Config"

    conf = "/etc/security/pwquality.conf"

    # 5.3.3.2.1 Ensure password number of changed characters is configured (minclass = 4)
    _run_check_fix(
        section,
        "Ensure pam_pwquality minclass=4",
        f"grep -E '^\\s*minclass\\s*=\\s*4' {conf}",
        f"sed -i '/^\\s*minclass\\s*=/d' {conf} && echo 'minclass = 4' >> {conf}",
        verify_only, REPORT, log
    )

    # 5.3.3.2.2 Ensure password length is configured (minlen = 14)
    _run_check_fix(
        section,
        "Ensure pam_pwquality minlen=14",
        f"grep -E '^\\s*minlen\\s*=\\s*14' {conf}",
        f"sed -i '/^\\s*minlen\\s*=/d' {conf} && echo 'minlen = 14' >> {conf}",
        verify_only, REPORT, log
    )

    # 5.3.3.2.3 Ensure password complexity is configured (dcredit, ucredit, lcredit, ocredit)
    for opt, val in [("dcredit","-1"), ("ucredit","-1"), ("lcredit","-1"), ("ocredit","-1")]:
        _run_check_fix(
            section,
            f"Ensure pam_pwquality {opt}={val}",
            f"grep -E '^\\s*{opt}\\s*=\\s*{val}' {conf}",
            f"sed -i '/^\\s*{opt}\\s*=/d' {conf} && echo '{opt} = {val}' >> {conf}",
            verify_only, REPORT, log
        )

    # 5.3.3.2.7 Ensure quality enforced for root (enforce_for_root)
    _run_check_fix(
        section,
        "Ensure pam_pwquality enforce_for_root",
        f"grep -E '^\\s*enforce_for_root' {conf}",
        f"sed -i '/^\\s*enforce_for_root/d' {conf} && echo 'enforce_for_root' >> {conf}",
        verify_only, REPORT, log
    )

    # 5.3.3.3.1 Ensure password history remember is configured (remember = 5)
    _run_check_fix(
        section,
        "Ensure pam_pwhistory remember=5",
        f"grep -E '^\\s*remember\\s*=\\s*5' {conf}",
        f"sed -i '/^\\s*remember\\s*=/d' {conf} && echo 'remember = 5' >> {conf}",
        verify_only, REPORT, log
    )

    # 5.3.3.3.2 Ensure history enforced for root (enforce_for_root covers both)
    # Already covered above

    # 5.3.3.4.1 Ensure pam_unix does not include nullok
    pam = "/etc/pam.d/system-auth"
    _run_check_fix(
        section,
        "Ensure pam_unix no nullok",
        f"grep -E 'pam_unix.*nullok' {pam}",
        f"sed -i 's/ nullok//g' {pam}",
        verify_only, REPORT, log
    )

    # 5.4.1.1 Ensure password expiration is configured (PASS_MAX_DAYS = 90)
    login_defs = "/etc/login.defs"
    _run_check_fix(
        section,
        "Ensure PASS_MAX_DAYS=90",
        "grep -E '^\\s*PASS_MAX_DAYS\\s+90' /etc/login.defs",
        "sed -i 's/^\\s*PASS_MAX_DAYS.*/PASS_MAX_DAYS   90/' /etc/login.defs",
        verify_only, REPORT, log
    )

    # 5.4.1.3 Ensure password expiration warning days is configured (PASS_WARN_AGE = 7)
    _run_check_fix(
        section,
        "Ensure PASS_WARN_AGE=7",
        "grep -E '^\\s*PASS_WARN_AGE\\s+7' /etc/login.defs",
        "sed -i 's/^\\s*PASS_WARN_AGE.*/PASS_WARN_AGE    7/' /etc/login.defs",
        verify_only, REPORT, log
    )

    # 5.4.1.5 Ensure inactive password lock is configured (INACTIVE = 30)
    useradd = "/etc/default/useradd"
    _run_check_fix(
        section,
        "Ensure INACTIVE=30",
        "grep -E '^\\s*INACTIVE\\s+30' /etc/default/useradd",
        "sed -i 's/^\\s*INACTIVE.*/INACTIVE     30/' /etc/default/useradd",
        verify_only, REPORT, log
    )
