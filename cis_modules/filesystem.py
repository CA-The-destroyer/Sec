# cis_modules/filesystem.py

import subprocess
from cis_modules import _run_check_fix

def _is_mounted(mnt: str) -> bool:
    """Return True if `mnt` appears in the output of findmnt."""
    return subprocess.run(
        f"findmnt --target {mnt}", shell=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode == 0

def run_section(verify_only, REPORT, log):
    section = "1.1 Filesystem"

    mounts = {
        "/tmp":  ["nodev", "nosuid", "noexec"],
        "/home": ["nodev"],
        "/var":  ["nodev"]
    }

    for mnt, opts in mounts.items():
        # 1.1.2.x: separate-partition check
        if not _is_mounted(mnt):
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual"))
            log(f"[!] {section} - {mnt} not mounted; manual partitioning required")
            continue
        else:
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Compliant"))
            log(f"[✔] {section} - {mnt} is a separate partition")

        # For each option, check and aggressively fix
        for opt in opts:
            desc     = f"Ensure {opt} option set on {mnt}"
            check_cmd = f"findmnt --target {mnt} -o OPTIONS -n | grep -qw {opt}"
            fix_cmd   = (
                # 1) Add the option into /etc/fstab if missing
                f"grep -q '{mnt} ' /etc/fstab && "
                f"sed -r -i '/\\s{mnt}\\s/s|(defaults)(,[^ ]*)?|\\1,{opt}\\2|' /etc/fstab; "
                # 2) Remount with that option
                f"mount -o remount,{opt} {mnt}"
            )
            _run_check_fix(
                section,
                desc,
                check_cmd,
                fix_cmd,
                verify_only, REPORT, log
            )
