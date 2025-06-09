#!/usr/bin/env bash
# cis_verify.sh — CIS Level 1 Manual Verifier with CSV output

# no -u here, to avoid '$3: unbound variable' errors
set -eE -o pipefail

CSV="cis_findings.csv"
echo "Section,Description,Status,Value" > "$CSV"

color_pass() { printf "\033[32mPASS\033[0m"; }
color_fail() { printf "\033[31mFAIL\033[0m"; }

# $1 = section, $2 = description, $3... = command to run
check() {
  section="$1"; shift
  desc="$1";    shift
  # capture both stdout and stderr
  value=$( { out=$("$@" 2>&1) || echo ""; echo "$out"; } )
  code=$?
  if [ $code -eq 0 ]; then
    status="PASS"
    printf "%-50s %-40s %s (%s)\n" "$section" "$desc" "$(color_pass)" "${value//[$'\n\r']/ }"
  else
    status="FAIL"
    printf "%-50s %-40s %s (%s)\n" "$section" "$desc" "$(color_fail)" "${value//[$'\n\r']/ }"
  fi
  # escape any commas in value
  safe_value=${value//,/\\,}
  echo "\"$section\",\"$desc\",\"$status\",\"$safe_value\"" >> "$CSV"
}

echo "=== Running CIS Level 1 Manual Checks ==="

# 1.1 Filesystem
check "1.1" "/tmp mounted"       mount | grep -q " on /tmp "
check "1.1" "/tmp opts"         findmnt --target /tmp -o OPTIONS -n
check "1.1" "/home mounted"      mount | grep -q " on /home "
check "1.1" "/home opts"        findmnt --target /home -o OPTIONS -n
check "1.1" "/var mounted"       mount | grep -q " on /var "
check "1.1" "/var opts"         findmnt --target /var -o OPTIONS -n

echo
echo "=== 1.2 Packages & Updates ==="
check() {
  desc="$1"; shift
  # run with timeout, capture exit code & output
  out=$(timeout 30s bash -c "$*" 2>&1)
  code=$?
  if [ $code -eq 0 ]; then
    status="PASS"
    printf "%-50s %s (%s)\n" "$desc" "$status" "${out//[$'\n']/ }"
  else
    status="FAIL"
    printf "%-50s %s (%s exit %d)\n" "$desc" "$status" "${out//[$'\n']/ }" "$code"
  fi
  # also append to CSV as before…
  safe=${out//,/\\,}
  echo "\"1.2\",\"$desc\",\"$status\",\"$safe\"" >> "$CSV"
}

# Ensure gpgcheck=1 in yum.conf
check "gpgcheck globally activated" \
  "grep -Eq '^gpgcheck[[:space:]]*=1' /etc/yum.conf"

# Quick, non-interactive update check (exit 100 = updates available; 0 = none)
check "yum updates pending (0=none,100=avail)" \
  "yum -q --assumeno check-update || test \$? -eq 100"


# 1.3 SELinux
check "1.3" "getenforce"         getenforce
check "1.3" "selinux-policy"     rpm -q selinux-policy-targeted

# 1.4 Bootloader
check "1.4" "grub user.cfg"      grep -q '^password_pbkdf2 ' /boot/grub2/user.cfg
check "1.4" "grub.cfg perms"     stat -c '%a %U:%G' /boot/grub2/grub.cfg

# 1.5 Hardening
check "1.5" "ptrace_scope"       sysctl kernel.yama.ptrace_scope
check "1.5" "core_pattern"       sysctl kernel.core_pattern

# 1.6 Crypto Policy
check "1.6" "policy show"        update-crypto-policies --show
check "1.6" "sshd ciphers"       grep -E '^Ciphers ' /etc/ssh/sshd_config

# 1.7 Banners
check "1.7" "/etc/motd exists"   test -f /etc/motd && echo OK
check "1.7" "/etc/issue exists"  test -f /etc/issue && echo OK

# 2.3 Chrony
check "2.3" "chronyd status"     systemctl status chronyd

# 3.3 Network Params
check "3.3" "ip_forward"         sysctl net.ipv4.ip_forward
check "3.3" "accept_src_route"   sysctl net.ipv4.conf.all.accept_source_route

# 4.2 Firewalld loopback
check "4.2" "fw-cmd loopback"    firewall-cmd --zone=trusted --query-interface=lo

# 5.1 SSHd config
check "5.1" "PermitRootLogin"    grep -E '^PermitRootLogin ' /etc/ssh/sshd_config
check "5.1" "ClientAliveInt"     grep -E '^ClientAliveInterval' /etc/ssh/sshd_config

# 5.2 Sudo & su
check "5.2" "Defaults use_pty"    grep -Eq '^Defaults\s+use_pty' /etc/sudoers
check "5.2" "pam_wheel"           grep -Eq '^auth\s+required\s+pam_wheel.so' /etc/pam.d/su

# 7.1 Maintenance
check "7.1" "no-owner files"      find / -xdev \( -nouser -o -nogroup \)

echo
echo "CSV report written to $CSV"
