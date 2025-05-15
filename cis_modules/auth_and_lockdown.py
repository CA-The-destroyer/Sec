# cis_modules/auth_and_lockdown.py

import os
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.5 Additional Process Hardening"
    sysctl_file = "/etc/sysctl.d/99-cis.conf"

    # Ensure the sysctl drop-in directory exists
    os.makedirs(os.path.dirname(sysctl_file), exist_ok=True)
    # Ensure the file exists so our check commands don’t fail
    open(sysctl_file, "a").close()

    # 1) ptrace_scope enforcement
    _run_check_fix(
        section,
        "Ensure ptrace_scope is restricted",
        (
            # runtime must equal “1”
            "sysctl -n kernel.yama.ptrace_scope | grep -xq '1' && "
            # file must contain exact line
            f"grep -xq 'kernel.yama.ptrace_scope = 1' {sysctl_file}"
        ),
        (
            # remove old lines, add correct one, reload
            f"sed -i '/^kernel.yama.ptrace_scope/d' {sysctl_file} && "
            f"echo 'kernel.yama.ptrace_scope = 1' >> {sysctl_file} && "
            "sysctl --system"
        ),
        verify_only, REPORT, log
    )

    # 2) core_pattern enforcement
    _run_check_fix(
        section,
        "Ensure core dump backtraces are disabled",
        (
            # runtime value must be exactly “core”
            "sysctl -n kernel.core_pattern | grep -xq 'core' && "
            # file must contain exact setting
            f"grep -xq 'kernel.core_pattern = core' {sysctl_file}"
        ),
        (
            # remove any previous core_pattern entries, add ours, reload
            f"sed -i '/^kernel.core_pattern/d' {sysctl_file} && "
            f"echo 'kernel.core_pattern = core' >> {sysctl_file} && "
            "sysctl --system"
        ),
        verify_only, REPORT, log
    )
