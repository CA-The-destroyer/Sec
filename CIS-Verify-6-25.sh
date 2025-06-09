#!/usr/bin/env bash
# cis_verify.sh — CIS Level 1 Manual Verifier with CSV output and timeouts

# Don’t use -u to avoid “unbound variable” errors
set -eE -o pipefail

CSV="cis_findings.csv"
echo "Section,Description,Status,Value" > "$CSV"

# Color functions
color_pass() { printf "\033[32mPASS\033[0m"; }
color_fail() { printf "\033[31mFAIL\033[0m"; }

# check <section> <description> <command…>
check() {
  section="$1"; shift
  desc="$1";    shift

  # Run command with timeout, capture output & exit code
  out=$( timeout 30s bash -c "$*" 2>&1 ) || true
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

  # Print to console
  printf "%-10s %-50s %s (%s)\n" "$section" "$desc" "$col" "$val"

  # Escape commas in value for CSV
  safe_val=${val//,/\\,}
  echo "\"$section\",\"$desc\",\"$status\",\"$safe_val\"" >> "$CSV"
}

echo "=== Running CIS Level 1 Manual Checks ==="

# 1.1 Filesystem
check "1.1" "/tmp mounted"    "mount | grep -q ' on /tmp '"
check "1.1" "/tmp opts"      "findmnt --target /tmp -o OPTIONS -n"
check "1.1" "/dev/shm mtd"   "mount | grep -q ' on /dev/shm '"
check "1.1" "/dev/shm opts"  "findmnt --target /dev/shm -o OPTIONS -n"
check "1.1" "/home mounted"  "mount | grep -q ' on /home '"
check "1.1" "/home opts"     "findmnt --target /home -o OPTIONS -n"
check "1.1" "/var mounted"   "mount | grep -q ' on /var '"
check "1.1" "/var opts"      "findmnt --target /var -o OPTIONS -n"

echo
# 1.2 Packages & Updates
check "1.2" "gpgcheck=1"       "grep -Eq '^gpgcheck[[:space:]]*=1' /etc/yum.conf"
check "1.2" "yum updates"      "yum -q --assumeno check-update"

echo
# 1.3 SELinux
check "1.3" "getenforce"       "getenforce"
check "1.3" "selinux-policy"   "rpm -q selinux-policy-targeted"
check "1.3" "SELinux disabled" "! grep -Eq 'selinux=0' /etc/default/grub"

echo
# 1.4 Bootloader
check "1.4" "grub user.cfg"    "grep -q '^password_pbkdf2 ' /boot/grub2/user.cfg"
check "1.4" "grub.cfg perms"   "stat -c '%a %U:%G' /boot/grub2/grub.cfg"

echo
# 1.5 Process Hardening
check "1.5" "ptrace_scope"     "sysctl kernel.yama.ptrace_scope"
check "1.5" "core_pattern"     "sysctl kernel.core_pattern"
check "1.5" "suid_dumpable"    "sysctl fs.suid_dumpable"

echo
# 1.6 Crypto Policy
check "1.6" "policy show"      "update-crypto-policies --show"
check "1.6" "SSH ciphers"      "grep -E '^Ciphers ' /etc/ssh/sshd_config"

echo
# 1.7 Banners
check "1.7" "/etc/motd"        "test -f /etc/motd && echo OK"
check "1.7" "/etc/issue"       "test -f /etc/issue && echo OK"
check "1.7" "/etc/issue.net"   "test -f /etc/issue.net && echo OK"

echo
# 1.8 GDM
check "1.8" "GDM banner"       "gsettings get org.gnome.login-screen banner-message-enable"
check "1.8" "GDM user-list"    "gsettings get org.gnome.login-screen disable-user-list"
check "1.8" "GDM idle-delay"   "gsettings get org.gnome.desktop.session idle-delay"
check "1.8" "GDM autorun-never" "grep -Eq 'autorun-never' /etc/gdm/custom.conf"

echo
# 2.1 Server Services
for svc in cups rpcbind avahi samba; do
  check "2.1" "$svc disabled" \
    "! systemctl is-enabled $svc && ! systemctl is-active $svc"
done

echo
# 2.2 Client Services
check "2.2" "telnet pkg"       "! rpm -q telnet >/dev/null"

echo
# 2.3 Chrony
check "2.3" "chrony pkg"       "rpm -q chrony"
check "2.3" "chronyd srv"      "systemctl status chronyd"
check "2.3" "chrony.conf"      "grep -Eq '^(server|pool)\s+' /etc/chrony.conf"

echo
# 2.4 Cron & At
check "2.4" "crontab perms"    "stat -c '%a' /etc/crontab"
for d in cron.hourly cron.daily cron.weekly cron.monthly cron.d; do
  check "2.4" "$d perms"       "stat -c '%a' /etc/$d"
done
check "2.4" "cron.allow"       "test -f /etc/cron.allow && grep -q '^root\$' /etc/cron.allow"
check "2.4" "cron.deny"        "! test -f /etc/cron.deny || grep -q '^$' /etc/cron.deny"
check "2.4" "at.allow"         "test -f /etc/at.allow && grep -q '^root\$' /etc/at.allow"
check "2.4" "at.deny"          "! test -f /etc/at.deny || grep -q '^$' /etc/at.deny"

echo
# 3.3 Network Kernel Params
check "3.3" "ip_forward"       "sysctl net.ipv4.ip_forward"
check "3.3" "src_route"        "sysctl net.ipv4.conf.all.accept_source_route"

echo
# 4.1 Firewall Utility
check "4.1" "one fw tool"      "bash -c '([ -x \"$(command -v firewall-cmd)\" ] && ! command -v nft) || (! command -v firewall-cmd && [ -x \"$(command -v nft)\" ])'"

echo
# 4.2 Firewalld Loopback
check "4.2" "fw loopback"      "firewall-cmd --zone=trusted --query-interface=lo"

echo
# 5.1 SSHD Config
check "5.1" "sshd perms"       "stat -c '%a' /etc/ssh/sshd_config"
check "5.1" "PermitRootLogin"  "grep -E '^PermitRootLogin ' /etc/ssh/sshd_config"
check "5.1" "ClientAliveInt"   "grep -E '^ClientAliveInterval ' /etc/ssh/sshd_config"
check "5.1" "ClientAliveMax"   "grep -E '^ClientAliveCountMax ' /etc/ssh/sshd_config"
check "5.1" "SSH MACs"         "grep -E '^MACs ' /etc/ssh/sshd_config"

echo
# 5.2 Sudo & su
check "5.2" "sudo pkg"         "rpm -q sudo"
check "5.2" "use_pty"          "grep -Eq '^Defaults\s+use_pty' /etc/sudoers"
check "5.2" "pam_wheel"        "grep -Eq '^auth\s+required\s+pam_wheel.so' /etc/pam.d/su"

echo
# 5.3 PAM Packages & Config
check "5.3" "pam pkgs"         "rpm -q pam authselect libpwquality"
check "5.3" "pwquality args"   "grep -E 'pam_pwquality.so.*minlen=14' /etc/pam.d/system-auth && grep -E 'difok=4' /etc/pam.d/system-auth && grep -E 'remember=5' /etc/pam.d/system-auth"
check "5.3" "nullok absent"    "! grep -E 'pam_unix.so.*nullok' /etc/pam.d/system-auth"

echo
# 5.4 Shadow & System Accounts
check "5.4" "PASS_MAX_DAYS"    "grep -E '^PASS_MAX_DAYS\s+90' /etc/login.defs"
check "5.4" "PASS_WARN_AGE"     "grep -E '^PASS_WARN_AGE\s+7' /etc/login.defs"
check "5.4" "INACTIVE"          "grep -E '^INACTIVE\s+30' /etc/default/useradd"
check "5.4" "root PATH"         "grep -E '^export PATH=' /root/.bash_profile"
check "5.4" "sys shells"        "awk -F: '$3<1000&&\$1!=\"root\"{print \$7}' /etc/passwd"

echo
# 6.1 AIDE Integrity
check "6.1" "aide pkg"         "rpm -q aide"
check "6.1" "aide.conf"        "grep -Eq '/.*f' /etc/aide.conf"

echo
# 6.2 Journald & Rsyslog
check "6.2" "journald active"  "systemctl is-active systemd-journald"
check "6.2" "ForwardToSyslog"   "grep -E '^ForwardToSyslog=no' /etc/systemd/journald.conf"
check "6.2" "Compress"         "grep -E '^Compress=' /etc/systemd/journald.conf"
check "6.2" "Storage"          "grep -E '^Storage=' /etc/systemd/journald.conf"
check "6.2" "rsyslog active"   "systemctl is-active rsyslog"
check "6.2" "rsyslog remote"   "grep -Eq '@' /etc/rsyslog.conf"

echo
# 7.1 Maintenance
check "7.1" "no-owner files"   "find / -xdev \( -nouser -o -nogroup \)"

echo
echo "Done. CSV report saved to $CSV"
