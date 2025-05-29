# cis_modules/nftables.py

from cis_modules import _run_check_fix


def run_section(verify_only, REPORT, log):
    section = "4.3 Configure NFTables"

    # 4.3.1 Ensure nftables base chains exist
    _run_check_fix(
        section,
        "Ensure nftables base chains exist",
        "nft list table inet filter | grep -q 'chain input'",
        (
            "nft add table inet filter && "
            "nft 'add chain inet filter input { type filter hook input priority 0; }' && "
            "nft 'add chain inet filter forward { type filter hook forward priority 0; }' && "
            "nft 'add chain inet filter output { type filter hook output priority 0; }'"
        ),
        verify_only, REPORT, log
    )

    # 4.3.2 Ensure nftables established connections are configured
    _run_check_fix(
        section,
        "Ensure nftables established connections are accepted",
        "nft list ruleset | grep -q 'ct state established,related accept'",
        "nft insert rule inet filter input ct state established,related accept",
        verify_only, REPORT, log
    )

    # 4.3.3 Ensure nftables default deny firewall policy
    _run_check_fix(
        section,
        "Ensure nftables default deny firewall policy",
        "nft list ruleset | grep -q 'policy drop'",
        (
            "nft insert rule inet filter input ct state invalid drop && "
            "nft add rule inet filter input counter drop"
        ),
        verify_only, REPORT, log
    )

    # 4.3.4 Ensure nftables loopback traffic is configured
    _run_check_fix(
        section,
        "Ensure nftables loopback traffic is accepted",
        "nft list ruleset | grep -q 'iif lo accept'",
        "nft insert rule inet filter input iif lo accept",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
