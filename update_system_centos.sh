#!/bin/sh

# stop services
sudo systemctl stop "openvpn-server@*"
sudo systemctl stop httpd
sudo systemctl stop php-fpm

# install updates
sudo yum clean expire-cache && sudo yum -y update

sudo systemctl start php-fpm
sudo systemctl start httpd

# regenerate config & firewall
sudo vpn-server-node-server-config --generate
sudo vpn-server-node-generate-firewall --install

# (re)start services
sudo systemctl restart iptables
sudo systemctl restart ip6tables
sudo systemctl start "openvpn-server@*"
