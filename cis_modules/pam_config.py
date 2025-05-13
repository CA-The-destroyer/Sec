# cis_modules/pam_config.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.3 PAM Config"
    conf = "/etc/security/pwquality.conf"
    pam  = "/etc/pam.d/system-auth"

    # === ORIGINAL IMPLEMENTATION ===
    _run_check_fix(section, "Ensure pam_pwquality minclass=4",
                   f"grep -E '^\\s*minclass\\s*=\\s*4' {conf}",
                   f"echo 'minclass = 4' >> {conf}",
                   verify_only, REPORT, log)
    _run_check_fix(section, "Ensure pam_pwquality minlen=14",
                   f"grep -E '^\\s*minlen\\s*=\\s*14' {conf}",
                   f"echo 'minlen = 14' >> {conf}",
                   verify_only, REPORT, log)
    for opt,val in [("dcredit","-1"),("ucredit","-1"),("lcredit","-1"),("ocredit","-1")]:
        _run_check_fix(section, f"Ensure pam_pwquality {opt}={val}",
                       f"grep -E '^\\s*{opt}\\s*=\\s*{val}' {conf}",
                       f"echo '{opt} = {val}' >> {conf}",
                       verify_only, REPORT, log)
    _run_check_fix(section, "Ensure pam_pwquality enforce_for_root",
                   f"grep -E '^\\s*enforce_for_root' {conf}",
                   f"echo 'enforce_for_root' >> {conf}",
                   verify_only, REPORT, log)
    _run_check_fix(section, "Ensure pam_pwhistory remember=5",
                   f"grep -E '^\\s*remember\\s*=\\s*5' {conf}",
                   f"echo 'remember = 5' >> {conf}",
                   verify_only, REPORT, log)
    _run_check_fix(section, "Ensure pam_unix no nullok",
                   f"grep -E 'pam_unix.*nullok' {pam}",
                   f"sed -i 's/ nullok//g' {pam}",
                   verify_only, REPORT, log)

    # === UPDATED IMPLEMENTATION ===
    _run_check_fix(section, "Ensure pam_pwquality minclass=4 (idempotent)",
                   f"grep -E '^\\s*minclass\\s*=\\s*4' {conf}",
                   f"sed -i '/^\\s*minclass\\s*=/d' {conf} && echo 'minclass = 4' >> {conf}",
                   verify_only, REPORT, log)
    _run_check_fix(section, "Ensure pam_pwquality minlen=14 (idempotent)",
                   f"grep -E '^\\s*minlen\\s*=\\s*14' {conf}",
                   f"sed -i '/^\\s*minlen\\s*=/d' {conf} && echo 'minlen = 14' >> {conf}",
                   verify_only, REPORT, log)
    for opt,val in [("dcredit","-1"),("ucredit","-1"),("lcredit","-1"),("ocredit","-1")]:
        _run_check_fix(section, f"Ensure pam_pwquality {opt}={val} (idempotent)",
                       f"grep -E '^\\s*{opt}\\s*=\\s*{val}' {conf}",
                       f"sed -i '/^\\s*{opt}\\s*=/d' {conf} && echo '{opt} = {val}' >> {conf}",
                       verify_only, REPORT, log)
    _run_check_fix(section, "Ensure pam_pwquality enforce_for_root (idempotent)",
                   f"grep -E '^\\s*enforce_for_root' {conf}",
                   f"sed -i '/^\\s*enforce_for_root/d' {conf} && echo 'enforce_for_root' >> {conf}",
                   verify_only, REPORT, log)
    _run_check_fix(section, "Ensure pam_pwhistory remember=5 (idempotent)",
                   f"grep -E '^\\s*remember\\s*=\\s*5' {conf}",
                   f"sed -i '/^\\s*remember\\s*=/d' {conf} && echo 'remember = 5' >> {conf}",
                   verify_only, REPORT, log)
    _run_check_fix(section, "Ensure pam_unix no nullok (idempotent)",
                   f"grep -E 'pam_unix.*nullok' {pam}",
                   f"sed -i 's/ nullok//g' {pam}",
                   verify_only, REPORT, log)
