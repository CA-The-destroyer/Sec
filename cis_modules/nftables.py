# cis_modules/nftables.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "4.3 nftables"

    # 4.3.1 Ensure base chains exist
    _run_check_fix(
        section,
        "Ensure nftables base chains exist",
        "nft list tables | grep -q inet",
        "nft add table inet filter",
        verify_only, REPORT, log
    )

    # 4.3.2 Ensure established connections are allowed
    _run_check_fix(
        section,
        "Ensure nftables established connections allowed",
        "nft list chain inet filter input | grep -q 'ct state established,related accept'",
        "nft insert rule inet filter input ct state established,related accept",
        verify_only, REPORT, log
    )

    # 4.3.3 Ensure default deny policy
    _run_check_fix(
        section,
        "Ensure nftables default deny policy",
        "nft list chain inet filter input | grep -q 'policy drop'",
        "nft chain inet filter input { type filter hook input priority 0 \; policy drop \; }",
        verify_only, REPORT, log
    )
