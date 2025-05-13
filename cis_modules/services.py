# cis_modules/services.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.1 Server Services"

    for svc in ("autofs", "avahi-daemon", "dnsmasq", "rpcbind", "smb", "nfs"): 
        _run_check_fix(
            section,
            f"Ensure {svc} service is not in use",
            f"systemctl is-enabled --quiet {svc}",
            f"dnf remove -y {svc} || systemctl disable --now {svc}",
            verify_only, REPORT, log
        )
