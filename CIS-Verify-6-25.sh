#!/usr/bin/env bash
# cis_verify.sh — CIS Level 1 Manual Verifier with CSV output and timeouts

# Don’t use -u to avoid “unbound variable” errors
set -eE -o pipefail

CSV="cis_findings.csv"
echo "Section,Description,Status,Value" > "$CSV"

# Color functions
color_pass() { printf "\033[32mPASS\033[0m"; }
color_fail() { printf "\033[31mFAIL\033[0m"; }

# Generic check helper
# Usage: check <section> <description> <timeout_seconds> <command…>
check() {
  section="$1"; shift
  desc="$1";    shift
  to="$1";      shift

  # Run command with timeout, capture output & exit code
  out=$( timeout "${to}s" bash -c "$*" 2>&1 ) || true
  code=$?

  if [ $code -eq 0 ]; then
    status="PASS"
    col=$(color_pass)
  else
    status="FAIL"
    col=$(color_fail)
  fi

  # Collapse multiline output
  val=${out//$'\n'/ }
  printf "%-10s %-50s %s (%s)\n" "$section" "$desc" "$col" "$val"

  # Escape commas for CSV
  safe_val=${val//,/\\,}
  echo "\"$section\",\"$desc\",\"$status\",\"$safe_val\"" >> "$CSV"
}

echo "=== Running CIS Level 1 Manual Checks ==="

# 1.1 Filesystem
check "1.1" "/tmp is separate"      5 "mount | grep -q ' on /tmp '"
check "1.1" "/tmp options"         5 "findmnt --target /tmp -o OPTIONS -n"
check "1.1" "/dev/shm is separate" 5 "mount | grep -q ' on /dev/shm '"
check "1.1" "/dev/shm options"     5 "findmnt --target /dev/shm -o OPTIONS -n"
check "1.1" "/home is separate"    5 "mount | grep -q ' on /home '"
check "1.1" "/home options"        5 "findmnt --target /home -o OPTIONS -n"
check "1.1" "/var is separate"     5 "mount | grep -q ' on /var '"
check "1.1" "/var options"         5 "findmnt --target /var -o OPTIONS -n"

echo
# 1.2 Packages & Updates
check "1.2" "gpgcheck=1"           5 "grep -Eq '^gpgcheck[[:space:]]*=1' /etc/yum.conf"

# custom yum‐updates check
section="1.2"; desc="updates pending"
# run with timeout
timeout 30s bash -c "yum -q --assumeno check-update >/dev/null 2>&1"
code=$?
if [ $code -eq 0 ]; then
  status="PASS"; val="no updates"
elif [ $code -eq 100 ]; then
  status="FAIL"; val="updates available"
else
  status="FAIL"; val="error code $code"
fi
col=$([ "$status" = "PASS" ] && color_pass || color_fail)
printf "%-10s %-50s %s (%s)\n" "$section" "$desc" "$col" "$val"
echo "\"$section\",\"$desc\",\"$status\",\"$val\"" >> "$CSV"

echo
# 1.3 SELinux
check "1.3" "getenforce"           5 "getenforce"
check "1.3" "selinux-policy"       5 "rpm -q selinux-policy-targeted"
check "1.3" "not disabled in grub" 5 "! grep -Eq 'selinux=0' /etc/default/grub"

echo
# 1.4 Bootloader
check "1.4" "bootloader pw set"     5 "grep -q '^password_pbkdf2 ' /boot/grub2/user.cfg"
check "1.4" "grub.cfg perms"        5 "stat -c '%a %U:%G' /boot/grub2/grub.cfg"

echo
# 1.5 Process Hardening
check "1.5" "ASLR=2"                5 "sysctl kernel.randomize_va_space | grep -q '= 2'"
check "1.5" "ptrace_scope=1"        5 "sysctl kernel.yama.ptrace_scope | grep -q '= 1'"
check "1.5" "core_pattern"          5 "sysctl kernel.core_pattern | grep -q '^|/bin/false'"
check "1.5" "suid_dumpable=0"       5 "sysctl fs.suid_dumpable | grep -q '= 0'"

echo
# 1.6 Crypto Policy
check "1.6" "policy not LEGACY"     5 "update-crypto-policies --show | grep -qv legacy"
check "1.6" "SSH aes256-ctr"        5 "grep -Eq '^Ciphers .*aes256-ctr' /etc/ssh/sshd_config"

echo
# 1.7 Banners
check "1.7" "/etc/motd exists"      5 "test -f /etc/motd"
check "1.7" "/etc/issue exists"     5 "test -f /etc/issue"
check "1.7" "/etc/issue.net exists" 5 "test -f /etc/issue.net"

echo
# 1.8 GDM
check "1.8" "banner enabled"        5 "gsettings get org.gnome.login-screen banner-message-enable"
check "1.8" "user-list disabled"    5 "gsettings get org.gnome.login-screen disable-user-list"
check "1.8" "idle-delay set"        5 "gsettings get org.gnome.desktop.session idle-delay"
check "1.8" "autorun-never"         5 "grep -Eq 'autorun-never' /etc/gdm/custom.conf"

echo
# 2.1 Server Services
for svc in cups rpcbind avahi samba; do
  check "2.1" "$svc disabled/not active" 5 \
    "! systemctl is-enabled $svc 2>/dev/null && ! systemctl is-active $svc 2>/dev/null"
done

echo
# 2.2 Client Services
check "2.2" "telnet client absent"  5 "! rpm -q telnet >/dev/null 2>&1"

echo
# 2.3 Chrony
check "2.3" "chrony pkg"            5 "rpm -q chrony >/dev/null"
check "2.3" "chronyd running"       5 "systemctl is-active chronyd >/dev/null"
check "2.3" "chrony.conf NTP"       5 "grep -Eq '^(server|pool)\s+' /etc/chrony.conf"

echo
# 2.4 Cron & At
check "2.4" "crontab perms 644"     5 "stat -c '%a' /etc/crontab"
for d in cron.hourly cron.daily cron.weekly cron.monthly cron.d; do
  check "2.4" "$d perms 755"        5 "stat -c '%a' /etc/$d"
done
check "2.4" "cron.allow root only"  5 "test -f /etc/cron.allow && grep -q '^root\$' /etc/cron.allow"
check "2.4" "cron.deny empty/absent"5 "! test -f /etc/cron.deny || grep -q '^$' /etc/cron.deny"
check "2.4" "at.allow root only"    5 "test -f /etc/at.allow && grep -q '^root\$' /etc/at.allow"
check "2.4" "at.deny empty/absent"  5 "! test -f /etc/at.deny || grep -q '^$' /etc/at.deny"

echo
# 3.3 Network Kernel Params
check "3.3" "ip_forward=0"          5 "sysctl net.ipv4.ip_forward | grep -q '= 0'"
check "3.3" "src_route disabled"    5 "sysctl net.ipv4.conf.all.accept_source_route | grep -q '= 0'"

echo
# 4.1 Firewall Utility
check "4.1" "one fw tool"           5 "bash -c '([ -x \"$(command -v firewall-cmd)\" ] && ! command -v nft) || (! command -v firewall-cmd && [ -x \"$(command -v nft)\" ])'"

echo
# 4.2 Firewalld Loopback
check "4.2" "loopback interface"    5 "firewall-cmd --zone=trusted --query-interface=lo"

echo
# 5.1 SSHD Config
check "5.1" "sshd_config perms"     5 "stat -c '%a' /etc/ssh/sshd_config | grep -q '^600\$'"
check "5.1" "PermitRootLogin no"    5 "grep -E '^PermitRootLogin no' /etc/ssh/sshd_config"
check "5.1" "ClientAlive settings"  5 "grep -E '^ClientAliveInterval ' /etc/ssh/sshd_config && grep -E '^ClientAliveCountMax ' /etc/ssh/sshd_config"
check "5.1" "SSH MACs configured"   5 "grep -E '^MACs ' /etc/ssh/sshd_config"

echo
# 5.2 Sudo & su
check "5.2" "sudo installed"         5 "rpm -q sudo >/dev/null"
check "5.2" "Defaults use_pty"       5 "grep -Eq '^Defaults\s+use_pty' /etc/sudoers"
check "5.2" "pam_wheel for su"       5 "grep -Eq '^auth\s+required\s+pam_wheel.so' /etc/pam.d/su"

echo
# 5.3 PAM Packages & Config
check "5.3" "pam/authselect/pwqual pkgs" 5 "rpm -q pam authselect libpwquality >/dev/null"
check "5.3" "pwquality args"             5 "grep -E 'pam_pwquality.so.*minlen=14' /etc/pam.d/system-auth && grep -E 'difok=4' /etc/pam.d/system-auth && grep -E 'remember=5' /etc/pam.d/system-auth"
check "5.3" "nullok absent"              5 "! grep -E 'pam_unix.so.*nullok' /etc/pam.d/system-auth"

echo
# 5.4 Shadow & System Accounts
check "5.4" "PASS_MAX_DAYS=90"      5 "grep -E '^PASS_MAX_DAYS\s+90' /etc/login.defs"
check "5.4" "PASS_WARN_AGE=7"       5 "grep -E '^PASS_WARN_AGE\s+7' /etc/login.defs"
check "5.4" "INACTIVE=30"           5 "grep -E '^INACTIVE\s+30' /etc/default/useradd"
check "5.4" "root PATH integrity"   5 "grep -E '^export PATH=' /root/.bash_profile"
check "5.4" "system shells nologin" 5 "awk -F: '\$3<1000&&\$1!=\"root\"{print \$7}' /etc/passwd | grep -q '/sbin/nologin'"

echo
# 6.1 AIDE Integrity
check "6.1" "aide installed"        5 "rpm -q aide >/dev/null"
check "6.1" "aide.conf not empty"   5 "grep -Eq '/.*f' /etc/aide.conf"

echo
# 6.2 Journald & Rsyslog
check "6.2" "journald running"      5 "systemctl is-active systemd-journald >/dev/null"
check "6.2" "ForwardToSyslog=no"    5 "grep -E '^ForwardToSyslog=no' /etc/systemd/journald.conf"
check "6.2" "Compress set"          5 "grep -E '^Compress=' /etc/systemd/journald.conf"
check "6.2" "Storage set"           5 "grep -E '^Storage=' /etc/systemd/journald.conf"
check "6.2" "rsyslog running"       5 "systemctl is-active rsyslog >/dev/null"
check "6.2" "rsyslog remote host"   5 "grep -Eq '@' /etc/rsyslog.conf"

echo
# 7.1 Maintenance
check "7.1" "no-owner files"       5 "find / -xdev \( -nouser -o -nogroup \) | grep -q ."

echo
echo "Done.  CSV report saved to $CSV"
