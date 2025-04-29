# cis_modules/filesystem.py
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.5-5 SSH & PAM"
    checks = [
        ("Ensure address space layout randomization is enabled","sysctl kernel.randomize_va_space | grep -q '1'"),
        ("Ensure core dumps are disabled","sysctl fs.suid_dumpable | grep -q '0'"),
        ("Ensure PermitRootLogin is disabled","grep -E '^PermitRootLogin no' /etc/ssh/sshd_config")
    ]
    fixes = {
        "Ensure address space layout randomization is enabled":"sysctl -w kernel.randomize_va_space=1",
        "Ensure core dumps are disabled":"sysctl -w fs.suid_dumpable=0",
        "Ensure PermitRootLogin is disabled":"sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && systemctl reload sshd"
    }
    for desc, check in checks:
        fix = fixes.get(desc)
        _run_check_fix(section, desc, check, fix, verify_only, REPORT, log)
