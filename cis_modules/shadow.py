# cis_modules/shadow.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.4 Shadow & Accounts"

    items = [
        ("PASS_MAX_DAYS", "90", "/etc/login.defs"),
        ("PASS_WARN_AGE", "7",  "/etc/login.defs"),
        ("INACTIVE",      "30", "/etc/default/useradd"),
    ]
    for name, val, f in items:
        _run_check_fix(
            section,
            f"Ensure {name}={val} in {f}",
            f"grep -E '^\\s*{name}\\s+{val}' {f}",
            f"sed -i '/^\\s*{name}\\s\\+/d' {f} && echo '{name}   {val}' >> {f}",
            verify_only, REPORT, log
        )

    # root umask
    _run_check_fix(
        section,
        "Ensure root umask is 027",
        "grep -E '^umask\\s+027' /root/.bashrc",
        "sed -i '/^umask\\s\\+/d' /root/.bashrc && echo 'umask 027' >> /root/.bashrc",
        verify_only, REPORT, log
    )

    # system accounts nologin
    for acct in ("sync","shutdown","halt"):
        _run_check_fix(
            section,
            f"Ensure {acct} shell is /usr/sbin/nologin",
            f"grep -E '^{acct}:[^:]*:/usr/sbin/nologin' /etc/passwd",
            f"usermod -s /usr/sbin/nologin {acct}",
            verify_only, REPORT, log
        )

    # TMOUT & UMASK in /etc/profile
    for var, val in [("TMOUT","900"), ("umask","027")]:
        _run_check_fix(
            section,
            f"Ensure {var}={val} in /etc/profile",
            f"grep -E '^{var}={val}' /etc/profile",
            f"sed -i '/^{var}=/d' /etc/profile && echo '{var}={val}' >> /etc/profile",
            verify_only, REPORT, log
        )
