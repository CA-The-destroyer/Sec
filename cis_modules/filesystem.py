# cis_modules/filesystem.py

import subprocess
from cis_modules import _run_check_fix

def _is_mounted(mnt: str) -> bool:
    """Return True if `mnt` is mounted according to findmnt."""
    return subprocess.run(
        ["findmnt", "--target", mnt],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode == 0

def run_section(verify_only, REPORT, log):
    section = "1.1 Filesystem"

    # Define mounts and required options
    mounts = {
        "/tmp":  ["nodev", "nosuid", "noexec"],
        "/home": ["nodev"],
        "/var":  ["nodev"]
    }

    for mnt, opts in mounts.items():
        # 1) Manual partition check
        if not _is_mounted(mnt):
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual"))
            log(f"[!] {section} – {mnt} not mounted; manual partitioning required")
            continue
        else:
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Compliant"))
            log(f"[✔] {section} – {mnt} is a separate partition")

        # Build the desired fstab fragment
        opts_str = ",".join(["defaults"] + opts)

        # For each option individually, but we’ll also apply them all at once
        desc = f"Enforce {opts_str} on {mnt} via fstab & remount"
        check_cmd = (
            f"findmnt --target {mnt} -o OPTIONS -n | grep -qw {' '.join(opts)}"
        )
        fix_cmd = (
            # 1a) Unmount the FS so fstab re-mount will pick up new options
            f"umount {mnt} || true; "
            # 1b) Edit fstab: replace any line for this mount with correct defaults+opts
            f"sed -r -i '/\\s{mnt}\\s/ s|^([^ ]+\\s+{mnt}\\s+[^ ]+\\s+)[^ ]+|\\1{opts_str}|' /etc/fstab; "
            # 1c) Remount with the new options
            f"mount {mnt}"
        )

        _run_check_fix(section, desc, check_cmd, fix_cmd, verify_only, REPORT, log)
