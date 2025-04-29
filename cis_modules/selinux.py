# cis_modules/filesystem.py
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.3 SELinux"
    checks = [
        ("Ensure SELinux is installed","rpm -q selinux-policy-targeted"),
        ("Ensure SELinux mode is enforcing","getenforce | grep -i Enforcing"),
        ("Ensure SELinux not disabled in bootloader","grep -E '(^GRUB_CMDLINE_LINUX=.*selinux=0)' /etc/default/grub || true")
    ]
    for desc, check in checks:
        fix = None if "not disabled" in desc else "setenforce 1" if "enforcing" in desc else None
        _run_check_fix(section, desc, check, fix, verify_only, REPORT, log)
