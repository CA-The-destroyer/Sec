# cis_modules/firewall.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "4.1–4.2 Firewall"

    # 4.1.1 Ensure nftables is installed
    _run_check_fix(
        section,
        "Ensure nftables is installed",
        "rpm -q nftables",
        "yum install -y nftables",
        verify_only, REPORT, log
    )

    # 4.1.2 Ensure a single firewall utility is in use
    _run_check_fix(
        section,
        "Ensure only nftables or firewalld is in use",
        "(! rpm -q firewalld ) || (! rpm -q nftables )",
        None,
        verify_only, REPORT, log
    )

    # 4.2.2 Ensure firewalld loopback traffic is configured
    _run_check_fix(
        section,
        "Ensure firewalld allows loopback",
        "firewall-cmd --list-interfaces | grep -q lo",
        "firewall-cmd --permanent --zone=trusted --add-interface=lo && firewall-cmd --reload",
        verify_only, REPORT, log
    )
