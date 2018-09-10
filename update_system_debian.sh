#!/bin/sh

#
# *ONLY* run this during a maintenance window!
#

systemctl stop apache2
systemctl stop php7.0-fpm

# install updates
apt-get update && apt-get -y dist-upgrade 

systemctl start php7.0-fpm
systemctl start apache2

# regenerate OpenVPN config
vpn-server-node-server-config

# regenerate/restart firewall
vpn-server-node-generate-firewall --install
systemctl restart netfilter-persistent

# restart OpenVPN
systemctl restart "openvpn-server@*"
