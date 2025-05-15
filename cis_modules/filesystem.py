import subprocess
from cis_modules import _run_check_fix

def _is_mounted(mnt: str) -> bool:
    return subprocess.run(
        f"findmnt --target {mnt}", shell=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode == 0

def run_section(verify_only, REPORT, log):
    section = "1.1 Filesystem"

    # Original checks for separate-partition and individual mounts
    for mnt in ("/tmp", "/dev/shm"):
        if not _is_mounted(mnt):
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual"))
            log(f"[!] {section} - {mnt} not mounted; manual partitioning required")
        else:
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

    for mnt, opts in (("/home", ("nodev","nosuid")), ("/var", ("nodev","nosuid"))):
        if not _is_mounted(mnt):
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual"))
            log(f"[!] {section} - {mnt} not mounted; manual partitioning required")
        else:
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Compliant"))
            log(f"[✔] {section} - {mnt} is a separate partition")
            for opt in opts:
                _run_check_fix(
                    section,
                    f"Ensure {opt} option set on {mnt}",
                    f"findmnt --target {mnt} | grep -q {opt}",
                    f"mount -o remount,{opt} {mnt}",
                    verify_only, REPORT, log
                )

    # Aggressive enforcement of nodev/nosuid on /tmp, nodev on /home and /var
    for path, opts in {
        "/tmp":  ["nodev", "nosuid"],
        "/home": ["nodev"],
        "/var":  ["nodev"]
    }.items():
        if not _is_mounted(path):
            continue
        opts_str = ",".join(opts)
        check_cmd = (
            f"! rpm -q && findmnt --target {path} -o OPTIONS -n | grep -q '{opts_str}'"
        )
        # (rpm -q is a no-op here just to force the leading "!" syntax flow)
        fix_cmd = (
            f"sed -r -i '/\\s{path}\\s/s|defaults\\S*|defaults,{opts_str}|' /etc/fstab && "
            f"mount -o remount,{opts_str} {path}"
        )
        _run_check_fix(
            section,
            f"Ensure {opts_str} options set on {path} (aggressive enforce)",
            check_cmd,
            fix_cmd,
            verify_only, REPORT, log
        )
