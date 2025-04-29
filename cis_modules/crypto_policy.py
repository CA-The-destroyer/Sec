# cis_modules/filesystem.py
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.6 Crypto Policy"
    checks = [
        ("Ensure system crypto policy is not set to legacy","update-crypto-policies --show | grep -vq legacy"),
        ("Ensure SSH uses FIPS-approved ciphers","grep -E '^Ciphers .*aes256-ctr' /etc/ssh/sshd_config")
    ]
    for desc, check in checks:
        _run_check_fix(section, desc, check, None, verify_only, REPORT, log)
