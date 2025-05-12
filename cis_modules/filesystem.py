# cis_modules/filesystem.py

import subprocess
from cis_modules import _run_check_fix

def _is_mounted(mnt: str) -> bool:
    return subprocess.run(
        f"findmnt --target {mnt}", shell=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode == 0

def run_section(verify_only, REPORT, log):
    section = "1.1 Filesystem"

    # === ORIGINAL IMPLEMENTATION ===
    # 1.1.2.1.x /tmp and /dev/shm
    for mnt in ("/tmp", "/dev/shm"):
        if not _is_mounted(mnt):
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual remediation required"))
            log(f"[!] {section} - {mnt} not mounted; manual partitioning required")
            continue
        REPORT.append((section, f"Ensure {mnt} is a separate partition", "Compliant"))
        log(f"[✔] {section} - {mnt} is a separate partition")
        for opt in ("nodev", "nosuid", "noexec"):
            _run_check_fix(
                section,
                f"Ensure {opt} option set on {mnt}",
                f"findmnt --target {mnt} | grep -q {opt}",
                f"mount -o remount,{opt} {mnt}",
                verify_only, REPORT, log
            )

    # 1.1.2.3.x /home
    mnt = "/home"
    if not _is_mounted(mnt):
        REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual remediation required"))
        log(f"[!] {section} - {mnt} not mounted; manual partitioning required")
    else:
        REPORT.append((section, f"Ensure {mnt} is a separate partition", "Compliant"))
        log(f"[✔] {section} - {mnt} is a separate partition")
        for opt in ("nodev", "nosuid"):
            _run_check_fix(
                section,
                f"Ensure {opt} option set on {mnt}",
                f"findmnt --target {mnt} | grep -q {opt}",
                f"mount -o remount,{opt} {mnt}",
                verify_only, REPORT, log
            )

    # 1.1.2.4.x /var
    mnt = "/var"
    if not _is_mounted(mnt):
        REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual remediation required"))
        log(f"[!] {section} - {mnt} not mounted; manual partitioning required")
    else:
        REPORT.append((section, f"Ensure {mnt} is a separate partition", "Compliant"))
        log(f"[✔] {section} - {mnt} is a separate partition")
        for opt in ("nodev", "nosuid"):
            _run_check_fix(
                section,
                f"Ensure {opt} option set on {mnt}",
                f"findmnt --target {mnt} | grep -q {opt}",
                f"mount -o remount,{opt} {mnt}",
                verify_only, REPORT, log
            )

    # === UPDATED IMPLEMENTATION ===
    # Ensure /etc/fstab entries are idempotently configured
    mounts = {
        "/tmp":    ["nodev", "nosuid", "noexec"],
        "/dev/shm":["nodev", "nosuid", "noexec"],
        "/home":   ["nodev", "nosuid"],
        "/var":    ["nodev", "nosuid"],
    }
    for path, opts in mounts.items():
        opts_str = ",".join(opts)
        # 1.1.x.y Ensure fstab line exists with correct options
        _run_check_fix(
            section,
            f"Ensure /etc/fstab entry for {path} contains defaults,{opts_str}",
            f"grep -E '^\\s*{path}\\s+.*defaults[,].*{opts[0]}' /etc/fstab",
            f"sed -i '/^\\s*{path}\\s\\+/d' /etc/fstab && echo '{path} defaults,{opts_str} 0 0' >> /etc/fstab",
            verify_only, REPORT, log
        )

