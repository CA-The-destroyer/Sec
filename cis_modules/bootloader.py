# cis_modules/bootloader.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.4 Bootloader"

    # 1.4.1 Ensure bootloader password is set
    check = "grep -q '^password_pbkdf2 ' /boot/grub2/user.cfg"
    # grub2-setpassword will interactively prompt; run only in enforcement mode
    fix   = "grub2-setpassword"
    _run_check_fix(
        section,
        "Ensure bootloader password is set",
        check,
        fix,
        verify_only,
        REPORT,
        log
    )
    
    # 1.4.2 Ensure access to GRUB config is restricted
    check2 = (
        "stat -c '%a' /boot/grub2/grub.cfg | grep -q '^600$' && "
        "stat -c '%U:%G' /boot/grub2/grub.cfg | grep -q '^root:root$'"
    )
    fix2 = "chmod 600 /boot/grub2/grub.cfg && chown root:root /boot/grub2/grub.cfg"
    _run_check_fix(
        section,
        "Ensure access to GRUB config is restricted",
        check2,
        fix2,
        verify_only,
        REPORT,
        log
    )
