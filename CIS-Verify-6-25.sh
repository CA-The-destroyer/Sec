#!/usr/bin/env bash
# cis_verify.sh — CIS Level 1 Manual Verifier with full control coverage and CSV output

set -o pipefail

CSV="cis_findings.csv"
echo "Section,Description,Status,ExitCode,Value" > "$CSV"

# Color helpers
pass() { printf "\033[32mPASS\033[0m"; }
fail() { printf "\033[31mFAIL\033[0m"; }

# run_check <section> <description> <timeout_secs> <command…>
run_check() {
  section="$1"; shift
  desc="$1";    shift
  to="$1";      shift

  if [ "$to" -gt 0 ]; then
    output=$( timeout "${to}s" bash -c "$*" 2>&1 )
    rc=$?
  else
    output=$( "$@" 2>&1 ) || rc=$?
    rc=${rc:-0}
  fi

  if [ "$rc" -eq 0 ]; then status="$(pass)"; else status="$(fail)"; fi
  val=${output//$'\n'/ }
  printf "%-8s %-50s %s (exit %d, \"%s\")\n" "$section" "$desc" "$status" "$rc" "$val"
  esc=${val//\"/\\\"}
  echo "\"$section\",\"$desc\",\"$status\",$rc,\"$esc\"" >> "$CSV"
}

echo "=== CIS Level 1 Manual Checks ==="

# 1.1 Filesystem
run_check "1.1" "/tmp separate"           5 "mount | grep -q ' on /tmp '"
run_check "1.1" "/tmp opts"               5 "findmnt --target /tmp -o OPTIONS -n"
run_check "1.1" "/dev/shm separate"       5 "mount | grep -q ' on /dev/shm '"
run_check "1.1" "/dev/shm opts"           5 "findmnt --target /dev/shm -o OPTIONS -n"
run_check "1.1" "/var/tmp separate"       5 "mount | grep -q ' on /var/tmp '"
run_check "1.1" "/var/tmp opts"           5 "findmnt --target /var/tmp -o OPTIONS -n"
run_check "1.1" "/home separate"          5 "mount | grep -q ' on /home '"
run_check "1.1" "/home opts"              5 "findmnt --target /home -o OPTIONS -n"
run_check "1.1" "/var separate"           5 "mount | grep -q ' on /var '"
run_check "1.1" "/var opts"               5 "findmnt --target /var -o OPTIONS -n"
run_check "1.1" "/var/log separate"       5 "mount | grep -q ' on /var/log '"
run_check "1.1" "/var/log opts"           5 "findmnt --target /var/log -o OPTIONS -n"
run_check "1.1" "/var/log/audit sep"      5 "mount | grep -q ' on /var/log/audit '"
run_check "1.1" "/var/log/audit opts"     5 "findmnt --target /var/log/audit -o OPTIONS -n"

# 1.2 Packages & Updates
run_check "1.2" "gpgcheck=1"              5 "grep -Eq '^gpgcheck[[:space:]]*=1' /etc/yum.conf"
# yum check
timeout 30s bash -c "yum -q --assumeno check-update >/dev/null 2>&1"; rc=$?
if   [ $rc -eq 0 ]; then status="$(pass)"; val="no updates"
elif [ $rc -eq 100 ]; then status="$(fail)"; val="updates available"
else status="$(fail)"; val="error $rc"; fi
printf "%-8s %-50s %s (exit %d, \"%s\")\n" "1.2" "updates pending" "$status" "$rc" "$val"
echo "\"1.2\",\"updates pending\",\"$status\",$rc,\"$val\"" >> "$CSV"

# 1.3 SELinux
run_check "1.3" "SELinux policy pkg"      5 "rpm -q selinux-policy-targeted"
run_check "1.3" "getenforce"              5 "getenforce | grep -q '^Enforcing'"
run_check "1.3" "not disabled in GRUB"    5 "! grep -Eq 'selinux=0' /etc/default/grub"
run_check "1.3" "SETroubleshoot removed"   5 "! rpm -q setroubleshoot-server"

# 1.4 Bootloader
run_check "1.4" "grub user.cfg pw"         5 "grep -q '^password_pbkdf2 ' /boot/grub2/user.cfg"
run_check "1.4" "grub.cfg perms"          5 "stat -c '%a %U:%G' /boot/grub2/grub.cfg"

# 1.5 Process Hardening
run_check "1.5" "ASLR=2"                  5 "sysctl kernel.randomize_va_space | grep -q '= 2'"
run_check "1.5" "ptrace_scope=1"          5 "sysctl kernel.yama.ptrace_scope | grep -q '= 1'"
run_check "1.5" "core_pattern"            5 "sysctl kernel.core_pattern | grep -q '^|/bin/false'"
run_check "1.5" "suid_dumpable=0"         5 "sysctl fs.suid_dumpable | grep -q '= 0'"

# 1.6 Crypto Policy
run_check "1.6" "policy not LEGACY"       5 "update-crypto-policies --show | grep -qv legacy"
run_check "1.6" "SSH aes256-ctr"          5 "grep -Eq '^Ciphers .*aes256-ctr' /etc/ssh/sshd_config"

# 1.7 Banners
run_check "1.7" "/etc/motd exists"        5 "test -f /etc/motd"
run_check "1.7" "/etc/issue exists"       5 "test -f /etc/issue"
run_check "1.7" "/etc/issue.net exists"   5 "test -f /etc/issue.net"

# 1.8 GDM
run_check "1.8" "GDM banner"              5 "gsettings get org.gnome.login-screen banner-message-enable"
run_check "1.8" "GDM user-list"           5 "gsettings get org.gnome.login-screen disable-user-list"
run_check "1.8" "GDM idle-delay"          5 "gsettings get org.gnome.desktop.session idle-delay"
run_check "1.8" "GDM autorun-never"       5 "grep -Eq 'autorun-never' /etc/gdm/custom.conf"

# 2.1 Server Services
for svc in cups rpcbind avahi samba; do
  run_check "2.1" "$svc disabled"        5 "! systemctl is-enabled $svc && ! systemctl is-active $svc"
done

# 2.2 Client Services
run_check "2.2" "telnet absent"          5 "! rpm -q telnet"
run_check "2.2" "ldap absent"            5 "! rpm -q openldap-clients"
run_check "2.2" "nis absent"             5 "! rpm -q ypbind"
run_check "2.2" "tftp absent"            5 "! rpm -q tftp"

# 2.3 Chrony
run_check "2.3" "chrony pkg"             5 "rpm -q chrony"
run_check "2.3" "chronyd running"        5 "systemctl is-active chronyd"
run_check "2.3" "chrony.conf has NTP"     5 "grep -Eq '^(server|pool)\s+' /etc/chrony.conf"
run_check "2.3" "chrony root-only"       5 "grep -Eq '^OPTIONS=.*-u chrony' /usr/lib/systemd/system/chronyd.service"

# 2.4 Cron & At
run_check "2.4" "/etc/crontab perms"      5 "stat -c '%a' /etc/crontab"
for d in cron.hourly cron.daily cron.weekly cron.monthly cron.d; do
  run_check "2.4" "/etc/$d perms"         5 "stat -c '%a' /etc/$d"
done
run_check "2.4" "cron.allow root only"    5 "test -f /etc/cron.allow && grep -q '^root\$' /etc/cron.allow"
run_check "2.4" "cron.deny clean"         5 "! test -f /etc/cron.deny || grep -q '^$' /etc/cron.deny"
run_check "2.4" "at.allow root only"      5 "test -f /etc/at.allow && grep -q '^root\$' /etc/at.allow"
run_check "2.4" "at.deny clean"           5 "! test -f /etc/at.deny || grep -q '^$' /etc/at.deny"

# 3.3 Network Kernel Params
run_check "3.3" "ip_forward=0"           5 "sysctl net.ipv4.ip_forward | grep -q '= 0'"
run_check "3.3" "src_route disabled"     5 "sysctl net.ipv4.conf.all.accept_source_route | grep -q '= 0'"
run_check "3.3" "rp_filter=1"            5 "sysctl net.ipv4.conf.all.rp_filter | grep -q '= 1'"
run_check "3.3" "martians logged"        5 "sysctl net.ipv4.conf.all.log_martians | grep -q '= 1'"
run_check "3.3" "tcp_syncookies=1"       5 "sysctl net.ipv4.tcp_syncookies | grep -q '= 1'"
run_check "3.3" "ipv6_ra disabled"       5 "sysctl net.ipv6.conf.all.accept_ra | grep -q '= 0'"

# 4.1 Firewall Utility
run_check "4.1" "one fw tool"            5 "bash -c '([ -x \"$(command -v firewall-cmd)\" ] && ! command -v nft) || (! command -v firewall-cmd && [ -x \"$(command -v nft)\" ])'"

# 4.2 Firewalld Loopback
run_check "4.2" "loopback interface"     5 "firewall-cmd --zone=trusted --query-interface=lo"

# 4.3 NFTables
run_check "4.3" "base chains exist"      5 "nft list table inet filter | grep -q 'chain input'"
run_check "4.3" "loopback accept"        5 "nft list ruleset | grep -q 'iif lo accept'"

# 5.1 SSHD Config
run_check "5.1" "sshd_config perms"      5 "stat -c '%a' /etc/ssh/sshd_config | grep -q '^600\$'"
run_check "5.1" "PermitRootLogin no"     5 "grep -E '^PermitRootLogin no' /etc/ssh/sshd_config"
run_check "5.1" "KexAlgorithms set"      5 "grep -E '^KexAlgorithms ' /etc/ssh/sshd_config"
run_check "5.1" "ClientAliveInterval"    5 "grep -E '^ClientAliveInterval ' /etc/ssh/sshd_config"
run_check "5.1" "ClientAliveCountMax"    5 "grep -E '^ClientAliveCountMax ' /etc/ssh/sshd_config"
run_check "5.1" "MACs strong"            5 "grep -E '^MACs ' /etc/ssh/sshd_config"
run_check "5.1" "MaxStartups 10:30:60"   5 "grep -E '^MaxStartups 10:30:60' /etc/ssh/sshd_config"

# 5.2 Sudo & su
run_check "5.2" "sudo installed"          5 "rpm -q sudo"
run_check "5.2" "Defaults use_pty"        5 "grep -Eq '^Defaults\s+use_pty' /etc/sudoers"
run_check "5.2" "pam_wheel for su"        5 "grep -Eq '^auth\s+required\s+pam_wheel.so' /etc/pam.d/su"

# 5.3 PAM Packages & Config
run_check "5.3" "pam/authselect/pwqual pkgs" 5 "rpm -q pam authselect libpwquality"
run_check "5.3" "difok=4,minlen=14,remember=5" 5 "grep -E 'pam_pwquality.so.*difok=4' /etc/pam.d/system-auth && grep -E 'minlen=14' /etc/pam.d/system-auth && grep -E 'remember=5' /etc/pam.d/system-auth"
run_check "5.3" "pam_unix nullok absent"   5 "! grep -E 'pam_unix.so.*nullok' /etc/pam.d/system-auth"
run_check "5.3" "pam_faillock preauth"      5 "grep -E '^auth\s+required\s+pam_faillock.so preauth' /etc/pam.d/system-auth"
run_check "5.3" "pam_faillock authfail"     5 "grep -E '^auth\[default=die\]\s+pam_faillock.so authfail' /etc/pam.d/system-auth"

# 5.4 Shadow & System Accounts
run_check "5.4" "PASS_MAX_DAYS=90"         5 "grep -E '^PASS_MAX_DAYS\s+90' /etc/login.defs"
run_check "5.4" "PASS_WARN_AGE=7"          5 "grep -E '^PASS_WARN_AGE\s+7' /etc/login.defs"
run_check "5.4" "INACTIVE=30"              5 "grep -E '^INACTIVE\s+30' /etc/default/useradd"
run_check "5.4" "root PATH"                5 "grep -E '^export PATH=' /root/.bash_profile"
run_check "5.4" "system shells nologin"    5 "awk -F: '(\$3<1000 && \$1!=\"root\"){print \$7}' /etc/passwd | grep -q '/sbin/nologin'"

# 6.1 AIDE Integrity
run_check "6.1" "aide pkg"                 5 "rpm -q aide"
run_check "6.1" "aide.conf rules"          5 "grep -Eq '/.*f' /etc/aide.conf"
run_check "6.1" "aide cron job"            5 "grep -q 'aide --check' /etc/cron.daily/aide"

# 6.2 Journald & Rsyslog
run_check "6.2" "journald active"          5 "systemctl is-active systemd-journald"
run_check "6.2" "ForwardToSyslog=no"       5 "grep -E '^ForwardToSyslog=no' /etc/systemd/journald.conf"
run_check "6.2" "Compress set"             5 "grep -E '^Compress=' /etc/systemd/journald.conf"
run_check "6.2" "Storage set"              5 "grep -E '^Storage=' /etc/systemd/journald.conf"
run_check "6.2" "rsyslog active"           5 "systemctl is-active rsyslog"
run_check "6.2" "rsyslog remote"           5 "grep -Eq '@' /etc/rsyslog.conf"

# 7.1 Maintenance
run_check "7.1" "no-owner files"           5 "find / -xdev \( -nouser -o -nogroup \) | grep -q ."

# Citrix-specific
run_check "DC"  "xzwctxclc001 alias"       5 "getent hosts xzwctxclc001.int.wellmark.com"
run_check "DC"  "xzwctxclc002 alias"       5 "getent hosts xzwctxclc002.int.wellmark.com"
run_check "USB" "usb-storage blacklisted"   5 "grep -R 'blacklist usb-storage' /etc/modprobe.d"
run_check "VDA" "ctxusbsd running"         5 "systemctl is-active ctxusbsd"

echo
echo "All checks complete. CSV report saved to $CSV"
