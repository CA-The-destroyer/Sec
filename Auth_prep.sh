#!/usr/bin/env bash
# setup_wheel_ssh.sh
# Prompts for a user to add to wheel, enables password authentication,
# restricts SSH to wheel group, and reloads sshd.

# This script is intended for use on a systemd-based Linux distribution
# Run as root or with sudo privileges.
# Start by copying this script to the target machine
# Next run "dos2unix auth_prep.sh"
# Then run "chmod +x auth_prep.sh"
# Finally run "./auth_prep.sh"

set -euo pipefail

SSHD_CONFIG="/etc/ssh/sshd_config"
BACKUP="${SSHD_CONFIG}.bak.$(date +%s)"

# Prompt for username(s)
read -rp "Enter username(s) to add to wheel (space-separated): " -a USERS

if [ "${#USERS[@]}" -eq 0 ]; then
  echo "No users specified. Exiting."
  exit 1
fi

# Add each user to wheel
for u in "${USERS[@]}"; do
  if id "$u" &>/dev/null; then
    usermod -aG wheel "$u"
    echo "Added $u to wheel"
  else
    echo "User '$u' does not exist; skipping"
  fi
done

# Backup current sshd_config
cp "$SSHD_CONFIG" "$BACKUP"
echo "Backed up original to $BACKUP"

# Ensure PasswordAuthentication yes
if grep -Eq '^\s*PasswordAuthentication\s+' "$SSHD_CONFIG"; then
  sed -i 's/^\s*PasswordAuthentication\s\+.*/PasswordAuthentication yes/' "$SSHD_CONFIG"
else
  echo 'PasswordAuthentication yes' >> "$SSHD_CONFIG"
fi
echo "Set PasswordAuthentication yes"

# Ensure AllowGroups wheel
if grep -Eq '^\s*AllowGroups\s+' "$SSHD_CONFIG"; then
  sed -i 's/^\s*AllowGroups\s\+.*/AllowGroups wheel/' "$SSHD_CONFIG"
else
  echo 'AllowGroups wheel' >> "$SSHD_CONFIG"
fi
echo "Configured AllowGroups wheel"

# Restart or reload sshd
if systemctl is-active --quiet sshd; then
  systemctl reload sshd
  echo "sshd reloaded"
else
  systemctl restart sshd
  echo "sshd started"
fi

echo "✅ Done. Users ${USERS[*]} can now SSH as members of wheel."
