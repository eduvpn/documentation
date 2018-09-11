#!/bin/sh

#
# *ONLY* run this during a maintenance window!
#

systemctl stop httpd
systemctl stop php-fpm

# install updates
yum clean expire-cache && yum -y update

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
