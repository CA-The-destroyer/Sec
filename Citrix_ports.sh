sudo nft add table inet filter
sudo nft 'add chain inet filter input { type filter hook input priority 0; policy drop; }'
sudo nft add rule inet filter input ct state established,related accept
# Allow ALL Citrix ports—both TCP & UDP
for p in 1494 2598; do
  sudo nft add rule inet filter input tcp dport $p accept
  sudo nft add rule inet filter input udp dport $p accept
done
sudo nft add rule inet filter input tcp dport 22 accept
