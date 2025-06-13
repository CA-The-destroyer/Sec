#!/usr/bin/env python3
"""
additional_low_risk_chg.py — Remediate low-risk CIS findings (Python version of cis_lowrisk_fix.sh)
"""
import subprocess
import sys
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

def run(cmd, **kwargs):
    logging.info(f"→ Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, **kwargs)

# 2.2.10 Ensure CUPS is not installed or running
#     Remove package and disable service
def cups_removal():
    logging.info("0) Ensure CUPS (print server) is not installed or running…")
    # Disable and stop service if present
    try:
        run(["systemctl", "disable", "--now", "cups.service"])
    except subprocess.CalledProcessError:
        logging.info(" → cups.service already disabled or not present")
    # Remove package if installed
    try:
        subprocess.run(["rpm", "-q", "cups"], check=True, stdout=subprocess.DEVNULL)
        logging.info(" → Removing cups package")
        run(["dnf", "-y", "remove", "cups"])
    except subprocess.CalledProcessError:
        logging.info(" → cups package not installed")

# 2.2.1 Remove unnecessary packages
#    Packages: setroubleshoot-server, telnet, openldap-clients, ypbind, tftp
def remove_packages():
    logging.info("1) Remove unnecessary packages…")
    pkgs = [
        "setroubleshoot-server",
        "telnet",
        "openldap-clients",
        "ypbind",
        "tftp",
    ]
    for pkg in pkgs:
        try:
            subprocess.run(["rpm", "-q", pkg], check=True, stdout=subprocess.DEVNULL)
            logging.info(f" → Removing {pkg}")
            run(["dnf", "-y", "remove", pkg])
        except subprocess.CalledProcessError:
            logging.info(f" → {pkg} not installed")

# 2.2.2 Enforce core dump pattern
#    kernel.core_pattern = |/bin/false
def enforce_core_dump():
    logging.info("\n2) Enforce core dump pattern…")
    run(["sysctl", "-w", "kernel.core_pattern=|/bin/false"])
    conf_dir = Path("/etc/sysctl.d")
    conf_dir.mkdir(parents=True, exist_ok=True)
    conf_file = conf_dir / "99-cis.conf"
    line = "kernel.core_pattern = |/bin/false"
    text = conf_file.read_text() if conf_file.exists() else ""
    if "kernel.core_pattern" in text:
        run(["sed", "-i",
             "s@^kernel.core_pattern.*@kernel.core_pattern = |/bin/false@",
             str(conf_file)])
    else:
        conf_file.write_text(line + "\n")
    run(["sysctl", "--system"])

# 2.2.3 Disable GDM autorun
#    GDM custom.conf: Autorun-never=true
def gdm_autorun_never():
    logging.info("\n3) GDM autorun-never (no functional impact)…")
    gdm_conf = Path("/etc/gdm/custom.conf")
    text = gdm_conf.read_text() if gdm_conf.exists() else ""
    if "Autorun-never=true" not in text:
        with gdm_conf.open("a") as f:
            f.write("[daemon]\nAutorun-never=true\n")

# 2.2.4 Restrict cron & at access
#    cron.allow=root, cron.deny=empty; at.allow=root, at.deny=empty
def cron_at_restrictions():
    logging.info("\n4) Cron & at restrictions…")
    Path("/etc/cron.allow").write_text("root\n")
    Path("/etc/cron.allow").chmod(0o600)
    Path("/etc/cron.deny").write_text("")
    Path("/etc/cron.deny").chmod(0o644)
    Path("/etc/at.allow").write_text("root\n")
    Path("/etc/at.allow").chmod(0o600)
    Path("/etc/at.deny").write_text("")
    Path("/etc/at.deny").chmod(0o644)

# 2.2.5 Trust loopback interface
#    firewall-cmd or nft rule for lo accept
def trust_loopback():
    logging.info("\n5) Trust loopback interface…")
    try:
        run(["firewall-cmd", "--permanent", "--zone=trusted", "--add-interface=lo"])
        run(["firewall-cmd", "--reload"])
    except subprocess.CalledProcessError:
        result = subprocess.run(["nft", "list", "ruleset"], check=False, text=True, capture_output=True)
        if "iif lo accept" not in result.stdout:
            run(["nft", "insert", "rule", "inet", "filter", "input", "iif", "lo", "accept"] )

# 2.2.6 SSH hardening
#    KexAlgorithms and MaxStartups settings
def ssh_hardening():
    logging.info("\n6) SSH hardening—KexAlgorithms & MaxStartups…")
    ssh_conf = Path("/etc/ssh/sshd_config")
    text = ssh_conf.read_text()
    if "KexAlgorithms" in text:
        run(["sed", "-i.bak", "-E",
             "s|^KexAlgorithms.*|KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group14-sha1|",
             str(ssh_conf)])
    else:
        ssh_conf.write_text(text + "\nKexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group14-sha1\n")
    text = ssh_conf.read_text()
    if "MaxStartups" in text:
        run(["sed", "-i.bak", "-E",
             "s|^MaxStartups.*|MaxStartups 10:30:60|",
             str(ssh_conf)])
    else:
        ssh_conf.write_text(text + "\nMaxStartups 10:30:60\n")
    run(["systemctl", "reload", "sshd"])

# 2.2.7 PAM hardening
#    pam_wheel, remove nullok, pam_faillock scoping
def pam_hardening():
    logging.info("\n7) PAM – pam_wheel, pam_unix nullok, pam_faillock scoping…")
    su_file = Path("/etc/pam.d/su")
    text = su_file.read_text() if su_file.exists() else ""
    if "pam_wheel.so" not in text:
        su_file.write_text(text + "\nauth required pam_wheel.so use_uid\n")
    run(["sed", "-i.bak", "-E",
         "s@(pam_unix\.so[^ ]*) nullok@\1@",
         "/etc/pam.d/system-auth"])  
    for f in ["/etc/pam.d/system-auth", "/etc/pam.d/password-auth"]:
        run(["sed", "-i.bak", "-E",
             "/pam_faillock\.so preauth/ i auth [success=1 default=ignore] pam_succeed_if.so uid >= 1000 quiet",
             f])
        run(["sed", "-i.bak", "-E",
             "/pam_faillock\.so authfail/ i auth [success=1 default=ignore] pam_succeed_if.so uid >= 1000 quiet",
             f])

# 2.2.8 Inactive password lock
#    Set INACTIVE to 30 for non-root accounts
def inactive_lock():
    logging.info("\n8) Inactive password lock – non-root only…")
    useradd_file = Path("/etc/default/useradd")
    text = useradd_file.read_text() if useradd_file.exists() else ""
    if "INACTIVE   30" not in text:
        run(["sed", "-i.bak", "-E", "s|^INACTIVE\\s+[0-9]+|INACTIVE   30|", str(useradd_file)])

# 2.2.9 Cleanup orphan files
#    Remove files in /tmp and /var/tmp owned by no user or group
def cleanup_tmp():
    logging.info("\n9) Cleanup orphan files under /tmp and /var/tmp only…")
    run(["find", "/tmp", "/var/tmp", "-xdev",
         "( -nouser -o -nogroup )", "-exec", "rm", "-rf", "{}", "+"])


def main():
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
    logging.info("\nLow-risk remediation complete. Please re-verify with your validation script.")


if __name__ == "__main__":
    main()
