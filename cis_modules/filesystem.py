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
    for mnt in ("/tmp", "/dev/shm"):
        if not _is_mounted(mnt):
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Manual"))
            log(f"[!] {section} - {mnt} not mounted; manual partitioning required")
        else:
            REPORT.append((section, f"Ensure {mnt} is a separate partition", "Compliant"))
            log(f"[✔] {section} - {mnt} is a separate partition")
            for opt in ("nodev","nosuid","noexec"):
                _run_check_fix(
                    section,
                    f"Ensure {opt} option set on {mnt}",
                    f"findmnt --target {mnt} | grep -q {opt}",
                    f"mount -o remount,{opt} {mnt}",
                    verify_only, REPORT, log
                )
    for mnt, opts in (("/home",("nodev","nosuid")), ("/var",("nodev","nosuid"))):
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

    # === UPDATED IMPLEMENTATION ===
    mounts = {
        "/tmp":    {"device":"/dev/mapper/rootvg-tmplv",   "fstype":"xfs","opts":["nodev","nosuid","noexec"]},
        "/dev/shm":{"device":"tmpfs",                     "fstype":"tmpfs","opts":["nodev","nosuid","noexec"]},
        "/home":   {"device":"/dev/mapper/rootvg-homelv",  "fstype":"xfs","opts":["nodev","nosuid"]},
        "/var":    {"device":"/dev/mapper/rootvg-varlv",   "fstype":"xfs","opts":["nodev","nosuid"]},
    }
    for path, info in mounts.items():
        dev, ftype, opts = info["device"], info["fstype"], info["opts"]
        opts_str = ",".join(opts)
        check_cmd = (
            f"grep -E '^\\s*\\S+\\s+{path}\\s+' /etc/fstab | "
            + " && ".join([f"grep -qw {o}" for o in opts])
        )
        fix_cmd = (
            f"if grep -qE '^\\s*\\S+\\s+{path}\\s' /etc/fstab; then "
            f"sed -r -i '/\\s{path}\\s/s|(\\S+\\s+{path}\\s+\\S+\\s+)\\S+|\\1defaults,{opts_str}|' /etc/fstab; "
            f"else echo '{dev} {path} {ftype} defaults,{opts_str} 0 0' >> /etc/fstab; fi && "
            f"mount -o remount,{opts_str} {path}"
        )
        _run_check_fix(
            section,
            f"Ensure defaults,{opts_str} in fstab for {path}",
            check_cmd, fix_cmd,
            verify_only, REPORT, log
        )
