# cis_modules/bootloader.py

from cis_modules import _run_check_fix


def run_section(verify_only, REPORT, log):
    section = "1.4 Configure Bootloader"

    # 1.4.1 Ensure bootloader password is set
    # Check if GRUB password is configured
    _run_check_fix(
        section,
        "Ensure GRUB bootloader password is set",
        "grep -E '^set password_pbkdf2' /etc/grub.d/40_custom",
        (
            "echo 'set superusers=\"root\"' >> /etc/grub.d/40_custom && "
            "grub2-mkpasswd-pbkdf2 | awk '/^ *PBKDF2 hash of your password is/{print \"set password_pbkdf2 root \\"\" $NF "\"\" }' >> /etc/grub.d/40_custom && "
            "chmod +x /etc/grub.d/40_custom && "
            "grub2-mkconfig -o /etc/grub2.cfg"
        ),
        verify_only, REPORT, log
    )

    # 1.4.2 Ensure access to bootloader config is configured
    _run_check_fix(
        section,
        "Ensure unauthorized users cannot read bootloader configuration",
        "stat -c '%a' /etc/grub2.cfg | grep -q '^[0-6][0-6][0-6]$'",
        "chmod og-rwx /etc/grub2.cfg",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
