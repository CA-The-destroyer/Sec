# cis_modules/services.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.1 Server Services"

    # 2.1.1 Ensure CUPS (print server) is not installed or running
    _run_check_fix(
        section,
        "Ensure CUPS (print server) is not installed or running",
        "! rpm -q cups && ! systemctl is-enabled --quiet cups.service && ! systemctl is-active --quiet cups.service",
        "systemctl disable --now cups.service || true && dnf remove -y cups",
        verify_only, REPORT, log
    )

    # 2.1.2 Ensure rpcbind is not installed or running
    _run_check_fix(
        section,
        "Ensure rpcbind is not installed or running",
        "! rpm -q rpcbind && ! systemctl is-enabled --quiet rpcbind.service && ! systemctl is-active --quiet rpcbind.service && ! systemctl is-enabled --quiet rpcbind.socket && ! systemctl is-active --quiet rpcbind.socket",
        "systemctl disable --now rpcbind.service rpcbind.socket || true && dnf remove -y rpcbind",
        verify_only, REPORT, log
    )

    # 2.1.3 Ensure avahi-daemon is not installed or running
    _run_check_fix(
        section,
        "Ensure avahi-daemon is not installed or running",
        "! rpm -q avahi-daemon && ! systemctl is-enabled --quiet avahi-daemon.service && ! systemctl is-active --quiet avahi-daemon.service",
        "systemctl disable --now avahi-daemon.service || true && dnf remove -y avahi-daemon",
        verify_only, REPORT, log
    )

    # 2.1.4 Ensure Samba server package is not installed or running
    _run_check_fix(
        section,
        "Ensure samba server (smb,nmb) is not installed or running",
        "! rpm -q samba && ! systemctl is-enabled --quiet smb.service && ! systemctl is-active --quiet smb.service && ! systemctl is-enabled --quiet nmb.service && ! systemctl is-active --quiet nmb.service",
        "systemctl disable --now smb.service nmb.service || true && dnf remove -y samba",
        verify_only, REPORT, log
    )

    # 2.1.6 Ensure Samba file server services are not in use
    # (the loop is commented out because 2.1.4 already handles it)
    # for svc in ("smb", "nmb"):
    #     _run_check_fix(
    #         section,
    #         f"Ensure {svc} service is disabled",
    #         f"systemctl is-enabled {svc}.service",
    #         f"systemctl disable --now {svc}.service",
    #         verify_only, REPORT, log
    #     )

    # 3.1.3 Ensure Bluetooth service is not in use
    _run_check_fix(
        "3.1 Network Services",
        "Ensure Bluetooth service is not in use",
        "systemctl is-enabled bluetooth.service",
        "systemctl disable --now bluetooth.service",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
