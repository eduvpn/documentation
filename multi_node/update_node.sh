#!/bin/sh

sudo yum clean expire-cache && sudo yum -y update
sudo vpn-server-node-server-config
sudo vpn-server-node-generate-firewall --install
sudo systemctl restart iptables
sudo systemctl restart ip6tables
