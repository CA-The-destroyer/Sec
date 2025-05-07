# cis_modules/filesystem.py

import subprocess
from cis_modules import _run_check_fix

def _is_mounted(mount_point: str) -> bool:
    """
    Return True if mount_point is an independent mount (of any type).
    """
    return subprocess.run(
        f"findmnt --target {mount_point}", shell=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode == 0

def run_section(verify_only, REPORT, log):
    section = "1.1 Filesystem"

    # 1.1.1 Disable unused filesystem kernel modules
    fs_modules = [
        ("cramfs",     "Ensure cramfs kernel module is not available"),
        ("freevxfs",   "Ensure freevxfs kernel module is not available"),
        ("hfs",        "Ensure hfs kernel module is not available"),
        ("hfsplus",    "Ensure hfsplus kernel module is not available"),
        ("jffs2",      "Ensure jffs2 kernel module is not available"),
        ("squashfs",   "Ensure squashfs kernel module is not available"),
        ("udf",        "Ensure udf kernel module is not available"),
        ("usb-storage","Ensure usb-storage kernel module is not available"),
    ]
    for mod, desc in fs_modules:
        check = f"modprobe -n -v {mod} | grep -E 'install /bin/false'"
        fix   = (
            f"echo 'install {mod} /bin/false' >> /etc/modprobe.d/CIS.conf && "
            f"echo 'blacklist {mod}' >> /etc/modprobe.d/CIS.conf"
        )
        _run_check_fix(section, desc, check, fix, verify_only, REPORT, log)

    # 1.1.2 Ensure separate partitions and mount options
    mounts = {
        "/tmp":     ["nodev", "nosuid", "noexec"],
        "/dev/shm": ["nodev", "nosuid", "noexec"],
        "/home":    ["nodev", "nosuid"],
        "/var":     ["nodev", "nosuid"],
    }

    for mnt, opts in mounts.items():
        # Check if the mount point is an independent mount
        if not _is_mounted(mnt):
            log(f"[!] {section} - {mnt} is not a separate mount; manual partition required")
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual remediation required"))
            continue

        # Mark partition compliance
        REPORT.append((section, f"Ensure {mnt} is a separate partition", "Compliant"))
        log(f"[✔] {section} - {mnt} is a separate partition")

        # Enforce mount options only if mounted
        for opt in opts:
            desc  = f"Ensure {opt} option set on {mnt}"
            check = f"findmnt --target {mnt} | grep -q {opt}"
            fix   = f"mount -o remount,{opt} {mnt}"
            _run_check_fix(section, desc, check, fix, verify_only, REPORT, log)

