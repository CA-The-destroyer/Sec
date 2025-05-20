# cis_modules/network_reverse.py
import os
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "3 Network (Revert)"

    # 2.2.4 Re-install telnet client
    _run_check_fix(
        section,
        "Reinstall telnet client",
        "rpm -q telnet",
        "dnf install -y 'telnet*'",
        verify_only, REPORT, log
    )

    # 3.1.3 Re-enable bluetooth (bluez)
    _run_check_fix(
        section,
        "Re-enable bluetooth (bluez)",
        "rpm -q bluez && systemctl is-enabled --quiet bluetooth.service && systemctl is-active --quiet bluetooth.service",
        (
            "dnf install -y bluez || true && "
            "systemctl enable --now bluetooth.service"
        ),
        verify_only, REPORT, log
    )

    # 3.3 Remove CIS network sysctl overrides
    sysctl_file = "/etc/sysctl.d/99-cis-network.conf"
    # Ensure file exists for removal actions
    if os.path.exists(sysctl_file):
        # Remove specific entries
        lines_to_strip = [
            'net.ipv4.ip_forward',
            'net.ipv4.conf.all.accept_source_route',
            'net.ipv4.conf.default.accept_source_route'
        ]
        # Build sed deletion commands
        delete_cmds = []
        for key in lines_to_strip:
            delete_cmds.append(f"sed -i '/^{key}/d' {sysctl_file}")
        delete_cmds.append("sysctl --system")
        full_cmd = " && ".join(delete_cmds)
    else:
        full_cmd = "echo 'No CIS network overrides to remove'"

    _run_check_fix(
        section,
        "Remove CIS network sysctl overrides",
        f"[ ! -f {sysctl_file} ] || ! grep -q 'net.ipv4.ip_forward' {sysctl_file}",
        full_cmd,
        verify_only, REPORT, log
    )
