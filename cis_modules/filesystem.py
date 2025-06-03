# cis_modules/filesystem.py

import subprocess
from cis_modules import _run_check_fix

# Helper: ensure a given mount has a specific option, both at runtime and persistently in /etc/fstab.
def _ensure_fstab_option(mnt: str, opt: str, verify_only: bool, REPORT: list, log):
    section = "1.1 Filesystem"
    desc = f"Ensure {opt} option set on {mnt}"
    # Check if the option is already in effect:
    check_cmd = f"findmnt --target {mnt} | grep -qw {opt}"
    # To persist: append or modify /etc/fstab for that mount
    # 1) If an entry for mnt exists, add opt to its options field
    # 2) If no entry (unlikely in production), leave manual
    fix_cmd = (
        f"grep -Eq '\\s{mnt}\\s' /etc/fstab "
        f"&& sed -i.bak -r 's|(\\s{mnt}\\s[^\\n]*)(defaults|[^,]*)(.*)|\\1\\2,{opt}\\3|' /etc/fstab "
        f"|| echo '[MANUAL] No /etc/fstab entry for {mnt}; please add \"{mnt} <fs> <type> defaults,{opt} 0 0\"' >> /tmp/failed_fstab.txt"
        f" && mount -o remount,{opt} {mnt}"
    )
    _run_check_fix(section, desc, check_cmd, fix_cmd, verify_only, REPORT, log)

def run_section(verify_only, REPORT, log):
    section = "1.1 Filesystem"

    # 1.1.2.1.x /tmp and /dev/shm
    for mnt in ("/tmp", "/dev/shm"):
        # 1.1.2.1.x Ensure separate partition exists (manual if not)
        _run_check_fix(
            section,
            f"Ensure {mnt} is a separate partition",
            f"mount | grep 'on {mnt} ' | grep -q '^/dev/'",
            None,  # no automatic fix for “create a partition”
            verify_only, REPORT, log
        )
        # Now ensure nodev, nosuid, noexec on each
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
    # Only nodev, nosuid required for /home
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
    # For /var: nodev, nosuid
    for opt in ("nodev", "nosuid"):
        _ensure_fstab_option(mnt, opt, verify_only, REPORT, log)

    log(f"[✔] {section} completed")
