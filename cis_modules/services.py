# Corrected cis_modules/services.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.1 Server Services"

    # CUPS (print server)
    _run_check_fix(
        section,
        "Ensure CUPS (print server) is not installed or running",
        # Check: package absent AND service disabled AND not active
        "! rpm -q cups && ! systemctl is-enabled --quiet cups.service && ! systemctl is-active --quiet cups.service",
        # Fix: disable/stop then remove
        "systemctl disable --now cups.service || true && dnf remove -y cups",
        verify_only, REPORT, log
    )

    # rpcbind
    _run_check_fix(
        section,
        "Ensure rpcbind is not installed or running",
        "! rpm -q rpcbind && ! systemctl is-enabled --quiet rpcbind.service && ! systemctl is-active --quiet rpcbind.service && ! systemctl is-enabled --quiet rpcbind.socket && ! systemctl is-active --quiet rpcbind.socket",
        "systemctl disable --now rpcbind.service rpcbind.socket || true && dnf remove -y rpcbind",
        verify_only, REPORT, log
    )

    # avahi-daemon
    _run_check_fix(
        section,
        "Ensure avahi-daemon is not installed or running",
        "! rpm -q avahi-daemon && ! systemctl is-enabled --quiet avahi-daemon.service && ! systemctl is-active --quiet avahi-daemon.service",
        "systemctl disable --now avahi-daemon.service || true && dnf remove -y avahi-daemon",
        verify_only, REPORT, log
    )

    # Samba server (smb & nmb)
    _run_check_fix(
        section,
        "Ensure samba server (smb,nmb) is not installed or running",
        "! rpm -q samba && ! systemctl is-enabled --quiet smb.service && ! systemctl is-active --quiet smb.service && ! systemctl is-enabled --quiet nmb.service && ! systemctl is-active --quiet nmb.service",
        "systemctl disable --now smb.service nmb.service || true && dnf remove -y samba",
        verify_only, REPORT, log
    )

