# cis_modules/nftables.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "4.3 NFTables"

    #
    # 4.3.1 Ensure nftables base table & input chain exist with default deny
    #
    _run_check_fix(
        section,
        "Ensure nftables base table & input chain exist",
        "nft list table inet filter &>/dev/null",
        (
            "nft add table inet filter || true && "
            "nft 'add chain inet filter input { type filter hook input priority 0; policy drop; }' || true"
        ),
        verify_only, REPORT, log
    )

    #
    # 4.3.2 Ensure nftables established connections are accepted
    #
    _run_check_fix(
        section,
        "Ensure nftables established connections are accepted",
        "nft list ruleset | grep -q 'ct state established,related accept'",
        "nft insert rule inet filter input ct state established,related accept || true",
        verify_only, REPORT, log
    )

    #
    # 4.3.3 Ensure nftables default deny firewall policy
    #
    _run_check_fix(
        section,
        "Ensure nftables default deny firewall policy",
        "nft list table inet filter | grep -E '^\\s+policy drop;'",
        "nft 'flush chain inet filter input; set policy chain inet filter input drop;' || true",
        verify_only, REPORT, log
    )

    #
    # Allow SSH (port 22) so scp/sftp traffic works
    #
    _run_check_fix(
        section,
        "Allow SSH (TCP 22) for SSH/SCP/SFTP",
        "nft list ruleset | grep -q 'tcp dport 22 accept'",
        "nft insert rule inet filter input tcp dport 22 accept || true",
        verify_only, REPORT, log
    )

    #
    # Citrix VDI ports (TCP 1494 & 2598)
    #
    _run_check_fix(
        section,
        "Allow Citrix VDI TCP 1494",
        "nft list ruleset | grep -q 'tcp dport 1494 accept'",
        "nft insert rule inet filter input tcp dport 1494 accept || true",
        verify_only, REPORT, log
    )
    _run_check_fix(
        section,
        "Allow Citrix VDI TCP 2598",
        "nft list ruleset | grep -q 'tcp dport 2598 accept'",
        "nft insert rule inet filter input tcp dport 2598 accept || true",
        verify_only, REPORT, log
    )
