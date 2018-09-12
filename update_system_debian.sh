#!/bin/sh

#
# *ONLY* run this during a maintenance window!
#

systemctl stop apache2
systemctl stop php7.0-fpm

# install updates
apt-get update && apt-get -y dist-upgrade 

# delete template cache
# ONLY enable when using your own custom theme not packaged as RPM/DEB
#rm -rf /var/lib/vpn-user-portal/default/tpl
#rm -rf /var/lib/vpn-admin-portal/default/tpl

systemctl start php7.0-fpm
systemctl start apache2

# regenerate OpenVPN config
vpn-server-node-server-config

# regenerate firewall
vpn-server-node-generate-firewall --install

# restart firewall
systemctl restart netfilter-persistent

# restart OpenVPN
systemctl restart "openvpn-server@*"
