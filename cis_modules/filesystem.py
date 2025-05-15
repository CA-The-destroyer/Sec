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
    # 1.1.2.1.x: /tmp and /dev/shm (Manual + Automated checks)
    #
    for mnt in ("/tmp", "/dev/shm"):
        if not _is_mounted(mnt):
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual"))
            log(f"[!] {section} - {mnt} not mounted; manual partitioning required")
        else:
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Compliant"))
            log(f"[✔] {section} - {mnt} is a separate partition")
            # Automated: nodev, nosuid, noexec
            for opt in ("nodev", "nosuid", "noexec"):
                _run_check_fix(
                    section,
                    f"Ensure {opt} option set on {mnt}",
                    f"findmnt --target {mnt} | grep -qw {opt}",
                    f"mount -o remount,{opt} {mnt}",
                    verify_only, REPORT, log
                )

    #
    # 1.1.2.3.x: /home (Manual + Automated)
    #
    mnt = "/home"
    if not _is_mounted(mnt):
        REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual"))
        log(f"[!] {section} - {mnt} not mounted; manual partitioning required")
    else:
        REPORT.append((section, f"Ensure {mnt} is a separate partition", "Compliant"))
        log(f"[✔] {section} - {mnt} is a separate partition")
        # Automated: nodev, nosuid
        for opt in ("nodev", "nosuid"):
            _run_check_fix(
                section,
                f"Ensure {opt} option set on {mnt}",
                f"findmnt --target {mnt} | grep -qw {opt}",
                f"mount -o remount,{opt} {mnt}",
                verify_only, REPORT, log
            )

    #
    # 1.1.2.4.x: /var (Manual + Automated)
    #
    mnt = "/var"
    if not _is_mounted(mnt):
        REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual"))
        log(f"[!] {section} - {mnt} not mounted; manual partitioning required")
    else:
        REPORT.append((section, f"Ensure {mnt} is a separate partition", "Compliant"))
        log(f"[✔] {section} - {mnt} is a separate partition")
        # Automated: nodev, nosuid
        for opt in ("nodev", "nosuid"):
            _run_check_fix(
                section,
                f"Ensure {opt} option set on {mnt}",
                f"findmnt --target {mnt} | grep -qw {opt}",
                f"mount -o remount,{opt} {mnt}",
                verify_only, REPORT, log
            )

    #
    # -- Aggressive FSTAB & Remount Enforcement --
    # Re-apply nodev/nosuid/noexec via fstab entry + remount
    #
    mounts = {
        "/tmp":  ["nodev", "nosuid", "noexec"],
        "/home": ["nodev"],
        "/var":  ["nodev"]
    }

    for mnt, opts in mounts.items():
        if not _is_mounted(mnt):
            continue
        opts_str = ",".join(opts)
        check_cmd = (
            f"findmnt --target {mnt} -o OPTIONS -n | grep -qw '{opts_str}'"
        )
        fix_cmd = (
            # Insert or replace default options line in /etc/fstab
            f"sed -r -i '/\\s{mnt}\\s/s|(defaults)(,[^ ]*)?|\\1,{opts_str}|' /etc/fstab && "
            # Remount with the enforced options
            f"mount -o remount,{opts_str} {mnt}"
        )
        _run_check_fix(
            section,
            f"Ensure {opts_str} options set on {mnt} (fstab & remount)",
            check_cmd,
            fix_cmd,
            verify_only, REPORT, log
        )
