# cis_modules/auth_and_lockdown.py

import subprocess
from pathlib import Path
from cis_modules import _run_check_fix

SYSCTL_CONF = "/etc/sysctl.d/99-cis.conf"


def run_section(verify_only, REPORT, log):
    section = "1.5 Configure Additional Process Hardening"

    # 1.5.1 Ensure ASLR is enabled
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
            "grep -Eq '^kernel.yama.ptrace_scope' " + SYSCTL_CONF + " && "
            "sed -i 's/^kernel.yama.ptrace_scope.*/kernel.yama.ptrace_scope = 1/' " + SYSCTL_CONF + " || "
            "echo 'kernel.yama.ptrace_scope = 1' >> " + SYSCTL_CONF
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
            "grep -Eq '^kernel.core_pattern' " + SYSCTL_CONF + " && "
            "sed -i 's|^kernel.core_pattern.*|kernel.core_pattern = |/bin/false|' " + SYSCTL_CONF + " || "
            "echo 'kernel.core_pattern = |/bin/false' >> " + SYSCTL_CONF
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
            "grep -Eq '^fs.suid_dumpable' " + SYSCTL_CONF + " && "
            "sed -i 's/^fs.suid_dumpable.*/fs.suid_dumpable = 0/' " + SYSCTL_CONF + " || "
            "echo 'fs.suid_dumpable = 0' >> " + SYSCTL_CONF
        ),
        verify_only, REPORT, log
    )

    # --- SSH Server Configuration ---
    # Permit root login via key only
    _run_check_fix(
        section,
        "Ensure SSH PermitRootLogin is 'without-password'",
        "grep -E '^\\s*PermitRootLogin\\s+without-password' /etc/ssh/sshd_config",
        (
            "sed -i.bak -E 's/^\\s*PermitRootLogin.*/PermitRootLogin without-password/' /etc/ssh/sshd_config && "
            "systemctl restart sshd"
        ),
        verify_only, REPORT, log
    )

    # Allow only wheel group
    _run_check_fix(
        section,
        "Ensure SSH AllowGroups includes 'wheel'",
        "grep -E '^\\s*AllowGroups.*wheel' /etc/ssh/sshd_config",
        (
            "if grep -q '^AllowGroups' /etc/ssh/sshd_config; then "
            "sed -i.bak -E 's/^AllowGroups.*/AllowGroups wheel/' /etc/ssh/sshd_config; "
            "else echo 'AllowGroups wheel' >> /etc/ssh/sshd_config; fi && "
            "systemctl restart sshd"
        ),
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
