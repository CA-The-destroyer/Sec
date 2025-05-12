# cis_modules/sshd.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.1 SSH"

    # 5.1.1 Ensure /etc/ssh/sshd_config permissions are 600 root:root
    _run_check_fix(
        section,
        "Ensure /etc/ssh/sshd_config permissions are 600 root:root",
        "stat -c '%a %U:%G' /etc/ssh/sshd_config | grep -q '^600 root:root$'",
        "chmod 600 /etc/ssh/sshd_config && chown root:root /etc/ssh/sshd_config",
        verify_only, REPORT, log
    )

    # 5.1.2 Ensure SSH host private keys are 600 root:root
    _run_check_fix(
        section,
        "Ensure SSH host private keys are 600 root:root",
        "bash -c \"find /etc/ssh -type f -name 'ssh_host_*_key' \\( ! -perm 600 -o ! -user root -o ! -group root \\) | grep -q . && exit 1 || exit 0\"",
        "find /etc/ssh -type f -name 'ssh_host_*_key' -exec chmod 600 {} \\; -exec chown root:root {} \\;",
        verify_only, REPORT, log
    )

    # 5.1.6 Ensure sshd MACs are set to hmac-sha2-512,hmac-sha2-256
    _run_check_fix(
        section,
        "Ensure sshd MACs are hmac-sha2-512,hmac-sha2-256",
        "grep -E '^\\s*MACs\\s+' /etc/ssh/sshd_config | grep -q 'hmac-sha2-512,hmac-sha2-256'",
        "sed -i '/^\\s*MACs\\s\\+/d' /etc/ssh/sshd_config && echo 'MACs hmac-sha2-512,hmac-sha2-256' >> /etc/ssh/sshd_config",
        verify_only, REPORT, log
    )

    # 5.1.9 Ensure ClientAliveInterval=300 and ClientAliveCountMax=0
    _run_check_fix(
        section,
        "Ensure ClientAliveInterval=300 and ClientAliveCountMax=0",
        "grep -E '^\\s*ClientAliveInterval\\s+300' /etc/ssh/sshd_config && grep -E '^\\s*ClientAliveCountMax\\s+0' /etc/ssh/sshd_config",
        "sed -i '/^ClientAliveInterval/d' /etc/ssh/sshd_config && echo 'ClientAliveInterval 300' >> /etc/ssh/sshd_config; "
        "sed -i '/^ClientAliveCountMax/d' /etc/ssh/sshd_config && echo 'ClientAliveCountMax 0' >> /etc/ssh/sshd_config",
        verify_only, REPORT, log
    )

    # 5.1.17 Ensure MaxStartups=10:30:60
    _run_check_fix(
        section,
        "Ensure MaxStartups is 10:30:60",
        "grep -E '^\\s*MaxStartups\\s+10:30:60' /etc/ssh/sshd_config",
        "sed -i '/^MaxStartups/d' /etc/ssh/sshd_config && echo 'MaxStartups 10:30:60' >> /etc/ssh/sshd_config",
        verify_only, REPORT, log
    )

    # 5.1.20 Ensure sshd PermitRootLogin is disabled
    _run_check_fix(
        section,
        "Ensure PermitRootLogin no",
        "grep -E '^\\s*PermitRootLogin\\s+no' /etc/ssh/sshd_config",
        "sed -i '/^\\s*PermitRootLogin\\s\\+/d' /etc/ssh/sshd_config && echo 'PermitRootLogin no' >> /etc/ssh/sshd_config",
        verify_only, REPORT, log
    )
