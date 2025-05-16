# cis_modules/firewall.py

import subprocess
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "4 Host-based Firewall"

    #
    # 4.1.2 Ensure only one firewall configuration utility is in use (firewalld)
    #
    _run_check_fix(
        section,
        "Ensure firewalld is the only firewall utility",
        (
            "rpm -q firewalld &>/dev/null && systemctl is-enabled --quiet firewalld.service "
            "&& ! rpm -q nftables &>/dev/null"
        ),
        (
            # Remove any other firewall utilities
            "dnf remove -y nftables iptables-services ufw firewalld || true; "
            # Install and enable firewalld
            "dnf install -y firewalld && systemctl enable --now firewalld.service"
        ),
        verify_only, REPORT, log
    )

    #
    # 4.2.2 Ensure firewalld loopback traffic is configured
    #
    _run_check_fix(
        section,
        "Ensure firewalld loopback traffic is configured",
        "firewall-cmd --zone=public --query-interface=lo",
        "firewall-cmd --zone=public --add-interface=lo --permanent && firewall-cmd --reload",
        verify_only, REPORT, log
    )
