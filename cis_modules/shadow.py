# cis_modules/shadow.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.4 Shadow & Accounts"

    # 5.4.1.1 Ensure password expiration is configured
    _run_check_fix(
        section,
        "Ensure PASS_MAX_DAYS=90 in /etc/login.defs",
        "grep -E '^PASS_MAX_DAYS\\s+90' /etc/login.defs",
        "sed -i 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS   90/' /etc/login.defs",
        verify_only, REPORT, log
    )
    # 5.4.1.5 Ensure inactive lock is configured
    _run_check_fix(
        section,
        "Ensure INACTIVE=30 in /etc/default/useradd",
        "grep -E '^INACTIVE\\s+30' /etc/default/useradd",
        "sed -i 's/^INACTIVE.*/INACTIVE     30/' /etc/default/useradd",
        verify_only, REPORT, log
    )

    # 5.4.2.4 Ensure root account access is controlled (PermitRootLogin in SSH)
    _run_check_fix(
        section,
        "Ensure PermitRootLogin no in /etc/ssh/sshd_config",
        "grep -E '^\\s*PermitRootLogin no' /etc/ssh/sshd_config",
        "sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && systemctl restart sshd",
        verify_only, REPORT, log
    )
    # 5.4.2.6 Ensure root user umask is configured
    _run_check_fix(
        section,
        "Ensure root umask is 027",
        "grep -E '^umask 027' /root/.bashrc",
        "echo 'umask 027' >> /root/.bashrc",
        verify_only, REPORT, log
    )
    # 5.4.2.7 Ensure system accounts have nologin shell
    for acct in ("sync","shutdown","halt"):
        _run_check_fix(
            section,
            f"Ensure {acct} shell is /usr/sbin/nologin",
            f"getent passwd {acct} | grep -E ':{acct}:[^:]+:[^:]+:[^:]+:/usr/sbin/nologin'",
            f"usermod -s /usr/sbin/nologin {acct}",
            verify_only, REPORT, log
        )

    # 5.4.3.2 Ensure default user shell timeout is configured
    _run_check_fix(
        section,
        "Ensure TMOUT=900 in /etc/profile",
        "grep -E '^TMOUT=900' /etc/profile",
        "echo 'TMOUT=900' >> /etc/profile",
        verify_only, REPORT, log
    )
    # 5.4.3.3 Ensure default user umask is configured
    _run_check_fix(
        section,
        "Ensure UMASK=027 in /etc/profile",
        "grep -E '^umask 027' /etc/profile",
        "echo 'umask 027' >> /etc/profile",
        verify_only, REPORT, log
    )
