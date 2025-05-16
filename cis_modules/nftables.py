# cis_modules/nftables.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "4.3 NFTables"

    #
    # 4.3.2 Ensure nftables established connections are configured
    #
    _run_check_fix(
        section,
        "Ensure nftables established connections are configured",
        "nft list ruleset | grep -E 'ct state established,related accept'",
        # Create the rule if missing
        (
            "nft add table inet filter || true; "
            "nft 'add chain inet filter input { type filter hook input priority 0; policy drop; }' || true; "
            "nft insert rule inet filter input ct state established,related accept || true"
        ),
        verify_only, REPORT, log
    )

    #
    # 4.3.3 Ensure nftables default deny firewall policy
    #
    _run_check_fix(
        section,
        "Ensure nftables default deny firewall policy",
        "nft list table inet filter | grep -E '^\\s+policy drop;'",
        # Recreate table if needed and set policy
        (
            "nft add table inet filter || true; "
            "nft 'flush chain inet filter input; set policy chain inet filter input drop;' || true"
        ),
        verify_only, REPORT, log
    )
