#!/bin/sh

#
# *ONLY* run this during a maintenance window!
#

sudo systemctl stop httpd
sudo systemctl stop php-fpm

# install updates
sudo yum clean expire-cache && sudo yum -y update

sudo systemctl start php-fpm
sudo systemctl start httpd

# regenerate OpenVPN config
sudo vpn-server-node-server-config

# regenerate firewall
sudo vpn-server-node-generate-firewall --install

# restart firewall
sudo systemctl restart iptables
sudo systemctl restart ip6tables

# restart OpenVPN
sudo systemctl restart "openvpn-server@*"
