# cis_modules/network.py

import os
import subprocess
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "3 Network"

    #
    # 2.2.4 Ensure telnet client is not installed
    #
    _run_check_fix(
        section,
        "Ensure telnet client is not installed",
        "! rpm -q telnet",
        # Aggressive uninstall of any telnet* packages
        "dnf remove -y 'telnet*'",
        verify_only, REPORT, log
    )

    #
    # 3.1.3 Ensure bluetooth (bluez) is not installed or running
    #
    _run_check_fix(
        section,
        "Ensure bluetooth (bluez) is not installed or running",
        "! rpm -q bluez && ! systemctl is-enabled --quiet bluetooth.service && ! systemctl is-active --quiet bluetooth.service",
        "systemctl disable --now bluetooth.service || true && dnf remove -y bluez",
        verify_only, REPORT, log
    )

    #
    # 3.3 Network Kernel Parameters
    #
    sysctl_file = "/etc/sysctl.d/99-cis-network.conf"
    os.makedirs(os.path.dirname(sysctl_file), exist_ok=True)
    open(sysctl_file, "a").close()

    # 3.3.1 IP forwarding
    _run_check_fix(
        section,
        "Ensure IP forwarding is disabled",
        "sysctl -n net.ipv4.ip_forward | grep -xq '0' && grep -xq 'net.ipv4.ip_forward = 0' /etc/sysctl.d/99-cis-network.conf",
        "sed -i '/^net.ipv4.ip_forward/d' /etc/sysctl.d/99-cis-network.conf && "
        "echo 'net.ipv4.ip_forward = 0' >> /etc/sysctl.d/99-cis-network.conf && sysctl --system",
        verify_only, REPORT, log
    )

    # 3.3.8 Source-routed packets
    for scope in ("all", "default"):
        key = f"net.ipv4.conf.{scope}.accept_source_route"
        desc = f"Ensure source-routed packets are not accepted ({scope})"
        _run_check_fix(
            section,
            desc,
            f"sysctl -n {key} | grep -xq '0' && grep -xq '{key} = 0' /etc/sysctl.d/99-cis-network.conf",
            f"sed -i '/^{key}/d' /etc/sysctl.d/99-cis-network.conf && "
            f"echo '{key} = 0' >> /etc/sysctl.d/99-cis-network.conf && sysctl --system",
            verify_only, REPORT, log
        )
