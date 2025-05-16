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
        # Check for a rule that accepts ct state established,related
        "nft list ruleset | grep -E 'ct state established,related accept'",
        # Fix: insert into the inet filter input chain
        "nft insert rule inet filter input ct state established,related accept",
        verify_only, REPORT, log
    )

    #
    # 4.3.3 Ensure nftables default deny firewall policy
    #
    _run_check_fix(
        section,
        "Ensure nftables default deny firewall policy",
        # Check that policy input is drop
        "nft list table inet filter | grep -E '^\\s+policy drop;'",
        # Fix: set the default policy to drop on the inet filter table
        "nft --batch << 'EOF'\n"
        "table inet filter {\n"
        "    chain input { policy drop; }\n"
        "}\n"
        "EOF",
        verify_only, REPORT, log
    )
