# cis_modules/process_hardening.py

import subprocess
from cis_modules import _run_check_fix

# Where we persist our sysctl overrides
SYSCTL_CONF = "/etc/sysctl.d/99-cis.conf"

def _persist_sysctl(key: str, value: str) -> str:
    """
    Build a shell snippet that will:
      - mkdir -p the conf dir
      - if the key exists, sed-replace it
      - otherwise append it
    """
    return (
        f"mkdir -p $(dirname {SYSCTL_CONF}) && "
        f"(grep -q '^{key}' {SYSCTL_CONF} && "
        f"sed -i 's|^{key}.*|{key} = {value}|' {SYSCTL_CONF} || "
        f"echo '{key} = {value}' >> {SYSCTL_CONF})"
    )

def run_section(verify_only, REPORT, log):
    section = "1.5 Process Hardening"

    # 1.5.1 Ensure address space layout randomization is enabled
    _run_check_fix(
        section,
        "Ensure address space layout randomization is enabled (ASLR=2)",
        "sysctl kernel.randomize_va_space | grep -q '= 2'",
        "sysctl -w kernel.randomize_va_space=2 && " + _persist_sysctl("kernel.randomize_va_space","2"),
        verify_only, REPORT, log
    )

    # 1.5.2 Ensure ptrace_scope is restricted
    _run_check_fix(
        section,
        "Ensure ptrace_scope is restricted (kernel.yama.ptrace_scope=1)",
        "sysctl kernel.yama.ptrace_scope | grep -q '= 1'",
        "sysctl -w kernel.yama.ptrace_scope=1 && " + _persist_sysctl("kernel.yama.ptrace_scope","1"),
        verify_only, REPORT, log
    )

    # 1.5.3 Ensure core dump backtraces are disabled
    _run_check_fix(
        section,
        "Ensure core dump backtraces are disabled (core_pattern = |/bin/false)",
        "sysctl kernel.core_pattern | grep -q '^|/bin/false'",
        "sysctl -w kernel.core_pattern='|/bin/false' && " + _persist_sysctl("kernel.core_pattern","|/bin/false"),
        verify_only, REPORT, log
    )

    # 1.5.4 Ensure suid_dumpable is disabled (fs.suid_dumpable=0)
    _run_check_fix(
        section,
        "Ensure suid_dumpable is disabled (fs.suid_dumpable=0)",
        "sysctl fs.suid_dumpable | grep -q '= 0'",
        "sysctl -w fs.suid_dumpable=0 && " + _persist_sysctl("fs.suid_dumpable","0"),
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
