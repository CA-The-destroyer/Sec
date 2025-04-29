# cis_modules/filesystem.py
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.1 Filesystem"
    # Disable uncommon fs modules
    fs_modules = [
        ("cramfs", "Ensure cramfs kernel module is not available"),
        ("freevxfs", "Ensure freevxfs kernel module is not available"),
        ("hfs", "Ensure hfs kernel module is not available"),
        ("hfsplus", "Ensure hfsplus kernel module is not available"),
        ("jffs2", "Ensure jffs2 kernel module is not available"),
        ("squashfs", "Ensure squashfs kernel module is not available"),
        ("udf", "Ensure udf kernel module is not available"),
        ("usb-storage", "Ensure usb-storage kernel module is not available")
    ]
    for mod, desc in fs_modules:
        check = f"/sbin/modprobe -n -v {mod} | grep -E 'install /bin/(true|false)'"
        fix = f"echo 'install {mod} /bin/false' >> /etc/modprobe.d/CIS.conf && echo 'blacklist {mod}' >> /etc/modprobe.d/CIS.conf"
        _run_check_fix(section, desc, check, fix, verify_only, REPORT, log)

    # Partition options for tmp, var/tmp, home, var/log, var/log/audit, dev/shm
    mounts = [
        ("/tmp", ["nodev","nosuid","noexec"]),
        ("/var/tmp", ["nodev","nosuid","noexec"]),
        ("/dev/shm", ["nodev","nosuid","noexec"]),
        ("/home", ["nodev"]),
        ("/var", ["nodev"]),ddassadaszcx
        ("/var/log", ["nodev","nosuid","noexec"]),
        ("/var/log/audit", ["nodev","nosuid","noexec"])
    ]
    for mnt, opts in mounts:
        desc_sep = f"Ensure {mnt} is a separate partition"
        check_sep = f"mount | grep 'on {mnt} ' | grep -q '^/dev/'"
        _run_check_fix(section, desc_sep, check_sep, None, verify_only, REPORT, log)
        for opt in opts:
            desc_opt = f"Ensure {opt} option set on {mnt}"
            check_opt = f"findmnt --target {mnt} | grep -q {opt}"
            fix_opt = f"mount -o remount,{opt} {mnt}"
            _run_check_fix(section, desc_opt, check_opt, fix_opt, verify_only, REPORT, log)
