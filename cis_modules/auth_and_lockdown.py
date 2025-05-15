# cis_modules/auth_and_lockdown.py

import os
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.5 Additional Process Hardening"

    sysctl_file = "/etc/sysctl.d/99-cis.conf"
    # Ensure the directory exists
    os.makedirs(os.path.dirname(sysctl_file), exist_ok=True)

    # 1) ptrace_scope enforcement
    _run_check_fix(
        section,
        "Ensure ptrace_scope is restricted",
        # Pass if runtime value ≥1 and file has exact entry
        "sysctl kernel.yama.ptrace_scope | grep -qE '^kernel.yama.ptrace_scope = [1-5]$' "
        "&& grep -qE '^kernel.yama.ptrace_scope = 1$' " + sysctl_file,
        # Fix: remove any old lines, add our line, reload
        (
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
        # Pass if runtime value does NOT start with '|' and file has exact entry
        "sysctl kernel.core_pattern | grep -qv '^\\|' "
        "&& grep -qE '^kernel.core_pattern = core$' " + sysctl_file,
        # Fix: remove any old core_pattern lines, add our entry, reload
        (
            f"sed -i '/^kernel.core_pattern/d' {sysctl_file} && "
            f"echo 'kernel.core_pattern = core' >> {sysctl_file} && "
            "sysctl --system"
        ),
        verify_only, REPORT, log
    )
