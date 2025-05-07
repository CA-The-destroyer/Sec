# cis_modules/network.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "3.3 Network Params"

    # 3.3.1 Ensure IP forwarding is disabled
    _run_check_fix(
        section,
        "Ensure IP forwarding is disabled",
        "sysctl net.ipv4.ip_forward | grep -q '= 0'",
        "sysctl -w net.ipv4.ip_forward=0",
        verify_only, REPORT, log
    )

    # 3.3.8 Ensure source routed packets are not accepted
    _run_check_fix(
        section,
        "Ensure source-routed packets are not accepted",
        "sysctl net.ipv4.conf.all.accept_source_route | grep -q '= 0'",
        "sysctl -w net.ipv4.conf.all.accept_source_route=0",
        verify_only, REPORT, log
    )
