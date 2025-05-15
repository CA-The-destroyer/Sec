# Updated cis_modules/services.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.1 Server Services"

    # Remove and disable print server (CUPS)
    _run_check_fix(
        section,
        "Ensure CUPS (print server) is not installed or running",
        "rpm -q cups && systemctl is-enabled --quiet cups.service && systemctl is-active --quiet cups.service",
        "dnf remove -y cups && systemctl disable --now cups.service",
        verify_only, REPORT, log
    )

    # Remove and disable rpcbind
    _run_check_fix(
        section,
        "Ensure rpcbind is not installed or running",
        "rpm -q rpcbind && systemctl is-enabled --quiet rpcbind.service && systemctl is-active --quiet rpcbind.service",
        "dnf remove -y rpcbind && systemctl disable --now rpcbind.service",
        verify_only, REPORT, log
    )

    # Remove and disable avahi-daemon
    _run_check_fix(
        section,
        "Ensure avahi-daemon is not installed or running",
        "rpm -q avahi-daemon && systemctl is-enabled --quiet avahi-daemon.service && systemctl is-active --quiet avahi-daemon.service",
        "dnf remove -y avahi-daemon && systemctl disable --now avahi-daemon.service",
        verify_only, REPORT, log
    )

    # Remove and disable Samba server (smb and nmb)
    for svc, pkg in [("smb", "samba"), ("nmb", "samba")]:
        _run_check_fix(
            section,
            f"Ensure {svc} service ({pkg}) is not installed or running",
            f"rpm -q {pkg} && systemctl is-enabled --quiet {svc}.service && systemctl is-active --quiet {svc}.service",
            f"dnf remove -y {pkg} && systemctl disable --now {svc}.service",
            verify_only, REPORT, log
        )

# Updated cis_modules/clients.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.2 Client Services"

    # Remove telnet client
    _run_check_fix(
        section,
        "Ensure telnet client is not installed",
        "rpm -q telnet",
        "dnf remove -y telnet",
        verify_only, REPORT, log
    )

# Updated cis_modules/chrony.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.3 Time Synchronization"

    # Ensure chrony installed, enabled, running; remove ntp if present
    _run_check_fix(
        section,
        "Ensure chrony is installed and running, ntp removed",
        "rpm -q chrony && systemctl is-enabled --quiet chronyd.service && systemctl is-active --quiet chronyd.service && ! rpm -q ntp",
        "dnf install -y chrony && systemctl enable --now chronyd.service && dnf remove -y ntp",
        verify_only, REPORT, log
    )

# Updated cis_modules/cron.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "2.4 Job Schedulers"

    # Cron allow only root
    _run_check_fix(
        section,
        "Ensure only root is in /etc/cron.allow",
        "grep -Ex '^root$' /etc/cron.allow && [[ $(wc -l < /etc/cron.allow) -eq 1 ]]",
        "echo 'root' > /etc/cron.allow && chmod 600 /etc/cron.allow && chown root:root /etc/cron.allow",
        verify_only, REPORT, log
    )

    # At allow only root
    _run_check_fix(
        section,
        "Ensure only root is in /etc/at.allow",
        "grep -Ex '^root$' /etc/at.allow && [[ $(wc -l < /etc/at.allow) -eq 1 ]]",
        "echo 'root' > /etc/at.allow && chmod 600 /etc/at.allow && chown root:root /etc/at.allow",
        verify_only, REPORT, log
    )

# Updated cis_modules/network.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "3.1 Network Devices"

    # Remove and disable bluetooth (bluez)
    _run_check_fix(
        section,
        "Ensure bluetooth (bluez) is not installed or running",
        "rpm -q bluez && systemctl is-enabled --quiet bluetooth.service && systemctl is-active --quiet bluetooth.service",
        "dnf remove -y bluez && systemctl disable --now bluetooth.service",
        verify_only, REPORT, log
    )

