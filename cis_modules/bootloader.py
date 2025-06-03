# cis_modules/bootloader.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.4 Bootloader"

    # 1.4.1 Ensure bootloader password is set
    _run_check_fix(
        section,
        "Ensure bootloader password is set",
        "grep -q '^password_pbkdf2 ' /boot/grub2/user.cfg",
        None,  # manual: setting a GRUB2 password requires running `grub2-setpassword` interactively
        verify_only, REPORT, log
    )

    # 1.4.2 Ensure access to GRUB config is restricted
    _run_check_fix(
        section,
        "Ensure access to GRUB configuration is restricted (600, root:root)",
        "stat -c '%a %U:%G' /boot/grub2/grub.cfg | grep -q '^600 root:root$'",
        "chmod 600 /boot/grub2/grub.cfg && chown root:root /boot/grub2/grub.cfg",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
