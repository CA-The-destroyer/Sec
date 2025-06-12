# cis_modules/shadow.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.4 User Accounts and Environment"

    # 5.4.1.1 Ensure password expiration is configured (90 days)
    _run_check_fix(
        section,
        "Ensure password expiration is set to 90 days",
        "grep -E '^PASS_MAX_DAYS\\s+90' /etc/login.defs",
        "sed -i.bak -E 's/^PASS_MAX_DAYS\\s+[0-9]+/PASS_MAX_DAYS   90/' /etc/login.defs",
        verify_only, REPORT, log
    )

    # 5.4.1.3 Ensure password expiration warning days is configured (7 days)
    _run_check_fix(
        section,
        "Ensure password expiration warning days is set to 7",
        "grep -E '^PASS_WARN_AGE\\s+7' /etc/login.defs",
        "sed -i.bak -E 's/^PASS_WARN_AGE\\s+[0-9]+/PASS_WARN_AGE   7/' /etc/login.defs",
        verify_only, REPORT, log
    )

    # 5.4.1.5 Ensure inactive password lock is configured
    cfg = "/etc/default/useradd"
    check_cmd = "grep -E '^INACTIVE=30' /etc/default/useradd"
    fix_cmd = (
        # If INACTIVE= line exists, change it; otherwise append
        "if grep -q '^INACTIVE=' " + cfg + "; then "
        "  sed -i.bak 's|^INACTIVE=.*|INACTIVE=30|' " + cfg + "; "
        "else "
        "  echo 'INACTIVE=30' >> " + cfg + "; "
        "fi"
    )

    _run_check_fix(
        section,
        "Ensure inactive password lock is configured",
        check_cmd,
        fix_cmd,
        verify_only, REPORT, log
    )

    # 5.4.2.5 Ensure root PATH integrity
    _run_check_fix(
        section,
        "Ensure root PATH integrity",
        "grep -E '^PATH=.+/s?bin' /root/.bash_profile",
        "echo 'export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' >> /root/.bash_profile",
        verify_only, REPORT, log
    )

    # 5.4.2.7 Ensure system accounts do not have a valid login shell
    #    (Exclude root explicitly so we do not lock out root)
    #    We target every user with UID < 1000 except “root”
    _run_check_fix(
        section,
        "Ensure system accounts shell is set to /sbin/nologin (except root)",
        # Only match UIDs <1000 and username ≠ root
        "awk -F: '$3 < 1000 && $1 != \"root\" {print $1 \":\" $7}' /etc/passwd | grep -q '/sbin/nologin'",
        (
            # For every system user (UID<1000, not root), set shell to /sbin/nologin
            "awk -F: '$3 < 1000 && $1 != \"root\" {print $1}' /etc/passwd "
            "| xargs -r -n1 usermod -s /sbin/nologin"
        ),
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
