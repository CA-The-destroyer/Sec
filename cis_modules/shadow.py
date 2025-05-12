# cis_modules/shadow.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.4 Shadow & Accounts"

    # 5.4.1.1 Ensure PASS_MAX_DAYS=90
    _run_check_fix(
        section,
        "Ensure PASS_MAX_DAYS=90 in /etc/login.defs",
        "grep -E '^\\s*PASS_MAX_DAYS\\s+90' /etc/login.defs",
        "sed -i '/^\\s*PASS_MAX_DAYS\\s\\+/d' /etc/login.defs && echo 'PASS_MAX_DAYS   90' >> /etc/login.defs",
        verify_only, REPORT, log
    )

    # 5.4.1.3 Ensure PASS_WARN_AGE=7
    _run_check_fix(
        section,
        "Ensure PASS_WARN_AGE=7 in /etc/login.defs",
        "grep -E '^\\s*PASS_WARN_AGE\\s+7' /etc/login.defs",
        "sed -i '/^\\s*PASS_WARN_AGE\\s\\+/d' /etc/login.defs && echo 'PASS_WARN_AGE   7' >> /etc/login.defs",
        verify_only, REPORT, log
    )

    # 5.4.1.5 Ensure INACTIVE=30
    _run_check_fix(
        section,
        "Ensure INACTIVE=30 in /etc/default/useradd",
        "grep -E '^\\s*INACTIVE\\s+30' /etc/default/useradd",
        "sed -i '/^\\s*INACTIVE\\s\\+/d' /etc/default/useradd && echo 'INACTIVE   30' >> /etc/default/useradd",
        verify_only, REPORT, log
    )

    # 5.4.2.5 Ensure root PATH integrity
    _run_check_fix(
        section,
        "Ensure root PATH contains only root-owned dirs",
        "bash -c 'for d in $(echo $PATH | tr \":\" \"\\n\"); do [ -d \"$d\" ] && [ ! -O \"$d\" ] && exit 1; done; exit 0'",
        None,
        verify_only, REPORT, log
    )

    # 5.4.2.6 Ensure root umask is 027
    _run_check_fix(
        section,
        "Ensure root umask is 027",
        "grep -E '^umask\\s+027' /root/.bashrc",
        "sed -i '/^umask\\s\\+/d' /root/.bashrc && echo 'umask 027' >> /root/.bashrc",
        verify_only, REPORT, log
    )

    # 5.4.2.7 Ensure system accounts have nologin shell
    for acct in ("sync", "shutdown", "halt"):
        _run_check_fix(
            section,
            f"Ensure {acct} shell is /usr/sbin/nologin",
            f"grep -E '^{acct}:[^:]*:[^:]*:[^:]*:[^:]*:/usr/sbin/nologin' /etc/passwd",
            f"usermod -s /usr/sbin/nologin {acct}",
            verify_only, REPORT, log
        )

    # 5.4.3.2 Ensure TMOUT=900
    _run_check_fix(
        section,
        "Ensure TMOUT=900 in /etc/profile",
        "grep -E '^TMOUT=900' /etc/profile",
        "sed -i '/^TMOUT=/d' /etc/profile && echo 'TMOUT=900' >> /etc/profile",
        verify_only, REPORT, log
    )

    # 5.4.3.3 Ensure UMASK=027
    _run_check_fix(
        section,
        "Ensure UMASK=027 in /etc/profile",
        "grep -E '^umask\\s+027' /etc/profile",
        "sed -i '/^umask\\s\\+/d' /etc/profile && echo 'umask 027' >> /etc/profile",
        verify_only, REPORT, log
    )