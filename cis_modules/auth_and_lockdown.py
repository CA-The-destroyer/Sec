# cis_modules/auth_and_lockdown.py

import subprocess
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.5 Configure Additional Process Hardening"

    # 1.5.1 Ensure address space layout randomization is enabled
    _run_check_fix(
        section,
        "Ensure address space layout randomization (ASLR) is enabled",
        "sysctl kernel.randomize_va_space | grep -q '= 2'",
        "sysctl -w kernel.randomize_va_space=2",
        verify_only, REPORT, log
    )

    # 1.5.2 Ensure ptrace_scope is restricted
    _run_check_fix(
        section,
        "Ensure ptrace_scope is restricted",
        "sysctl kernel.yama.ptrace_scope | grep -q '= 1'",
        (
            "mkdir -p /etc/sysctl.d && "
            "sysctl -w kernel.yama.ptrace_scope=1 && "
            "grep -Eq '^kernel.yama.ptrace_scope' /etc/sysctl.d/99-cis.conf && "
            "sed -i 's/^kernel.yama.ptrace_scope.*/kernel.yama.ptrace_scope = 1/' /etc/sysctl.d/99-cis.conf || "
            "echo 'kernel.yama.ptrace_scope = 1' >> /etc/sysctl.d/99-cis.conf"
        ),
        verify_only, REPORT, log
    )

    # 1.5.3 Ensure core dump backtraces are disabled
    _run_check_fix(
        section,
        "Ensure core dump backtraces are disabled",
        "sysctl kernel.core_pattern | grep -q '^\\|/bin/false'",
        (
            "mkdir -p /etc/sysctl.d && "
            "sysctl -w kernel.core_pattern='|/bin/false' && "
            "grep -Eq '^kernel.core_pattern' /etc/sysctl.d/99-cis.conf && "
            "sed -i \"s|^kernel.core_pattern.*|kernel.core_pattern = |/bin/false|\" "
            "/etc/sysctl.d/99-cis.conf || "
            "echo 'kernel.core_pattern = |/bin/false' >> /etc/sysctl.d/99-cis.conf"
        ),
        verify_only, REPORT, log
    )

    # 1.5.4 Ensure core dump storage is disabled
    _run_check_fix(
        section,
        "Ensure core dump storage is disabled",
        "sysctl fs.suid_dumpable | grep -q '= 0'",
        (
            "mkdir -p /etc/sysctl.d && "
            "sysctl -w fs.suid_dumpable=0 && "
            "grep -Eq '^fs.suid_dumpable' /etc/sysctl.d/99-cis.conf && "
            "sed -i 's/^fs.suid_dumpable.*/fs.suid_dumpable = 0/' /etc/sysctl.d/99-cis.conf || "
            "echo 'fs.suid_dumpable = 0' >> /etc/sysctl.d/99-cis.conf"
        ),
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
