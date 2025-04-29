# cis_modules/filesystem.py
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.4 Bootloader"
    checks = [
        ("Ensure bootloader password is set","grep -q '^password_pbkdf2 ' /boot/grub2/user.cfg"),
        ("Ensure access to GRUB config is restricted","stat -c '%a' /boot/grub2/grub.cfg | grep -q '600'; stat -c '%U:%G' /boot/grub2/grub.cfg | grep -q 'root:root'")
    ]
    fixes = {
        "Ensure access to GRUB config is restricted":"chmod 600 /boot/grub2/grub.cfg && chown root:root /boot/grub2/grub.cfg"
    }
    for desc, check in checks:
        fix = fixes.get(desc)
        _run_check_fix(section, desc, check, fix, verify_only, REPORT, log)
