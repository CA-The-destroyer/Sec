# cis_modules/auth_and_lockdown.py
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.5 Process Hardening"
    # 1.5.1 Ensure address space layout randomization is enabled
    _run_check_fix(section,
                   "Ensure ASLR is enabled",
                   "sysctl kernel.randomize_va_space | grep -q '2'",
                   "sysctl -w kernel.randomize_va_space=2",
                   verify_only, REPORT, log)
    # 1.5.2 Ensure ptrace_scope is restricted
    _run_check_fix(section,
                   "Ensure ptrace_scope is restricted",
                   "sysctl kernel.yama.ptrace_scope | grep -q '1'",
                   "sysctl -w kernel.yama.ptrace_scope=1",
                   verify_only, REPORT, log)
    # 1.5.3 Ensure core dump backtraces are disabled
    _run_check_fix(section,
                   "Ensure core dump backtraces are disabled",
                   "grep -q 'fs.suid_dumpable = 0' /etc/sysctl.conf",
                   "echo 'fs.suid_dumpable = 0' >> /etc/sysctl.conf && sysctl -p",
                   verify_only, REPORT, log)
    # 1.5.4 Ensure core dump storage is disabled
    _run_check_fix(section,
                   "Ensure core dump storage is disabled",
                   "grep -q '^Storage=none' /etc/systemd/coredump.conf",
                   "sed -i 's/^#Storage=.*/Storage=none/' /etc/systemd/coredump.conf && systemctl daemon-reload",
                   verify_only, REPORT, log)