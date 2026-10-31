#!/usr/bin/env bash
# bootstrap_vm.sh: Day 22. Run ONCE on a fresh Ubuntu 24.04 LTS VM, as a sudo user:  sudo bash bootstrap_vm.sh <your-laptop-public-ip>
# Hardens the box, sets IST + NTP, creates the 'trader' user, a Python venv, and the secrets/log directories.
set -euo pipefail
LAPTOP_IP="${1:?usage: sudo bash bootstrap_vm.sh <your laptop public IP for SSH>}"

apt-get update && apt-get -y upgrade
apt-get -y install python3-venv python3-pip git ufw fail2ban chrony unattended-upgrades jq

# time: IST wall clock, NTP-synced (decision days + the 06:00 token expiry depend on it)
timedatectl set-timezone Asia/Kolkata
systemctl enable --now chrony
dpkg-reconfigure -f noninteractive unattended-upgrades

# firewall: SSH only, only from your laptop. No inbound web ports: the login redirect comes through your SSH tunnel.
ufw default deny incoming && ufw default allow outgoing
ufw allow from "$LAPTOP_IP" to any port 22 proto tcp
ufw --force enable
systemctl enable --now fail2ban

# SSH: keys only, no root login
sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/; s/^#\?PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart ssh

# trader user + layout
id trader &>/dev/null || adduser --disabled-password --gecos "" trader
mkdir -p /home/trader/.ssh && cp ~/.ssh/authorized_keys /home/trader/.ssh/ 2>/dev/null || true
install -d -o trader -g trader -m 700 /home/trader/app /home/trader/.kite /home/trader/logs
install -d -m 750 -o root -g trader /etc/rubin-trader
[ -f /etc/rubin-trader/kite.env ] || install -m 640 -o root -g trader /dev/null /etc/rubin-trader/kite.env
chown -R trader:trader /home/trader/.ssh && chmod 700 /home/trader/.ssh
sudo -u trader python3 -m venv /home/trader/app/.venv
sudo -u trader /home/trader/app/.venv/bin/pip install --upgrade pip "kiteconnect>=5.1" pandas numpy pytest

echo "Done. Next: put KITE_API_KEY / KITE_API_SECRET in /etc/rubin-trader/kite.env (root:trader 640),"
echo "whitelist this VM's static IP in the Kite developer console, then: python preflight.py --static-ip <ip>"
