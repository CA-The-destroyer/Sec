#!/usr/bin/env bash
# cis_verify.sh — Run manual CIS Level 1 checks (skips NFTables .2 & .3)

set -euo pipefail

GREEN="\033[32mPASS\033[0m"
RED="\033[31mFAIL\033[0m"

check() {
  desc="$1"; shift
  if eval "$*" &>/dev/null; then
    printf "%-60s %b\n" "$desc" "$GREEN"
  else
    printf "%-60s %b\n" "$desc" "$RED"
  fi
}

echo "=== 1.1 Filesystem ==="
check "Separate partition on /tmp"    "mount | grep -q ' on /tmp '"
check "nodev,nosuid,noexec on /tmp"   "findmnt --target /tmp -o OPTIONS -n | grep -qw nodev && findmnt --target /tmp -o OPTIONS -n | grep -qw nosuid && findmnt --target /tmp -o OPTIONS -n | grep -qw noexec"
check "Separate partition on /dev/shm" "mount | grep -q ' on /dev/shm '"
check "nodev,nosuid,noexec on /dev/shm" "findmnt --target /dev/shm -o OPTIONS -n | grep -qw nodev && findmnt --target /dev/shm -o OPTIONS -n | grep -qw nosuid && findmnt --target /dev/shm -o OPTIONS -n | grep -qw noexec"
check "Separate partition on /home"    "mount | grep -q ' on /home '"
check "nodev,nosuid on /home"          "findmnt --target /home -o OPTIONS -n | grep -qw nodev && findmnt --target /home -o OPTIONS -n | grep -qw nosuid"
check "Separate partition on /var"     "mount | grep -q ' on /var '"
check "nodev,nosuid on /var"           "findmnt --target /var -o OPTIONS -n | grep -qw nodev && findmnt --target /var -o OPTIONS -n | grep -qw nosuid"

echo
echo "=== 1.2 Packages & Updates ==="
check "gpgcheck globally activated"    "grep -Eq '^gpgcheck[[:space:]]*=1' /etc/yum.conf"
check "no pending yum updates"         "yum check-update >/dev/null; test \$? -eq 0"

echo
echo "=== 1.3 SELinux ==="
check "SELinux policy installed"       "rpm -q selinux-policy-targeted"
check "SELinux enforcing"              "getenforce | grep -q '^Enforcing'"
check "SELinux not disabled in grub"   "! grep -Eq 'selinux=0' /etc/default/grub"

echo
echo "=== 1.4 Bootloader ==="
check "bootloader password set"        "grep -q '^password_pbkdf2 ' /boot/grub2/user.cfg"
check "grub.cfg perms 600 root:root"   "stat -c '%a %U:%G' /boot/grub2/grub.cfg | grep -q '^600 root:root\$'"

echo
echo "=== 1.5 Process Hardening ==="
check "ASLR enabled"                   "sysctl kernel.randomize_va_space | grep -q '= 2'"
check "ptrace_scope=1"                 "sysctl kernel.yama.ptrace_scope | grep -q '= 1'"
check "core_pattern '|/bin/false'"     "sysctl kernel.core_pattern | grep -q '^|/bin/false'"
check "fs.suid_dumpable=0"             "sysctl fs.suid_dumpable | grep -q '= 0'"

echo
echo "=== 1.6 Crypto Policy ==="
check "policy not LEGACY"              "update-crypto-policies --show | grep -qv legacy"
check "SSH uses aes256-ctr only"       "grep -Eq '^Ciphers .*aes256-ctr' /etc/ssh/sshd_config"

echo
echo "=== 1.7 Banners ==="
check "/etc/motd exists"               "test -f /etc/motd"
check "/etc/issue exists"              "test -f /etc/issue"
check "/etc/issue.net exists"          "test -f /etc/issue.net"

echo
echo "=== 1.8 GDM ==="
check "GDM banner enabled"             "gsettings get org.gnome.login-screen banner-message-enable | grep -q true"
check "GDM user-list disabled"         "gsettings get org.gnome.login-screen disable-user-list | grep -q true"
check "GDM idle lock set"              "gsettings get org.gnome.desktop.session idle-delay | grep -Eq '[1-9]+'"
check "GDM autorun-never in custom.conf" "grep -Eq 'autorun-never' /etc/gdm/custom.conf"

echo
echo "=== 2.1 Server Services ==="
for svc in cups rpcbind avahi samba; do
  check "Service $svc disabled/not active" \
    "! systemctl is-enabled $svc 2>/dev/null && ! systemctl is-active $svc 2>/dev/null"
done

echo
echo "=== 2.2 Client Services ==="
check "telnet not installed"            "! rpm -q telnet"

echo
echo "=== 2.3 Chrony ==="
check "chrony installed"                "rpm -q chrony"
check "chronyd enabled+running"        "systemctl is-enabled chronyd && systemctl is-active chronyd"
check "chrony.conf has NTP server"     "grep -Eq '^(server|pool)\s+' /etc/chrony.conf"

