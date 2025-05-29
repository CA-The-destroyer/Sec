# cis_modules/network.py

import subprocess
import shlex
from cis_modules import _run_check_fix

SYSCTL_CONF = "/etc/sysctl.d/99-cis.conf"


def _run_sysctl(key, value, persist, verify_only, REPORT, log, section):
    check_cmd = f"sysctl {key} | grep -q '= {value}'"
    fix_parts = [f"sysctl -w {key}={value}"]
    if persist:
        fix_parts.append(
            f"mkdir -p $(dirname {SYSCTL_CONF}) && "
            f"grep -Eq '^\\s*{key}\\s*=' {SYSCTL_CONF} "
            f"&& sed -i 's|^{key}.*|{key} = {value}|' {SYSCTL_CONF} "
            f"|| echo '{key} = {value}' >> {SYSCTL_CONF}"
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
    try:
        out = subprocess.check_output(shlex.split("ip route show default"), text=True)
        parts = out.split()
        if "dev" in parts:
            return parts[parts.index("dev") + 1]
    except subprocess.CalledProcessError:
        pass
    return None


def run_section(verify_only, REPORT, log):
    section = "3.3 Configure Network Kernel Parameters"

    # IPv4 parameters
    params = [
        ("net.ipv4.ip_forward",          "0"),
        ("net.ipv4.conf.all.send_redirects",     "0"),
        ("net.ipv4.icmp_ignore_bogus_error_responses", "1"),
        ("net.ipv4.icmp_echo_ignore_broadcasts",     "1"),
        ("net.ipv4.conf.all.accept_redirects",      "0"),
        ("net.ipv4.conf.all.accept_source_route",   "0"),
        ("net.ipv4.conf.all.rp_filter",             "1"),
        ("net.ipv4.conf.all.log_martians",          "1"),
        ("net.ipv4.tcp_syncookies",                 "1"),
    ]
    for key, val in params:
        _run_sysctl(key, val, True, verify_only, REPORT, log, section)

    # IPv6
    _run_sysctl("net.ipv6.conf.all.accept_ra", "0", True, verify_only, REPORT, log, section)

    # Citrix VDI exceptions
    iface = _get_default_iface()
    if iface:
        # disable rp_filter on default interface
        _run_sysctl(f"net.ipv4.conf.{iface}.rp_filter", "0", True, verify_only, REPORT, log, section)
        log(f"[✔] {section} - Disabled rp_filter on interface '{iface}'")
        # re-enable RA on default interface
        _run_sysctl(f"net.ipv6.conf.{iface}.accept_ra", "1", True, verify_only, REPORT, log, section)
        log(f"[✔] {section} - Enabled IPv6 RA exception on '{iface}'")

    # Disable bluetooth service (3.1.3)
    _run_check_fix(
        section,
        "Ensure bluetooth service is disabled",
        "systemctl is-enabled bluetooth.service | grep -q disabled",
        "systemctl disable --now bluetooth.service",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
