echo "== 2.1.11 CUPS (print server) =="
rpm -q cups                       && echo "✗ cups still installed" || echo "✔ cups removed"
systemctl is-enabled --quiet cups && echo "✗ cups.service still enabled"
systemctl is-active  --quiet cups && echo "✗ cups.service still running"

echo
echo "== 2.1.12 rpcbind =="
rpm -q rpcbind                       && echo "✗ rpcbind still installed" || echo "✔ rpcbind removed"
systemctl is-enabled --quiet rpcbind && echo "✗ rpcbind.service still enabled"
systemctl is-active  --quiet rpcbind && echo "✗ rpcbind.service still running"

echo
echo "== 2.1.2 avahi-daemon =="
rpm -q avahi-daemon                             && echo "✗ avahi-daemon still installed" || echo "✔ avahi-daemon removed"
systemctl is-enabled --quiet avahi-daemon.service && echo "✗ avahi-daemon.service still enabled"
systemctl is-active  --quiet avahi-daemon.service && echo "✗ avahi-daemon.service still running"

echo
echo "== 2.1.6 Samba (smb/nmb) =="
rpm -q samba                   && echo "✗ samba still installed" || echo "✔ samba removed"
for svc in smb nmb; do
  systemctl is-enabled --quiet $svc.service && echo "✗ $svc.service still enabled"
  systemctl is-active  --quiet $svc.service && echo "✗ $svc.service still running"
done

echo
echo "== 2.2.4 telnet client =="
rpm -q telnet                   && echo "✗ telnet still installed" || echo "✔ telnet removed"

echo
echo "== 2.3.2 chrony vs ntp =="
rpm -q chrony                    && echo "✔ chrony installed" || echo "✗ chrony missing"
systemctl is-enabled --quiet chronyd.service && echo "✔ chronyd enabled" || echo "✗ chronyd not enabled"
systemctl is-active  --quiet chronyd.service && echo "✔ chronyd running" || echo "✗ chronyd not running"
rpm -q ntp                       && echo "✗ ntp still installed" || echo "✔ ntp removed"

echo
echo "== 2.4.1.8 cron.allow =="
stat -c '%a %U:%G' /etc/cron.allow    || echo "✗ /etc/cron.allow missing"
grep -Ex '^root$' /etc/cron.allow     && echo "✔ only root in cron.allow" || echo "✗ cron.allow incorrect"
wc -l < /etc/cron.allow | grep -qx 1 && echo "✔ cron.allow has exactly one entry" || echo "✗ cron.allow entry count wrong"

echo
echo "== 2.4.2.1 at.allow =="
stat -c '%a %U:%G' /etc/at.allow      || echo "✗ /etc/at.allow missing"
grep -Ex '^root$' /etc/at.allow       && echo "✔ only root in at.allow" || echo "✗ at.allow incorrect"
wc -l < /etc/at.allow | grep -qx 1   && echo "✔ at.allow has exactly one entry" || echo "✗ at.allow entry count wrong"

echo
echo "== 3.1.3 Bluetooth (bluez) =="
rpm -q bluez                       && echo "✗ bluez still installed" || echo "✔ bluez removed"
systemctl is-enabled --quiet bluetooth.service && echo "✗ bluetooth.service still enabled"
systemctl is-active  --quiet bluetooth.service && echo "✗ bluetooth.service still running"
