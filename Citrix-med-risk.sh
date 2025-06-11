#!/usr/bin/env bash
# cis_citrix_medium_risk.sh — Medium-Risk CIS Remediations for Citrix VDA (SELinux step removed)

set -euo pipefail

echo "=== Medium-Risk Remediation for Citrix VDA ==="

# 1. LDAP client: reinstall if your FAS/LDAP backend needs it
echo -n "1) Ensuring LDAP client present… "
if ! rpm -q openldap-clients &>/dev/null; then
  dnf -y install openldap-clients
  echo "installed"
else
  echo "already present"
fi

# 2. PAM faillock scoping: skip system/service accounts
echo -n "2) Scoping pam_faillock to non-root/service UIDs… "
for f in /etc/pam.d/system-auth /etc/pam.d/password-auth; do
  if grep -q 'pam_faillock.so' "$f"; then
    sed -i.bak -E "/pam_faillock\\.so preauth/ i auth [success=1 default=ignore] pam_succeed_if.so uid > 0 quiet" "$f"
    sed -i -E "/pam_faillock\\.so authfail/ i auth [success=1 default=ignore] pam_succeed_if.so uid > 0 quiet" "$f"
  fi
done
echo "done"

# 3. SSH KexAlgorithms: apply Citrix-recommended list
echo -n "3) Hardening SSH KexAlgorithms… "
SSH_CONF=/etc/ssh/sshd_config
grep -q '^KexAlgorithms ' "$SSH_CONF" \
  && sed -i.bak -E "s|^KexAlgorithms.*|KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group14-sha1|" "$SSH_CONF" \
  || echo "KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group14-sha1" >> "$SSH_CONF"
systemctl reload sshd
echo "done"

# 4. Trust loopback in the firewall
echo -n "4) Trusting loopback interface… "
if command -v firewall-cmd &>/dev/null; then
  firewall-cmd --permanent --zone=trusted --add-interface=lo
  firewall-cmd --reload
else
  nft list ruleset | grep -q 'iif lo accept' || nft insert rule inet filter input iif lo accept
fi
echo "done"

# 5. Blacklist usb-storage (if acceptable for your USB policy)
echo -n "5) Blacklisting usb-storage… "
BL=/etc/modprobe.d/usb-blacklist.conf
if ! grep -q 'blacklist usb-storage' "$BL" 2>/dev/null; then
  echo -e "install usb-storage /bin/false\nblacklist usb-storage" >> "$BL"
  depmod -a
fi
echo "done"

# 6. Review chrony run user (informational)
echo -n "6) Confirm chronyd runs as non-root… "
if grep -Eq '^OPTIONS=.*-u chrony' /usr/lib/systemd/system/chronyd.service; then
  echo "OK"
else
  echo "WARNING: chronyd may run as root"
fi

echo
echo "Medium-risk remediation complete.  Please re-test Citrix VDA functionality."