echo
echo "=== 2.4 Cron & At ==="
check "crontab perms 644"              "stat -c '%a' /etc/crontab | grep -q '^644\$'"
for d in cron.hourly cron.daily cron.weekly cron.monthly cron.d; do
  check "$d perms 755"                 "stat -c '%a' /etc/$d | grep -q '^755\$'"
done
check "cron.allow root only"            "test -f /etc/cron.allow && grep -q '^root\$' /etc/cron.allow"
check "cron.deny empty/absent"          "! test -f /etc/cron.deny || grep -q '^$' /etc/cron.deny"
check "at.allow root only"              "test -f /etc/at.allow && grep -q '^root\$' /etc/at.allow"
check "at.deny empty/absent"            "! test -f /etc/at.deny || grep -q '^$' /etc/at.deny"

echo
echo "=== 3.3 Network Kernel Params ==="
check "ip_forward=0"                    "sysctl net.ipv4.ip_forward | grep -q '= 0'"
check "source routing disabled"         "sysctl net.ipv4.conf.all.accept_source_route | grep -q '= 0'"

echo
echo "=== 4.1 Firewall Utility ==="
check "exactly one fw tool"            "bash -c '([ -x \"$(command -v firewall-cmd)\" ] && ! command -v nft) || (! command -v firewall-cmd && [ -x \"$(command -v nft)\" ])'"

echo
echo "=== 4.2 Firewalld Loopback ==="
check "firewalld loopback ok"          "firewall-cmd --zone=trusted --query-interface=lo"

echo
echo "=== 5.1 SSHD Config ==="
check "sshd_config perms 600"          "stat -c '%a' /etc/ssh/sshd_config | grep -q '^600\$'"
check "PermitRootLogin no"             "grep -E '^PermitRootLogin no' /etc/ssh/sshd_config"
check "SSH MACs set"                   "grep -E '^MACs ' /etc/ssh/sshd_config"
check "ClientAlive settings"           "grep -E '^ClientAliveInterval ' /etc/ssh/sshd_config && grep -E '^ClientAliveCountMax ' /etc/ssh/sshd_config"

echo
echo "=== 5.2 Sudo & su ==="
check "sudo installed"                 "rpm -q sudo"
check "Defaults use_pty"               "grep -Eq '^Defaults\s+use_pty' /etc/sudoers"
check "pam_wheel for su"               "grep -Eq '^auth\s+required\s+pam_wheel.so' /etc/pam.d/su"

echo
echo "=== 5.3 PAM Packages & Config ==="
check "pam,authselect,pwquality pkgs"  "rpm -q pam authselect libpwquality"
check "pwquality minlen,difok,remember" "grep -E 'pam_pwquality.so.*minlen=14' /etc/pam.d/system-auth && grep -E 'difok=4' /etc/pam.d/system-auth && grep -E 'remember=5' /etc/pam.d/system-auth"
check "pam_unix nullok absent"         "! grep -E 'pam_unix.so.*nullok' /etc/pam.d/system-auth"

echo
echo "=== 5.4 Shadow & System Accounts ==="
check "PASS_MAX_DAYS=90"               "grep -E '^PASS_MAX_DAYS\s+90' /etc/login.defs"
check "PASS_WARN_AGE=7"                "grep -E '^PASS_WARN_AGE\s+7' /etc/login.defs"
check "INACTIVE=30"                    "grep -E '^INACTIVE\s+30' /etc/default/useradd"
check "root PATH in .bash_profile"     "grep -E '^export PATH=' /root/.bash_profile"
check "sys accs shell=/sbin/nologin"   "awk -F: '$3<1000&&$1!=\"root\"{print \$7}' /etc/passwd | grep -q '/sbin/nologin'"

echo
echo "=== 6.1 AIDE Integrity ==="
check "aide installed"                 "rpm -q aide"
check "aide.conf not empty"            "grep -Eq '/.*f' /etc/aide.conf"

echo
echo "=== 6.2 Journald & Rsyslog ==="
check "journald running"               "systemctl is-active systemd-journald >/dev/null"
check "ForwardToSyslog=no"             "grep -E '^ForwardToSyslog=no' /etc/systemd/journald.conf"
check "Compress set"                   "grep -E '^Compress=' /etc/systemd/journald.conf"
check "Storage set"                    "grep -E '^Storage=' /etc/systemd/journald.conf"
check "rsyslog running"                "systemctl is-active rsyslog >/dev/null"
check "rsyslog remote host"            "grep -Eq '@' /etc/rsyslog.conf"

echo
echo "=== 7.1 Maintenance ==="
check "no owner/group-less files"      "! find / -xdev \( -nouser -o -nogroup \) | grep -q ."

echo
echo "Done. (Skipped 4.3.2 & 4.3.3)"
