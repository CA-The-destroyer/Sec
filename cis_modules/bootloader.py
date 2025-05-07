# cis_modules/bootloader.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.4 Bootloader"

    # 1.4.1 Ensure bootloader password is set
    _run_check_fix(
        section,
        "Ensure bootloader password is set",
        "grep -q '^password_pbkdf2 ' /boot/grub2/user.cfg",
        "grub2-setpassword",
        verify_only, REPORT, log
    )
