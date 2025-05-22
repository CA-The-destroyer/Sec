# cis_modules/firewall.py

import subprocess
from cis_modules import _run_check_fix

def _has_firewalld():
    return subprocess.run(
        ["systemctl", "is-active", "--quiet", "firewalld"]
    ).returncode == 0

def run_section(verify_only, REPORT, log):
    section = "4.2 FirewallD / nftables"
    ssh_desc       = "Allow SSH (port 22)"
    loopback_desc  = "Allow loopback traffic"
    vdi_tcp_1494   = "Allow Citrix VDI TCP 1494"
    vdi_tcp_2598   = "Allow Citrix VDI TCP 2598"
    vdi_udp_1494   = "Allow Citrix VDI UDP 1494"
    vdi_udp_2598   = "Allow Citrix VDI UDP 2598"

    if _has_firewalld():
        log("[→] Using firewalld for firewall configuration")

        _run_check_fix(
            section, ssh_desc,
            "firewall-cmd --zone=public --query-service=ssh",
            "firewall-cmd --permanent --zone=public --add-service=ssh && firewall-cmd --reload",
            verify_only, REPORT, log
        )
        _run_check_fix(
            section, loopback_desc,
            "firewall-cmd --zone=trusted --query-interface=lo",
            "firewall-cmd --permanent --zone=trusted --add-interface=lo && firewall-cmd --reload",
            verify_only, REPORT, log
        )
        # Citrix VDI TCP
        _run_check_fix(
            section, vdi_tcp_1494,
            "firewall-cmd --zone=public --query-port=1494/tcp",
            "firewall-cmd --permanent --zone=public --add-port=1494/tcp && firewall-cmd --reload",
            verify_only, REPORT, log
        )
        _run_check_fix(
            section, vdi_tcp_2598,
            "firewall-cmd --zone=public --query-port=2598/tcp",
            "firewall-cmd --permanent --zone=public --add-port=2598/tcp && firewall-cmd --reload",
            verify_only, REPORT, log
        )
        # Citrix VDI UDP
        _run_check_fix(
            section, vdi_udp_1494,
            "firewall-cmd --zone=public --query-port=1494/udp",
            "firewall-cmd --permanent --zone=public --add-port=1494/udp && firewall-cmd --reload",
            verify_only, REPORT, log
        )
        _run_check_fix(
            section, vdi_udp_2598,
            "firewall-cmd --zone=public --query-port=2598/udp",
            "firewall-cmd --permanent --zone=public --add-port=2598/udp && firewall-cmd --reload",
            verify_only, REPORT, log
        )

    else:
        log("[→] Using nftables for firewall configuration")

        _run_check_fix(
            section, ssh_desc,
            "nft list ruleset | grep -q 'tcp dport 22 accept'",
            "nft insert rule inet filter input tcp dport 22 accept || true",
            verify_only, REPORT, log
        )
        _run_check_fix(
            section, loopback_desc,
            "nft list ruleset | grep -q 'iif lo accept'",
            "nft insert rule inet filter input iif lo accept || true",
            verify_only, REPORT, log
        )
        # Citrix VDI TCP
        _run_check_fix(
            section, vdi_tcp_1494,
            "nft list ruleset | grep -q 'tcp dport 1494 accept'",
            "nft insert rule inet filter input tcp dport 1494 accept || true",
            verify_only, REPORT, log
        )
        _run_check_fix(
            section, vdi_tcp_2598,
            "nft list ruleset | grep -q 'tcp dport 2598 accept'",
            "nft insert rule inet filter input tcp dport 2598 accept || true",
            verify_only, REPORT, log
        )
        # Citrix VDI UDP
        _run_check_fix(
            section, vdi_udp_1494,
            "nft list ruleset | grep -q 'udp dport 1494 accept'",
            "nft insert rule inet filter input udp dport 1494 accept || true",
            verify_only, REPORT, log
        )
        _run_check_fix(
            section, vdi_udp_2598,
            "nft list ruleset | grep -q 'udp dport 2598 accept'",
            "nft insert rule inet filter input udp dport 2598 accept || true",
            verify_only, REPORT, log
        )

    log(f"[✔] {section} completed")
