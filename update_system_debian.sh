#!/bin/sh

#
# *ONLY* run this during a maintenance window!
#

sudo systemctl stop apache2
sudo systemctl stop php7.0-fpm

# install updates
sudo apt-get update && sudo apt-get -y dist-upgrade 

# delete template cache
# ONLY enable when using your own custom theme not packaged as RPM/DEB
#rm -rf /var/lib/vpn-user-portal/default/tpl
#rm -rf /var/lib/vpn-admin-portal/default/tpl

sudo systemctl start php7.0-fpm
sudo systemctl start apache2

# regenerate OpenVPN config
sudo vpn-server-node-server-config

# regenerate firewall
sudo vpn-server-node-generate-firewall --install

# restart firewall
sudo systemctl restart netfilter-persistent

# restart OpenVPN
sudo systemctl restart "openvpn-server@*"
