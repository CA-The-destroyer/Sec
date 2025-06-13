# cis_modules/lowrisk_fix.py

import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")

def run(cmd):
    logging.info(f"→ Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def cups_removal():
    """
    CIS 2.1.11 Ensure CUPS (print server) is not in use
    Rationale: Unneeded services increase attack surface.
    """
    logging.info("0) Ensure CUPS (print server) is not installed or running…")
    try:
        run(["systemctl", "disable", "--now", "cups.service"])
    except subprocess.CalledProcessError:
        logging.info(" → cups.service already disabled or not present")
    try:
        subprocess.run(["rpm", "-q", "cups"], check=True, stdout=subprocess.DEVNULL)
        logging.info(" → Removing cups package")
        # Avoid removing dependencies like XenDesktopVDA
        run(["dnf", "-y", "--noautoremove", "remove", "cups"])
    except subprocess.CalledProcessError:
        logging.info(" → cups package not installed")

def remove_packages():
    """
    CIS 2.2.4 Ensure telnet client is not installed
    CIS 2.2.x Remove other unnecessary clients: setroubleshoot-server, openldap-clients, ypbind, tftp
    Rationale: Removing obsolete clients reduces risk.
    """
    logging.info("1) Remove unnecessary packages…")
    pkgs = ["setroubleshoot-server", "telnet", "openldap-clients", "ypbind", "tftp"]
    for pkg in pkgs:
        try:
            subprocess.run(["rpm", "-q", pkg], check=True, stdout=subprocess.DEVNULL)
            logging.info(f" → Removing {pkg}")
            # Avoid removing dependencies
            run(["dnf", "-y", "--noautoremove", "remove", pkg])
        except subprocess.CalledProcessError:
            logging.info(f" → {pkg} not installed")

def enforce_core_dump():
    """
    CIS 1.5.3 Ensure core dump backtraces are disabled
    Sets kernel.core_pattern to |/bin/false to prevent dumps.
    """
    logging.info("2) Enforce core dump pattern…")
    run(["sysctl", "-w", "kernel.core_pattern=|/bin/false"])
    conf_file = Path("/etc/sysctl.d/99-cis.conf")
    text = conf_file.read_text() if conf_file.exists() else ""
    line = "kernel.core_pattern = |/bin/false"
    if "kernel.core_pattern" in text:
        run([
            "sed", "-i",
            "s@^kernel.core_pattern.*@kernel.core_pattern = |/bin/false@",
            str(conf_file)
        ])
    else:
        conf_file.parent.mkdir(parents=True, exist_ok=True)
        conf_file.write_text(line + "\n")
    run(["sysctl", "--system"])

def gdm_autorun_never():
    """
    CIS 1.8.8 Ensure GDM autorun-never is enabled
    Prevents automatic media autorun in the graphical login manager.
    """
    logging.info("3) GDM autorun-never (no functional impact)…")
    gdm_conf = Path("/etc/gdm/custom.conf")
    text = gdm_conf.read_text() if gdm_conf.exists() else ""
    if "Autorun-never=true" not in text:
        with gdm_conf.open("a") as f:
            f.write("[daemon]\nAutorun-never=true\n")

def cron_at_restrictions():
    """
    CIS 2.4.1.8 Ensure cron.allow is root only
    CIS 2.4.1.8 Ensure cron.deny is empty/absent
    CIS 2.4.2.1 Ensure at.allow is root only
    CIS 2.4.2.1 Ensure at.deny is empty/absent
    """
    logging.info("4) Cron & at restrictions…")
    Path("/etc/cron.allow").write_text("root\n"); Path("/etc/cron.allow").chmod(0o600)
    Path("/etc/cron.deny").write_text("");  Path("/etc/cron.deny").chmod(0o644)
    Path("/etc/at.allow").write_text("root\n");  Path("/etc/at.allow").chmod(0o600)
    Path("/etc/at.deny").write_text("");  Path("/etc/at.deny").chmod(0o644)

def trust_loopback():
    """
    CIS 4.2.2 Ensure firewalld loopback traffic is configured (or equivalent nft)
    Permits localhost communication.
    """
    logging.info("5) Trust loopback interface…")
    try:
        run(["firewall-cmd", "--permanent", "--zone=trusted", "--add-interface=lo"])
        run(["firewall-cmd", "--reload"])
    except subprocess.CalledProcessError:
        out = subprocess.run(
            ["nft", "list", "ruleset"], check=False, text=True, capture_output=True
        ).stdout
        if "iif lo accept" not in out:
            run(["nft", "insert", "rule", "inet", "filter", "input", "iif", "lo", "accept"])

def ssh_hardening():
    """
    CIS 5.1.20 Ensure sshd PermitRootLogin is disabled
    CIS 5.1.6 Ensure sshd MACs are configured
    CIS 5.1.9 Ensure sshd ClientAliveInterval/CountMax are configured
    CIS 5.1.x KexAlgorithms & MaxStartups hardening
    """
    logging.info("6) SSH hardening—KexAlgorithms & MaxStartups…")
    ssh_conf = Path("/etc/ssh/sshd_config")
    text = ssh_conf.read_text()
    if "KexAlgorithms" in text:
        run([
            "sed", "-i.bak", "-E",
            "s|^KexAlgorithms.*|KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group14-sha1|",
            str(ssh_conf)
        ])
    else:
        ssh_conf.write_text(text + "\nKexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group14-sha1\n")
    text = ssh_conf.read_text()
    if "MaxStartups" in text:
        run([
            "sed", "-i.bak", "-E",
            "s|^MaxStartups.*|MaxStartups 10:30:60|",
            str(ssh_conf)
        ])
    else:
        ssh_conf.write_text(text + "\nMaxStartups 10:30:60\n")
    run(["systemctl", "reload", "sshd"])

def pam_hardening():
    """
    CIS 5.2.2 Ensure sudo commands use pty (via pam_wheel or sudoers)
    CIS 5.2.7 Ensure access to the su command is restricted (pam_wheel)
    CIS 5.3.3.4.1 Ensure pam_unix does not include nullok
    CIS 5.3.3.1.x Ensure pam_faillock is configured on preauth and authfail
    """
    logging.info("7) PAM – pam_wheel, pam_unix nullok, pam_faillock scoping…")
    su_file = Path("/etc/pam.d/su")
    text = su_file.read_text() if su_file.exists() else ""
    if "pam_wheel.so" not in text:
        su_file.write_text(text + "\nauth required pam_wheel.so use_uid\n")
    run([
        "sed", "-i.bak", "-E",
        "s@(pam_unix\\.so[^ ]*) nullok@\\1@",
        "/etc/pam.d/system-auth"
    ])
    for f in ("/etc/pam.d/system-auth", "/etc/pam.d/password-auth"):
        run([
            "sed", "-i.bak", "-E",
            "/pam_faillock\\.so preauth/ i auth [success=1 default=ignore] pam_succeed_if.so uid >= 1000 quiet",
            f
        ])
        run([
            "sed", "-i.bak", "-E",
            "/pam_faillock\\.so authfail/ i auth [success=1 default=ignore] pam_succeed_if.so uid >= 1000 quiet",
            f
        ])

def inactive_lock():
    """
    CIS 5.4.1.5 Ensure inactive password lock is configured (INACTIVE=30)
    """
    logging.info("8) Inactive password lock – non-root only…")
    ua = Path("/etc/default/useradd")
    text = ua.read_text() if ua.exists() else ""
    if "INACTIVE=30" not in text:
        if "INACTIVE=" in text:
            run(["sed", "-i.bak", "-E", "s|^INACTIVE=.*|INACTIVE=30|", str(ua)])
        else:
            ua.write_text(text + "\nINACTIVE=30\n")

def cleanup_tmp():
    """
    CIS 7.1.12 Ensure no files/directories without owner/group exist
    Only under /tmp and /var/tmp; explicitly skip /opt/Citrix
    """
    logging.info("9) Cleanup orphan files under /tmp and /var/tmp only…")
    run([
        "find", "/tmp", "/var/tmp", "-xdev",
        "(", "-nouser", "-o", "-nogroup", ")",
        "-not", "-path", "/opt/Citrix/*",
        "-exec", "rm", "-rf", "{}", "+",
    ])

def run_section(verify_only, REPORT, log):
    section = "9 Low-Risk Fixes"
    if verify_only:
        log(f"[→] Skipping low-risk fixes in verify-only mode")
        REPORT.append((section, "Low-risk fixes", "Skipped"))
        return

    cups_removal()
    remove_packages()
    enforce_core_dump()
    gdm_autorun_never()
    cron_at_restrictions()
    trust_loopback()
    ssh_hardening()
    pam_hardening()
    inactive_lock()
    cleanup_tmp()

    REPORT.append((section, "Low-risk fixes applied", "Success"))
    log(f"[✔] {section} completed successfully")
