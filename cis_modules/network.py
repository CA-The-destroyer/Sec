# cis_modules/network.py

import subprocess
import shlex
from cis_modules import _run_check_fix

SYSCTL_CONF = "/etc/sysctl.d/99-cis.conf"

def _run_sysctl(key: str, value: str, persist: bool, verify_only: bool, REPORT: list, log, section: str):
    """
    Checks `sysctl key` against a value and, if necessary, sets it and persists in SYSCTL_CONF.
    """
    check_cmd = f"sysctl {key} | grep -q '= {value}'"
    fix_parts = [f"sysctl -w {key}={value}"]
    if persist:
        fix_parts.append(
            f"mkdir -p $(dirname {SYSCTL_CONF}) && "
            f"(grep -Eq '^\\s*{key}\\s*=' {SYSCTL_CONF} "
            f"&& sed -i -E 's|^{key}.*|{key} = {value}|' {SYSCTL_CONF} "
            f"|| echo '{key} = {value}' >> {SYSCTL_CONF})"
        )
    fix_cmd = " && ".join(fix_parts)
    _run_check_fix(
        section,
        f"Ensure {key} is set to {value}",
        check_cmd,
        fix_cmd,
        verify_only, REPORT, log
    )

def _get_default_iface():
    """
    Returns the interface name for the default route, e.g. ‘eth0’ or ‘ens33’. 
    Used for Citrix exceptions if needed.
    """
    try:
        out = subprocess.check_output(shlex.split("ip route show default"), text=True)
        parts = out.split()
        if "dev" in parts:
            return parts[parts.index("dev") + 1]
    except subprocess.CalledProcessError:
        pass
    return None

def run_section(verify_only, REPORT, log):
    section = "3.3 Network Kernel Parameters"

    # 3.3.1 Ensure IP forwarding is disabled
    _run_sysctl("net.ipv4.ip_forward", "0", True, verify_only, REPORT, log, section)

    # 3.3.2 Ensure ICMP redirects are not sent
    _run_sysctl("net.ipv4.conf.all.send_redirects", "0", True, verify_only, REPORT, log, section)

    # 3.3.3 Ensure bogus ICMP responses are ignored
    _run_sysctl("net.ipv4.icmp_ignore_bogus_error_responses", "1", True, verify_only, REPORT, log, section)

    # 3.3.4 Ensure broadcast ICMP requests are ignored
    _run_sysctl("net.ipv4.icmp_echo_ignore_broadcasts", "1", True, verify_only, REPORT, log, section)

    # 3.3.5 Ensure ICMP redirects are not accepted
    _run_sysctl("net.ipv4.conf.all.accept_redirects", "0", True, verify_only, REPORT, log, section)

    # 3.3.6 & 3.3.8 Ensure source routed packets are not accepted
    _run_sysctl("net.ipv4.conf.all.accept_source_route", "0", True, verify_only, REPORT, log, section)

    # 3.3.7 Ensure reverse path filtering is enabled
    _run_sysctl("net.ipv4.conf.all.rp_filter", "1", True, verify_only, REPORT, log, section)

    # Citrix exception: disable rp_filter on the default‐route interface if needed
    iface = _get_default_iface()
    if iface:
        _run_sysctl(f"net.ipv4.conf.{iface}.rp_filter", "0", True, verify_only, REPORT, log, section)
        log(f"[✔] {section} – Disabled rp_filter on default interface '{iface}' (Citrix exception)")

    # 3.3.9 Ensure suspicious packets are logged
    _run_sysctl("net.ipv4.conf.all.log_martians", "1", True, verify_only, REPORT, log, section)

    # 3.3.10 Ensure TCP SYN cookies is enabled
    _run_sysctl("net.ipv4.tcp_syncookies", "1", True, verify_only, REPORT, log, section)

    # 3.3.11 Ensure IPv6 router advertisements are not accepted by default
    _run_sysctl("net.ipv6.conf.all.accept_ra", "0", True, verify_only, REPORT, log, section)

    # Citrix exception: allow RA on the default‐route interface
    if iface:
        _run_sysctl(f"net.ipv6.conf.{iface}.accept_ra", "1", True, verify_only, REPORT, log, section)
        log(f"[✔] {section} – Exception: enabled IPv6 RA on interface '{iface}'")

    log(f"[✔] {section} completed")
