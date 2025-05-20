# cis_modules/firewall_reverse.py
import subprocess
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "4 Host-based Firewall (Revert)"

    # 4.1.2 Disable firewalld and re-enable other utilities
    _run_check_fix(
        section,
        "Disable firewalld and install nftables/iptables-services/ufw",
        (
            "! rpm -q firewalld"  # firewalld not installed
            " && rpm -q nftables && rpm -q iptables-services && rpm -q ufw"
        ),
        (
            # Stop and remove firewalld
            "systemctl disable --now firewalld.service || true && dnf remove -y firewalld || true; "
            # Install other firewall utilities
            "dnf install -y nftables iptables-services ufw && "
            "systemctl enable --now nftables.service"
        ),
        verify_only, REPORT, log
    )

    # 4.2.2 Remove loopback interface from public zone
    _run_check_fix(
        section,
        "Remove loopback interface from firewalld public zone",
        "! firewall-cmd --zone=public --query-interface=lo",
        "firewall-cmd --zone=public --remove-interface=lo --permanent && firewall-cmd --reload",
        verify_only, REPORT, log
    )