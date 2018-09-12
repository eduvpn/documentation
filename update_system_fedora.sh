#!/bin/sh

#
# *ONLY* run this during a maintenance window!
#

systemctl stop httpd
systemctl stop php-fpm

# install updates
dnf -y --refresh update

# delete template cache
# ONLY enable when using your own custom theme not packaged as RPM/DEB
#rm -rf /var/lib/vpn-user-portal/default/tpl
#rm -rf /var/lib/vpn-admin-portal/default/tpl

systemctl start php-fpm
systemctl start httpd

# regenerate OpenVPN config
vpn-server-node-server-config

# regenerate firewall
vpn-server-node-generate-firewall --install

# restart firewall
systemctl restart iptables
systemctl restart ip6tables

# restart OpenVPN
systemctl restart "openvpn-server@*"
