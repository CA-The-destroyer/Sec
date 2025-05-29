# cis_modules/filesystem.py

import subprocess
from cis_modules import _run_check_fix

# Helper to check if mount has option

def _has_mount_option(mnt: str, opt: str) -> bool:
    cmd = f"findmnt --target {mnt} -o OPTIONS -n | grep -qw {opt}"
    return subprocess.run(cmd, shell=True).returncode == 0

# Ensure mount and options in fstab for persistence

def _ensure_fstab_option(mnt: str, opt: str, verify_only: bool, REPORT: list, log):
    section = "1.1 Filesystem"
    desc = f"Ensure {opt} option set on {mnt}"
    # Check runtime
    check_cmd = f"findmnt --target {mnt} | grep -q {opt}"
    # Persist by updating /etc/fstab
    fix_cmd = (
        f"sed -i.bak -r 's|(\s{mnt}\s[^\n]*)(defaults|[^,]*)(.*)|\1\2,{opt}\3|' /etc/fstab || "
        f"echo '$(grep -E '^{mnt}' /etc/fstab || grep -E '\s{mnt}\s' /etc/fstab)\n' >> /etc/fstab"
    ) + f" && mount -o remount,{opt} {mnt}"
    _run_check_fix(section, desc, check_cmd, fix_cmd, verify_only, REPORT, log)


def run_section(verify_only, REPORT, log):
    section = "1.1 Filesystem"

    # 1.1.2.1.x /tmp and /dev/shm
    for mnt in ("/tmp", "/dev/shm"):
        # separate partition check
        _run_check_fix(
            section,
            f"Ensure {mnt} is a separate partition",
            f"mount | grep 'on {mnt} ' | grep -q '^/dev/'",
            None,
            verify_only, REPORT, log
        )
        # nodev, nosuid, noexec
        for opt in ("nodev", "nosuid", "noexec"):
            _ensure_fstab_option(mnt, opt, verify_only, REPORT, log)

    # 1.1.2.3.x /home
    mnt = "/home"
    _run_check_fix(
        section,
        f"Ensure {mnt} is a separate partition",
        f"mount | grep 'on {mnt} ' | grep -q '^/dev/'",
        None,
        verify_only, REPORT, log
    )
    for opt in ("nodev", "nosuid"):
        _ensure_fstab_option(mnt, opt, verify_only, REPORT, log)

    # 1.1.2.4.x /var
    mnt = "/var"
    _run_check_fix(
        section,
        f"Ensure {mnt} is a separate partition",
        f"mount | grep 'on {mnt} ' | grep -q '^/dev/'",
        None,
        verify_only, REPORT, log
    )
    for opt in ("nodev", "nosuid"):
        _ensure_fstab_option(mnt, opt, verify_only, REPORT, log)

    log(f"[✔] {section} completed")
