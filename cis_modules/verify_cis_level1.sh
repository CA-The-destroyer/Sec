#!/usr/bin/env bash
set -eo pipefail

echo "== 1.1 Filesystem =="
for mnt in /tmp /home /var; do
  echo "-- Checking $mnt mount options"
  opts=$(findmnt --target "$mnt" -o OPTIONS -n)
  echo "   Options: $opts"
  for want in nodev nosuid; do
    echo -n "   * $want: "
    echo "$opts" | grep -qw "$want" && echo "✔" || echo "✗"
  done
done

echo
echo "== 1.2 Package Management =="
echo -n "* gpgcheck=1: "
grep -E '^\s*gpgcheck\s*=\s*1' /etc/dnf/dnf.conf && echo "✔" || echo "✗"
echo -n "* no pending updates: "
dnf makecache -q && ! dnf check-update -q && echo "✔" || echo "✗"

echo
echo "== 1.3 SELinux =="
echo -n "* setroubleshoot-server removed: "
rpm -q setroubleshoot-server &>/dev/null && echo "✗" || echo "✔"

echo
echo "== 1.5 Process Hardening =="
echo -n "* ptrace_scope ≥1: "
sysctl kernel.yama.ptrace_scope | grep -qE '=[[:space:]]*[1-5]' && echo "✔" || echo "✗"
echo -n "* core_pattern no pipe: "
sysctl kernel.core_pattern | grep -qv '^\|' && echo "✔" || echo "✗"

echo
echo "== 1.6 Crypto Policy =="
echo -n "* policy not LEGACY: "
update-crypto-policies --show | grep -qv legacy && echo "✔" || echo "✗"
echo -n "* sha1 disabled: "
update-crypto-policies --show | grep -q ':!SHA1' && echo "✔" || echo "✗"
echo -n "* CBC for SSH disabled: "
grep -q 'Ciphers.*-aes128-cbc' /etc/crypto-policies/back-ends/openssh.config && echo "✔" || echo "✗"
echo -n "* chacha20-poly1305 disabled: "
grep -q 'Ciphers.*-chacha20-poly1305@openssh.com' /etc/crypto-policies/back-ends/openssh.config && echo "✔" || echo "✗"
echo -n "* EtM disabled: "
grep -q 'MACs.*-hmac-etm' /etc/crypto-policies/back-ends/openssh.config && echo "✔" || echo "✗"

echo
echo "== 1.7 Banners =="
echo -n "* /etc/issue contains banner: "
grep -q 'Authorized users only' /etc/issue && echo "✔" || echo "✗"
echo -n "* /etc/issue.net contains banner: "
grep -q 'Authorized users only' /etc/issue.net && echo "✔" || echo "✗"

echo
echo "== 1.8 GDM =="
for num in 01-banner-message 02-disable-users 03-idle-lock 04-lock-policy 05-automount 06-automount-ignore 07-autorun 08-autorun-ignore; do
  echo -n "* $num: "
  grep -q '=' /etc/dconf/db/gdm.d/$num && echo "✔" || echo "✗"
done

echo
echo "== 2.3 Time Synchronization =="
echo -n "* chrony installed & running: "
(rpm -q chrony &>/dev/null && systemctl is-enabled --quiet chronyd.service && systemctl is-active --quiet chronyd.service) && echo "✔" || echo "✗"
echo -n "* ntp removed: "
rpm -q ntp &>/dev/null && echo "✗" || echo "✔"
echo -n "* chrony.conf has server: "
grep -E '^\s*server\s+' /etc/chrony.conf && echo "✔" || echo "✗"

echo
echo "== 2.4 Job Schedulers =="
for f in cron.allow cron.deny at.allow at.deny; do
  echo "-- /etc/$f"
  [[ -f /etc/$f ]] && echo "   exists: ✔" || echo "   exists: ✗"
  perms=$(stat -c '%a' /etc/$f 2>/dev/null || echo "missing")
  echo "   perms: $perms"
  if [[ $f == cron.allow || $f == at.allow ]]; then
    echo -n "   only root: "
    grep -xq 'root' /etc/$f && [[ $(wc -l < /etc/$f) -eq 1 ]] && echo "✔" || echo "✗"
  else
    echo -n "   empty: "
    [[ -s /etc/$f ]] && echo "✗" || echo "✔"
  fi
done

echo
echo "== 3.1 Network Devices =="
echo -n "* bluez removed & disabled: "
(! rpm -q bluez &>/dev/null && ! systemctl is-enabled --quiet bluetooth.service && ! systemctl is-active --quiet bluetooth.service) && echo "✔" || echo "✗"

echo
echo "All checks complete."
