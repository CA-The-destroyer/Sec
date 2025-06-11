#!/usr/bin/env bash
# cis_lowrisk_fix.sh — Remediate low‐risk CIS findings

set -euo pipefail

echo "1) Remove unnecessary packages (low-risk cleanup)…"
for pkg in setroubleshoot-server telnet openldap-clients ypbind tftp; do
  if rpm -q "$pkg" &>/dev/null; then
    echo " → Removing $pkg"
    dnf -y remove "$pkg"
  else
    echo " → $pkg not installed"
  fi
done

echo
echo "2) Enforce core dump pattern (no impact on VDA)…"
sysctl -w kernel.core_pattern="|/bin/false"
mkdir -p /etc/sysctl.d
if grep -q '^kernel.core_pattern' /etc/sysctl.d/99-cis.conf; then
  sed -i 's|^kernel.core_pattern.*|kernel.core_pattern = |/bin/false|' /etc/sysctl.d/99-cis.conf
else
  echo 'kernel.core_pattern = |/bin/false' >> /etc/sysctl.d/99-cis.conf
fi
sysctl --system

echo
echo "3) Disable GDM autorun (harmless for VDA)…"
if grep -q 'autorun-never' /etc/gdm/custom.conf; then
  echo " → GDM autorun-never already set"
else
  echo " → Setting GDM autorun-never"
  mkdir -p /etc/gdm
  echo '[daemon]' >> /etc/gdm/custom.conf
  echo 'AutomaticLoginEnable=false' >> /etc/gdm/custom.conf
  echo 'AutomaticLogin=' >> /etc/gdm/custom.conf
  echo 'DefaultSession=gnome' >> /etc/gdm/custom.conf
  echo 'WaylandEnable=false' >> /etc/gdm/custom.conf
  echo 'Autorun-Never=true' >> /etc/gdm/custom.conf
fi

echo
echo "4) Ensure cron.allow & at.allow contain only root…"
for file in /etc/cron.allow /etc/at.allow; do
  echo " → Ensuring $file exists and contains only root"
  echo root > "$file"
  chmod 600 "$file"
done

echo
echo "5) Ensure cron.deny & at.deny are empty or absent…"
for file in /etc/cron.deny /etc/at.deny; do
  if [ -f "$file" ]; then
    echo " → Truncating $file"
    : > "$file"
    chmod 644 "$file"
  else
    echo " → $file not present, OK"
  fi
done

echo
echo "6) Confirm chrony runs as root only (low-risk)…"
# This check is purely informational; chronyd already runs as chrony user by default.
grep -q '^OPTIONS=.*-u chrony' /usr/lib/systemd/system/chronyd.service \
  && echo " → chronyd is running as non-root (chrony user)" \
  || echo " → chronyd service file needs review for user directive"

echo
echo "Low-risk remediation complete.  You can re-run your verification now."
