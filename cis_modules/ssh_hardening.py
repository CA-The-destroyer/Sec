# cis_modules/ssh_hardening.py

import subprocess
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.1 SSH Hardening"

    # 5.1.20 Ensure sshd PermitRootLogin is disabled
    _run_check_fix(
        section,
        "Ensure sshd PermitRootLogin is disabled",
        "grep -E '^\\s*PermitRootLogin\\s+no' /etc/ssh/sshd_config",
        "sed -i 's/^\\s*#*\\s*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && systemctl reload sshd",
        verify_only, REPORT, log
    )

    # 5.1.4 Ensure sshd Ciphers are configured
    _run_check_fix(
        section,
        "Ensure sshd Ciphers are configured",
        "grep -E '^\\s*Ciphers\\s+' /etc/ssh/sshd_config",
        "sed -i 's/^\\s*#*\\s*Ciphers.*/Ciphers aes256-ctr,aes192-ctr,aes128-ctr/' /etc/ssh/sshd_config && systemctl reload sshd",
        verify_only, REPORT, log
    )

    # 5.1.5 Ensure sshd KexAlgorithms is configured
    _run_check_fix(
        section,
        "Ensure sshd KexAlgorithms are configured",
        "grep -E '^\\s*KexAlgorithms\\s+' /etc/ssh/sshd_config",
        "sed -i 's/^\\s*#*\\s*KexAlgorithms.*/KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group14-sha1/' /etc/ssh/sshd_config && systemctl reload sshd",
        verify_only, REPORT, log
    )

    # 5.1.6 Ensure sshd MACs are configured
    _run_check_fix(
        section,
        "Ensure sshd MACs are configured",
        "grep -E '^\\s*MACs\\s+' /etc/ssh/sshd_config",
        "sed -i 's/^\\s*#*\\s*MACs.*/MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com/' /etc/ssh/sshd_config && systemctl reload sshd",
        verify_only, REPORT, log
    )

    # 5.1.9 Ensure sshd ClientAliveInterval and ClientAliveCountMax are configured
    _run_check_fix(
        section,
        "Ensure sshd ClientAliveInterval and ClientAliveCountMax are configured",
        "grep -E '^\\s*ClientAliveInterval\\s+' /etc/ssh/sshd_config && grep -E '^\\s*ClientAliveCountMax\\s+' /etc/ssh/sshd_config",
        "grep -E '^\\s*ClientAliveInterval' /etc/ssh/sshd_config || echo 'ClientAliveInterval 300' >> /etc/ssh/sshd_config; "
        "grep -E '^\\s*ClientAliveCountMax' /etc/ssh/sshd_config || echo 'ClientAliveCountMax 0' >> /etc/ssh/sshd_config; "
        "systemctl reload sshd",
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
