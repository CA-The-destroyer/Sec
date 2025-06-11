#!/usr/bin/env bash
# cis_lowrisk_fix.sh — Remediate low-risk CIS findings (fixed sed syntax)

set -euo pipefail

echo "1) Remove unnecessary packages…"
for pkg in setroubleshoot-server telnet openldap-clients ypbind tftp; do
  if rpm -q "$pkg" &>/dev/null; then
    echo " → Removing $pkg"
    dnf -y remove "$pkg"
  else
    echo " → $pkg not installed"
  fi
done

echo
echo "2) Enforce core dump pattern…"
sysctl -w kernel.core_pattern="|/bin/false"
mkdir -p /etc/sysctl.d
if grep -q '^kernel.core_pattern' /etc/sysctl.d/99-cis.conf; then
  # use @ as sed delimiter so the |/bin/false text isn't misinterpreted
  sed -i 's@^kernel.core_pattern.*@kernel.core_pattern = |/bin/false@' /etc/sysctl.d/99-cis.conf
else
  echo 'kernel.core_pattern = |/bin/false' >> /etc/sysctl.d/99-cis.conf
fi
sysctl --system

echo
echo "3) GDM autorun-never (no functional impact)…"
if ! grep -q '^Autorun-never=true' /etc/gdm/custom.conf; then
  echo '[daemon]' >> /etc/gdm/custom.conf
  echo 'Autorun-never=true' >> /etc/gdm/custom.conf
fi

echo
echo "4) Cron & at restrictions…"
echo " → cron.allow = root"
echo root > /etc/cron.allow; chmod 600 /etc/cron.allow
echo " → cron.deny = empty"
: > /etc/cron.deny; chmod 644 /etc/cron.deny
echo " → at.allow = root"
echo root > /etc/at.allow; chmod 600 /etc/at.allow
echo " → at.deny = empty"
: > /etc/at.deny; chmod 644 /etc/at.deny

echo
echo "5) Trust loopback interface…"
if command -v firewall-cmd &>/dev/null; then
  firewall-cmd --permanent --zone=trusted --add-interface=lo
  firewall-cmd --reload
else
  nft list ruleset | grep -q 'iif lo accept' || nft insert rule inet filter input iif lo accept
fi

echo
echo "6) SSH hardening—KexAlgorithms & MaxStartups…"
SSH_CONF=/etc/ssh/sshd_config
# KexAlgorithms
grep -q '^KexAlgorithms ' $SSH_CONF && \
  sed -i.bak -E "s|^KexAlgorithms.*|KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group14-sha1|" $SSH_CONF \
  || echo 'KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group14-sha1' >> $SSH_CONF
# MaxStartups
grep -q '^MaxStartups ' $SSH_CONF && \
  sed -i.bak -E "s|^MaxStartups.*|MaxStartups 10:30:60|" $SSH_CONF \
  || echo 'MaxStartups 10:30:60' >> $SSH_CONF
systemctl reload sshd

echo
echo "7) PAM – pam_wheel, pam_unix nullok, pam_faillock scoping…"
# pam_wheel for su
if ! grep -q '^auth\s\+required\s\+pam_wheel.so' /etc/pam.d/su; then
  echo 'auth required pam_wheel.so use_uid' >> /etc/pam.d/su
fi
# remove nullok from pam_unix
sed -i.bak -E 's@(pam_unix\.so[^ ]*) nullok@\1@' /etc/pam.d/system-auth
# scope pam_faillock to non-root/service accounts
for f in /etc/pam.d/system-auth /etc/pam.d/password-auth; do
  sed -i.bak -E "/pam_faillock\.so preauth/ i auth [success=1 default=ignore] pam_succeed_if.so uid >= 1000 quiet" $f
  sed -i.bak -E "/pam_faillock\.so authfail/ i auth [success=1 default=ignore] pam_succeed_if.so uid >= 1000 quiet" $f
done

echo
echo "8) Inactive password lock – non-root only…"
# Adjust only the default for new accounts; root account unchanged
grep -q '^INACTIVE\s\+30' /etc/default/useradd || \
  sed -i.bak -E 's|^INACTIVE\s+[0-9]+|INACTIVE   30|' /etc/default/useradd

echo
echo "9) Cleanup orphan files under /tmp and /var/tmp only…"
find /tmp /var/tmp -xdev \( -nouser -o -nogroup \) -exec rm -rf {} +

echo
echo "Low-risk remediation complete.  Please re-verify with your validation script."
