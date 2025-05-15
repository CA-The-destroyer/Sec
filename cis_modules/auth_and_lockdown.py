from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.5 Additional Process Hardening"

    # Ensure ptrace_scope is restricted (>=1)
    _run_check_fix(
        section,
        "Ensure ptrace_scope is restricted",
        "sysctl kernel.yama.ptrace_scope | grep -qE '^kernel.yama.ptrace_scope = [1-5]$'",
        "sysctl -w kernel.yama.ptrace_scope=1 && "
        "echo 'kernel.yama.ptrace_scope = 1' > /etc/sysctl.d/99-cis.conf && sysctl --system",
        verify_only, REPORT, log
    )

    # Ensure core dump backtraces are disabled
    _run_check_fix(
        section,
        "Ensure core dump backtraces are disabled",
        "sysctl kernel.core_pattern | grep -qv '^\\|'",
        "sed -i '/^kernel.core_pattern/d' /etc/sysctl.d/99-cis.conf && "
        "echo 'kernel.core_pattern = core' >> /etc/sysctl.d/99-cis.conf && sysctl --system",
        verify_only, REPORT, log
    )
