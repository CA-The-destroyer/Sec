# cis_modules/firewall_loopback.py

import subprocess
from cis_modules import _run_check_fix

def _has_firewalld():
    return subprocess.run(
        ["systemctl", "is-active", "--quiet", "firewalld"]
    ).returncode == 0

def run_section(verify_only, REPORT, log):
    section = "4.2 Firewall Loopback"

    # 4.2.2 Ensure loopback traffic is allowed via firewalld
    if _has_firewalld():
        _run_check_fix(
            section,
            "Allow loopback interface (firewalld)",
            "firewall-cmd --zone=trusted --query-interface=lo",
            "firewall-cmd --permanent --zone=trusted --add-interface=lo && firewall-cmd --reload",
            verify_only, REPORT, log
        )
    else:
        # 4.2.2 Ensure loopback traffic is allowed via nftables
        _run_check_fix(
            section,
            "Allow loopback interface (nftables)",
            "nft list ruleset | grep -q 'iif lo accept'",
            "nft insert rule inet filter input iif lo accept || true",
            verify_only, REPORT, log
        )

    log(f"[✔] {section} completed")
