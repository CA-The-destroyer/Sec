# cis_modules/firewall.py

import subprocess
from cis_modules import _run_check_fix

def _has_firewalld() -> bool:
    return subprocess.run(
        ["systemctl", "is-active", "--quiet", "firewalld"]
    ).returncode == 0

def run_section(verify_only, REPORT, log):
    section = "4.2 FirewallD / nftables"

    ssh_desc         = "Allow SSH (port 22)"
    loopback_desc    = "Allow loopback traffic"
    # Citrix ICA (TCP & UDP)
    vdi_tcp_1494     = "Allow Citrix VDI TCP 1494"
    vdi_tcp_2598     = "Allow Citrix VDI TCP 2598"
    vdi_udp_1494     = "Allow Citrix VDI UDP 1494"
    vdi_udp_2598     = "Allow Citrix VDI UDP 2598"
    # Registration ports (HTTP/HTTPS)
    reg_tcp_80       = "Allow Citrix Registration TCP 80"
    reg_tcp_443      = "Allow Citrix Registration TCP 443"
    # LDAP / FAS ports
    ldap_tcp_389     = "Allow LDAP TCP 389"
    ldap_tcp_636     = "Allow LDAPS TCP 636"
    ldap_udp_389     = "Allow LDAP UDP 389"
    ldap_udp_636     = "Allow LDAPS UDP 636"

    if _has_firewalld():
        log("[→] Using firewalld for firewall configuration")

        # ── SSH ──────────────────────────────────────────────────────────────────
        _run_check_fix(
            section, ssh_desc,
            "firewall-cmd --zone=public --query-service=ssh",
            "firewall-cmd --permanent --zone=public --add-service=ssh && firewall-cmd --reload",
            verify_only, REPORT, log
        )

        # ── Loopback ─────────────────────────────────────────────────────────────
        _run_check_fix(
            section, loopback_desc,
            "firewall-cmd --zone=trusted --query-interface=lo",
            "firewall-cmd --permanent --zone=trusted --add-interface=lo && firewall-cmd --reload",
            verify_only, REPORT, log
        )

        # ── Citrix ICA (TCP 1494, 2598) ──────────────────────────────────────────
        for port in (1494, 2598):
            desc = f"Allow Citrix VDI TCP {port}"
            _run_check_fix(
                section, desc,
                f"firewall-cmd --zone=public --query-port={port}/tcp",
                f"firewall-cmd --permanent --zone=public --add-port={port}/tcp && firewall-cmd --reload",
                verify_only, REPORT, log
            )

        # ── Citrix ICA (UDP 1494, 2598) ──────────────────────────────────────────
        for port in (1494, 2598):
            desc = f"Allow Citrix VDI UDP {port}"
            _run_check_fix(
                section, desc,
                f"firewall-cmd --zone=public --query-port={port}/udp",
                f"firewall-cmd --permanent --zone=public --add-port={port}/udp && firewall-cmd --reload",
                verify_only, REPORT, log
            )

        # ── Registration (TCP 80, 443) ───────────────────────────────────────────
        for port in (80, 443):
            desc = f"Allow Citrix Registration TCP {port}"
            _run_check_fix(
                section, desc,
                f"firewall-cmd --zone=public --query-port={port}/tcp",
                f"firewall-cmd --permanent --zone=public --add-port={port}/tcp && firewall-cmd --reload",
                verify_only, REPORT, log
            )

        # ── LDAP / FAS (TCP/UDP 389, 636) ────────────────────────────────────────
        for port in (389, 636):
            # TCP
            desc_tcp = f"Allow LDAP TCP {port}"
            _run_check_fix(
                section, desc_tcp,
                f"firewall-cmd --zone=public --query-port={port}/tcp",
                f"firewall-cmd --permanent --zone=public --add-port={port}/tcp && firewall-cmd --reload",
                verify_only, REPORT, log
            )
            # UDP
            desc_udp = f"Allow LDAP UDP {port}"
            _run_check_fix(
                section, desc_udp,
                f"firewall-cmd --zone=public --query-port={port}/udp",
                f"firewall-cmd --permanent --zone=public --add-port={port}/udp && firewall-cmd --reload",
                verify_only, REPORT, log
            )

    else:
        log("[→] Using nftables for firewall configuration")

        # ── SSH ──────────────────────────────────────────────────────────────────
        _run_check_fix(
            section, ssh_desc,
            "nft list ruleset | grep -q 'tcp dport 22 accept'",
            "nft insert rule inet filter input tcp dport 22 accept || true",
            verify_only, REPORT, log
        )

        # ── Loopback ─────────────────────────────────────────────────────────────
        _run_check_fix(
            section, loopback_desc,
            "nft list ruleset | grep -q 'iif lo accept'",
            "nft insert rule inet filter input iif lo accept || true",
            verify_only, REPORT, log
        )

        # ── Citrix ICA (TCP 1494, 2598) ──────────────────────────────────────────
        for port in (1494, 2598):
            desc = f"Allow Citrix VDI TCP {port}"
            _run_check_fix(
                section, desc,
                f"nft list ruleset | grep -q 'tcp dport {port} accept'",
                f"nft insert rule inet filter input tcp dport {port} accept || true",
                verify_only, REPORT, log
            )

        # ── Citrix ICA (UDP 1494, 2598) ──────────────────────────────────────────
        for port in (1494, 2598):
            desc = f"Allow Citrix VDI UDP {port}"
            _run_check_fix(
                section, desc,
                f"nft list ruleset | grep -q 'udp dport {port} accept'",
                f"nft insert rule inet filter input udp dport {port} accept || true",
                verify_only, REPORT, log
            )

        # ── Registration (TCP 80, 443) ───────────────────────────────────────────
        for port in (80, 443):
            desc = f"Allow Citrix Registration TCP {port}"
            _run_check_fix(
                section, desc,
                f"nft list ruleset | grep -q 'tcp dport {port} accept'",
                f"nft insert rule inet filter input tcp dport {port} accept || true",
                verify_only, REPORT, log
            )

        # ── LDAP / FAS (TCP/UDP 389, 636) ────────────────────────────────────────
        for port in (389, 636):
            # TCP
            desc_tcp = f"Allow LDAP TCP {port}"
            _run_check_fix(
                section, desc_tcp,
                f"nft list ruleset | grep -q 'tcp dport {port} accept'",
                f"nft insert rule inet filter input tcp dport {port} accept || true",
                verify_only, REPORT, log
            )
            # UDP
            desc_udp = f"Allow LDAP UDP {port}"
            _run_check_fix(
                section, desc_udp,
                f"nft list ruleset | grep -q 'udp dport {port} accept'",
                f"nft insert rule inet filter input udp dport {port} accept || true",
                verify_only, REPORT, log
            )

    log(f"[✔] {section} completed")
