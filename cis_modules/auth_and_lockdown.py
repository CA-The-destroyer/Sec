# cis_modules/auth_and_lockdown.py

import subprocess
from cis_modules import _run_check_fix

SSHD_CONFIG = "/etc/ssh/sshd_config"

def _ensure_sshd_setting(key, value, verify_only, REPORT, log, section):
    """
    Ensure SSHD config directive key is set to value. If present (commented or not), replace;
    otherwise append it. Then restart sshd.
    """
    check_cmd = f"grep -E '^{key}\\s+{value}' {SSHD_CONFIG}"
    fix_cmd = (
        f"grep -Eq '^#?\\s*{key}\\b' {SSHD_CONFIG} "
        f"&& sed -i.bak -E 's|^#?\\s*{key}.*|{key} {value}|' {SSHD_CONFIG} "
        f"|| echo '{key} {value}' >> {SSHD_CONFIG} && systemctl restart sshd"
    )
    _run_check_fix(section, f"Ensure {key} is set to {value}", check_cmd, fix_cmd, verify_only, REPORT, log)

def run_section(verify_only, REPORT, log):
    section = "5.1-5.2 SSH & Lockdown"

    # 5.1.20 Ensure sshd PermitRootLogin is disabled
    _ensure_sshd_setting("PermitRootLogin", "no", verify_only, REPORT, log, section)

    # 5.1.7 Ensure sshd AllowGroups wheel is set
    _ensure_sshd_setting("AllowGroups", "wheel", verify_only, REPORT, log, section)

    # 5.1.1 Ensure permissions on /etc/ssh/sshd_config are 600
    _run_check_fix(
        section,
        "Ensure permissions on /etc/ssh/sshd_config are 600",
        "stat -c '%a' /etc/ssh/sshd_config | grep -q '^600$'",
        "chmod 600 /etc/ssh/sshd_config",
        verify_only, REPORT, log
    )

    # 5.1.2 Ensure permissions on SSH private host key files are 600
    _run_check_fix(
        section,
        "Ensure permissions on SSH private host keys are 600",
        "find /etc/ssh -type f -name 'ssh_host_*_key' -exec stat -c '%a' {} \\; | grep -q '^600$'",
        "find /etc/ssh -type f -name 'ssh_host_*_key' -exec chmod 600 {} \\;",
        verify_only, REPORT, log
    )

    # 5.1.6 Ensure sshd MACs are configured (disable weak MACs)
    # Example of strong-only MACs
    strong_macs = "hmac-sha2-512,hmac-sha2-256"
    _run_check_fix(
        section,
        "Ensure sshd MACs are configured to strong algorithms",
        f"grep -E '^MACs\\s+{strong_macs}' {SSHD_CONFIG}",
        (
            f"grep -Eq '^#?MACs' {SSHD_CONFIG} "
            f"&& sed -i.bak -E 's|^#?MACs.*|MACs {strong_macs}|' {SSHD_CONFIG} "
            f"|| echo 'MACs {strong_macs}' >> {SSHD_CONFIG} && systemctl restart sshd"
        ),
        verify_only, REPORT, log
    )

    # 5.1.9 Ensure sshd ClientAliveInterval is 300 and ClientAliveCountMax is 0
    _run_check_fix(
        section,
        "Ensure sshd ClientAliveInterval is 300",
        "grep -E '^ClientAliveInterval\\s+300' /etc/ssh/sshd_config",
        (
            "grep -Eq '^#?ClientAliveInterval' /etc/ssh/sshd_config "
            "&& sed -i.bak -E 's|^#?ClientAliveInterval.*|ClientAliveInterval 300|' /etc/ssh/sshd_config "
            "|| echo 'ClientAliveInterval 300' >> /etc/ssh/sshd_config && systemctl restart sshd"
        ),
        verify_only, REPORT, log
    )
    _run_check_fix(
        section,
        "Ensure sshd ClientAliveCountMax is 0",
        "grep -E '^ClientAliveCountMax\\s+0' /etc/ssh/sshd_config",
        (
            "grep -Eq '^#?ClientAliveCountMax' /etc/ssh/sshd_config "
            "&& sed -i.bak -E 's|^#?ClientAliveCountMax.*|ClientAliveCountMax 0|' /etc/ssh/sshd_config "
            "|| echo 'ClientAliveCountMax 0' >> /etc/ssh/sshd_config && systemctl restart sshd"
        ),
        verify_only, REPORT, log
    )

    # 5.1.17 Ensure sshd MaxStartups is configured (e.g., 10:30:60)
    _run_check_fix(
        section,
        "Ensure sshd MaxStartups is set to 10:30:60",
        "grep -E '^MaxStartups\\s+10:30:60' /etc/ssh/sshd_config",
        (
            "grep -Eq '^#?MaxStartups' /etc/ssh/sshd_config "
            "&& sed -i.bak -E 's|^#?MaxStartups.*|MaxStartups 10:30:60|' /etc/ssh/sshd_config "
            "|| echo 'MaxStartups 10:30:60' >> /etc/ssh/sshd_config && systemctl restart sshd"
        ),
        verify_only, REPORT, log
    )

    # 5.2.2 Ensure sudo commands use pty
    _run_check_fix(
        section,
        "Ensure sudo commands use pty",
        "grep -E '^Defaults\\s+use_pty' /etc/sudoers",
        "echo 'Defaults use_pty' >> /etc/sudoers",
        verify_only, REPORT, log
    )

    # 5.2.7 Ensure access to the su command is restricted
    #  - create wheel group if not exists, add current user, update /etc/pam.d/su
    _run_check_fix(
        section,
        "Ensure access to su is restricted to wheel group",
        "grep -E '^auth\\s+required\\s+pam_wheel.so use_uid' /etc/pam.d/su",
        (
            "groupadd -f wheel && "
            "user=$(whoami) && usermod -aG wheel $user && "
            "echo 'auth required pam_wheel.so use_uid' >> /etc/pam.d/su"
        ),
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
