# cis_modules/sshd.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.1 SSH"

    # === ORIGINAL IMPLEMENTATION ===
    _run_check_fix(
        section, "Ensure /etc/ssh/sshd_config perms",
        "stat -c '%a %U:%G' /etc/ssh/sshd_config | grep -q '^600 root:root$'",
        "chmod 600 /etc/ssh/sshd_config && chown root:root /etc/ssh/sshd_config",
        verify_only, REPORT, log
    )
    _run_check_fix(
        section, "Ensure SSH host keys perms",
        "bash -c \"find /etc/ssh -name 'ssh_host_*_key' ! -perm 600 | grep -q . && exit 1 || exit 0\"",
        "find /etc/ssh -name 'ssh_host_*_key' -exec chmod 600 {} \\; -exec chown root:root {} \\;",
        verify_only, REPORT, log
    )
    _run_check_fix(
        section, "Ensure sshd PermitRootLogin no",
        "grep -E '^\\s*PermitRootLogin\\s+no' /etc/ssh/sshd_config",
        "sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && systemctl reload sshd",
        verify_only, REPORT, log
    )
    _run_check_fix(
        section, "Ensure sshd MACs are set",
        "grep -E '^\\s*MACs\\s+' /etc/ssh/sshd_config",
        "sed -i '/^#\\?MACs/d' /etc/ssh/sshd_config && echo 'MACs hmac-sha2-512,hmac-sha2-256' >> /etc/ssh/sshd_config && systemctl reload sshd",
        verify_only, REPORT, log
    )
    _run_check_fix(
        section, "Ensure sshd ClientAliveInterval & CountMax",
        "grep -E '^ClientAliveInterval\\s+' /etc/ssh/sshd_config",
        "sed -i '/^ClientAliveInterval/d' /etc/ssh/sshd_config && echo 'ClientAliveInterval 300' >> /etc/ssh/sshd_config && echo 'ClientAliveCountMax 0' >> /etc/ssh/sshd_config && systemctl reload sshd",
        verify_only, REPORT, log
    )
    _run_check_fix(
        section, "Ensure sshd MaxStartups configured",
        "grep -E '^MaxStartups\\s+' /etc/ssh/sshd_config",
        "sed -i '/^MaxStartups/d' /etc/ssh/sshd_config && echo 'MaxStartups 10:30:60' >> /etc/ssh/sshd_config && systemctl reload sshd",
        verify_only, REPORT, log
    )

    # === UPDATED IMPLEMENTATION ===
    # (all sed commands already remove prior lines before appending)
