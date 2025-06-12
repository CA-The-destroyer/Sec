#!/usr/bin/env bash
# cis_verify.sh — CIS Level 1 Manual Verifier with Evidence and CSV output

set -euo pipefail

CSV="cis_findings.csv"
echo "Section,Description,Status,ExitCode,Evidence" > "$CSV"

# Color helpers
pass() { printf "\033[32mPASS\033[0m"; }
fail() { printf "\033[31mFAIL\033[0m"; }

# run_check <section> <description> <timeout_secs> <command…>
run_check() {
  section="$1"; shift
  desc="$1";    shift
  to="$1";      shift

  rc=0
  if [ "$to" -gt 0 ]; then
    raw=$( timeout "${to}s" bash -c "$*" 2>&1 ) || rc=$?
  else
    raw=$( "$@" 2>&1 ) || rc=$?
  fi

  # sanitize multi-line into one line
  val=$(printf "%s" "$raw" | sed ':a;N;$!ba;s/\n/ | /g')

  if [ "$rc" -eq 0 ]; then
    status="$(pass)"
    csv_status="PASS"
  else
    status="$(fail)"
    csv_status="FAIL"
  fi

  printf "%-8s %-40s %s  [exit %d]  evidence: %s\n" \
    "$section" "$desc" "$status" "$rc" "$val"

  # Append to CSV
  esc=$(echo "$val" | sed 's/"/""/g')
  echo "\"$section\",\"$desc\",\"$csv_status\",$rc,\"$esc\"" >> "$CSV"
}

echo "=== CIS Level 1 Manual Checks ==="

# (… Insert all your existing checks here, for brevity omitted …)

# -----------------------------
# Example subset of checks:
# 1.1 Filesystem
run_check "1.1" "/tmp separate"      5 "mount | grep -q ' on /tmp '"
run_check "1.1" "/tmp opts"          5 "findmnt --target /tmp -o OPTIONS -n"
# …

# 5.4 Shadow & System Accounts
run_check "5.4" "PASS_MAX_DAYS=90"   5 "grep -E '^root:[^:]*:[^:]*:[^:]*:[^:]*:([0-9]+):' /etc/shadow | cut -d: -f5"
run_check "5.4" "INACTIVE in default" 5 "grep -E '^INACTIVE' /etc/default/useradd"

# -----------------------------
echo
echo "=== Evidence for Remaining Nessus Failures ==="
# 1.6.7 EtM for SSH
run_check "1.6" "EtM disabled for SSH"      5 "grep -E '^MACs ' /etc/ssh/sshd_config"
# 2.1.6 Samba service
run_check "2.1" "samba enabled"             5 "systemctl is-enabled smb nmb"
# 2.4.2.1 AT restricted
run_check "2.4" "at.allow contents"         5 "cat /etc/at.allow 2>/dev/null || echo '(missing)'"
# 3.1.3 Bluetooth
run_check "3.1" "bluetooth service"         5 "systemctl is-enabled bluetooth 2>&1"
# 4.2.2 Loopback firewall
run_check "4.2" "firewalld lo-trusted"      5 "firewall-cmd --zone=trusted --query-interface=lo 2>&1"
# 4.3.2 nft established
run_check "4.3" "nft established rule"      5 "nft list ruleset | grep -E 'ct state (established|related) accept'"
# 4.3.3 nft default policy
run_check "4.3" "nft default policy"        5 "nft list ruleset | grep -E 'chain input.*policy (drop|reject)'"
# 5.1.20 PermitRootLogin
run_check "5.1" "PermitRootLogin setting"   5 "grep -E '^PermitRootLogin' /etc/ssh/sshd_config"
# 5.4.1.1 PASS_MAX_DAYS for root
run_check "5.4" "root PASS_MAX_DAYS"        5 "grep -E '^root:' /etc/shadow | cut -d: -f5"
# 5.4.1.5 INACTIVE for root
run_check "5.4" "INACTIVE in default"       5 "grep -E '^INACTIVE' /etc/default/useradd"
# 5.4.2.7 service shells
run_check "5.4" "service-shells"            5 "awk -F: '(\$3<1000){print \$1\":\"\$7}' /etc/passwd"

echo
echo "All checks complete.  See $CSV for full results and evidence."
