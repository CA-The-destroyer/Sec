# cis_modules/firewall.py

import subprocess
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "4 Host-based Firewall"

    #
    # 4.1.2 Ensure only one firewall configuration utility is in use
    # We’ll prefer firewalld; if nftables is present we disable it, vice versa.
    #
    # Check: exactly one of firewalld or ufw or nftables is installed & enabled
    check_cmd = (
        "("
        "rpm -q firewalld &>/dev/null && systemctl is-enabled --quiet firewalld.service && "
        "! (rpm -q nftables &>/dev/null) "
        ") || ( "
        "rpm -q nftables &>/dev/null && systemctl is-enabled --quiet nftables.service && "
        "! (rpm -q firewalld &>/dev/null) "
        ")"
    )
    # Fix: disable/uninstall the non-preferred one; enable the preferred
    fix_cmd = (
        # If nftables installed, disable it; install+enable firewalld
        "if rpm -q nftables &>/dev/null; then "
        "   systemctl disable --now nftables.service || true; dnf remove -y nftables; "
        "fi; "
        "dnf install -y firewalld && systemctl enable --now firewalld.service"
    )
    _run_check_fix(
        section,
        "Ensure a single firewall configuration utility is in use (firewalld)",
        check_cmd,
        fix_cmd,
        verify_only, REPORT, log
    )

    #
    # 4.2.2 Ensure firewalld loopback traffic is configured
    #
    _run_check_fix(
        section,
        "Ensure firewalld loopback traffic is configured",
        # Check that loopback interface is allowed in public zone
        "firewall-cmd --zone=public --query-interface=lo",
        # Fix: add interface 'lo' to the public zone permanently
        "firewall-cmd --zone=public --add-interface=lo --permanent && firewall-cmd --reload",
        verify_only, REPORT, log
    )
