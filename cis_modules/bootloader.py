# cis_modules/bootloader.py

from cis_modules import _run_check_fix
import subprocess

def run_section(verify_only, REPORT, log):
    section = "1.4 Bootloader"

    # 1.4.1 Ensure bootloader password is set
    _run_check_fix(
        section,
        "Ensure GRUB2 bootloader password is set",
        "grep -E '^GRUB2_PASSWORD=' /etc/default/grub",
        "grub2-setpassword --password 'YourSecurePass' && grub2-mkconfig -o /boot/grub2/grub.cfg",
        verify_only, REPORT, log
    )
