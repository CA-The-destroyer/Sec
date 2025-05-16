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
  if [ "$mnt" = "/tmp" ]; then
    echo -n "   * noexec: "
    echo "$opts" | grep -qw "noexec" && echo "✔" || echo "✗"
  fi
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
echo -n "* ptrace_scope =1: "
sysctl -n kernel.yama.ptrace_scope | grep -xq '1' && echo "✔" || echo "✗"
echo -n "* core_pattern = core: "
sysctl -n kernel.core_pattern | grep -xq 'core' && echo "✔" || echo "✗"

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
echo -n "* /etc/issue: "
grep -q 'Authorized users only' /etc/issue && echo "✔" || echo "✗"
echo -n "* /etc/issue.net: "
grep -q 'Authorized users only' /etc/issue.net && echo "✔" || echo "✗"

echo
echo "== 1.8 GDM =="
for num in 01-banner-message 02-disable-users 03-idle-lock 04-lock-policy 05-automount 06-automount-ignore 07-autorun 08-autorun-ignore; do
  echo -n "* $num: "
  grep -q '=' /etc/dconf/db/gdm.d/$num && echo "✔" || echo "✗"
done

echo
echo "== 2.2 Client Services =="
echo -n "* telnet client removed: "
rpm -q telnet &>/dev/null && echo "✗" || echo "✔"

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
echo "== 3 Network =="
echo -n "* telnet client removed: "
rpm -q telnet &>/dev/null && echo "✗" || echo "✔"
echo -n "* bluetooth removed & disabled: "
(! rpm -q bluez &>/dev/null && ! systemctl is-enabled --quiet bluetooth.service && ! systemctl is-active --quiet bluetooth.service) && echo "✔" || echo "✗"
echo -n "* ip forwarding disabled: "
sysctl -n net.ipv4.ip_forward | grep -xq '0' && echo "✔" || echo "✗"
echo -n "* source routing disabled (all): "
sysctl -n net.ipv4.conf.all.accept_source_route | grep -xq '0' && echo "✔" || echo "✗"
echo -n "* source routing disabled (default): "
sysctl -n net.ipv4.conf.default.accept_source_route | grep -xq '0' && echo "✔" || echo "✗"

echo
echo "== 4 Host-based Firewall =="
echo -n "* firewalld enabled, nftables removed: "
(rpm -q firewalld &>/dev/null && systemctl is-enabled --quiet firewalld.service && ! rpm -q nftables) && echo "✔" || echo "✗"
echo -n "* loopback allowed: "
firewall-cmd --zone=public --query-interface=lo && echo "✔" || echo "✗"

echo
echo "== 4.3 NFTables =="
echo -n "* established connections allowed: "
nft list ruleset | grep -q 'ct state established,related accept' && echo "✔" || echo "✗"
echo -n "* default deny policy: "
nft list table inet filter | grep -q 'policy drop' && echo "✔" || echo "✗"

echo
echo "== 5 SSHD =="
echo -n "* /etc/ssh/sshd_config perms: "
stat -c '%a' /etc/ssh/sshd_config | grep -q '600' && echo "✔" || echo "✗"
echo -n "* PermitRootLogin no: "
grep -E '^PermitRootLogin\s+no' /etc/ssh/sshd_config && echo "✔" || echo "✗"
echo -n "* MACs set: "
grep -E '^MACs\s+' /etc/ssh/sshd_config && echo "✔" || echo "✗"
echo -n "* ClientAliveInterval & CountMax: "
grep -E '^ClientAliveInterval\s+[0-9]+' /etc/ssh/sshd_config && grep -E '^ClientAliveCountMax\s+[0-9]+' /etc/ssh/sshd_config && echo "✔" || echo "✗"

echo
echo "== 5.2 Sudo & SU =="
echo -n "* sudo use_pty: "
grep -E '^Defaults\s+use_pty' /etc/sudoers && echo "✔" || echo "✗"
echo -n "* su restricted to wheel: "
grep -E '^auth\s+required\s+pam_wheel.so' /etc/pam.d/su && echo "✔" || echo "✗"

echo
echo "== 5 PAM & Shadow =="
echo -n "* password complexity: "
grep -E 'pam_pwquality.so.*minlen=[0-9]+' /etc/pam.d/password-auth && echo "✔" || echo "✗"
echo -n "* history remember: "
grep -E 'pam_pwhistory.so.*remember=[0-9]+' /etc/pam.d/password-auth && echo "✔" || echo "✗"
echo -n "* no nullok: "
grep -E 'pam_unix.so.*nullok' /etc/pam.d/password-auth && echo "✗" || echo "✔"
echo -n "* password expiration: "
chage -l root | grep -q 'Maximum.*:[[:space:]]*[0-9]' && echo "✔" || echo "✗"
echo -n "* warning days: "
grep -E '^\s*WARN_[DT]OOLSAYS' /etc/login.defs && echo "✔" || echo "✗"
echo -n "* inactive lock: "
grep -E '^\s*INACTIVE' /etc/login.defs && echo "✔" || echo "✗"

echo
echo "== 6 AIDE =="
echo -n "* aide installed: "
rpm -q aide &>/dev/null && echo "✔" || echo "✗"
echo -n "* aide cron exists: "
grep -q '/usr/sbin/aide --check' /etc/cron.hourly/aide || echo "✗"; echo "✔"

echo
echo "== 6 Journald & Rsyslog =="
echo -n "* journal-upload enabled: "
systemctl is-enabled --quiet systemd-journal-upload.service && echo "✔" || echo "✗"
echo -n "* ForwardToSyslog disabled: "
grep -E '^ForwardToSyslog\s*=\s*no' /etc/systemd/journald.conf && echo "✔" || echo "✗"
echo -n "* rsyslog configured: "
grep -q '^*.*@@' /etc/rsyslog.conf && echo "✔" || echo "✗"

echo
echo "== 6 Logfiles =="
echo -n "* all logfiles locked: "
find /var/log -type f ! -perm -o-rwx | grep -q /var/log && echo "✔" || echo "✗"

echo
echo "== 7 Maintenance =="
echo -n "* no files without owner/group: "
find / -xdev \( -nouser -o -nogroup \) | grep -q . && echo "✗" || echo "✔"

echo
echo "All checks complete."
