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

    #
    # 1.1.2.1.x and 1.1.2.2.x: /tmp and /dev/shm
    #
    for mnt in ("/tmp", "/dev/shm"):
        if not _is_mounted(mnt):
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual"))
            log(f"[!] {section} – {mnt} not mounted; manual partitioning required")
        else:
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Compliant"))
            log(f"[✔] {section} – {mnt} is a separate partition")
            for opt in ("nodev", "nosuid", "noexec"):
                _run_check_fix(
                    section,
                    f"Ensure {opt} option set on {mnt}",
                    f"findmnt --target {mnt} -o OPTIONS -n | grep -qw {opt}",
                    # 1) Update fstab (insert opt if missing), 2) Remount
                    (
                        f"grep -q '{mnt} ' /etc/fstab && "
                        f"sed -r -i '/\\s{mnt}\\s/s|(defaults)(,[^ ]*)?|\\1,{opt}\\2|' /etc/fstab; "
                        f"mount -o remount,{opt} {mnt}"
                    ),
                    verify_only, REPORT, log
                )

    #
    # 1.1.2.3.x: /home
    #
    mnt = "/home"
    if not _is_mounted(mnt):
        REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual"))
        log(f"[!] {section} – {mnt} not mounted; manual partitioning required")
    else:
        REPORT.append((section, f"Ensure {mnt} is a separate partition", "Compliant"))
        log(f"[✔] {section} – {mnt} is a separate partition")
        for opt in ("nodev", "nosuid"):
            _run_check_fix(
                section,
                f"Ensure {opt} option set on {mnt}",
                f"findmnt --target {mnt} -o OPTIONS -n | grep -qw {opt}",
                (
                    f"grep -q '{mnt} ' /etc/fstab && "
                    f"sed -r -i '/\\s{mnt}\\s/s|(defaults)(,[^ ]*)?|\\1,{opt}\\2|' /etc/fstab; "
                    f"mount -o remount,{opt} {mnt}"
                ),
                verify_only, REPORT, log
            )

    #
    # 1.1.2.4.x: /var
    #
    mnt = "/var"
    if not _is_mounted(mnt):
        REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual"))
        log(f"[!] {section} – {mnt} not mounted; manual partitioning required")
    else:
        REPORT.append((section, f"Ensure {mnt} is a separate partition", "Compliant"))
        log(f"[✔] {section} – {mnt} is a separate partition")
        for opt in ("nodev", "nosuid"):
            _run_check_fix(
                section,
                f"Ensure {opt} option set on {mnt}",
                f"findmnt --target {mnt} -o OPTIONS -n | grep -qw {opt}",
                (
                    f"grep -q '{mnt} ' /etc/fstab && "
                    f"sed -r -i '/\\s{mnt}\\s/s|(defaults)(,[^ ]*)?|\\1,{opt}\\2|' /etc/fstab; "
                    f"mount -o remount,{opt} {mnt}"
                ),
                verify_only, REPORT, log
            )
