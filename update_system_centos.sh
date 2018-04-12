#!/bin/sh

#
# *ONLY* run this during maintenance window!
#

(
    ./openvpn_disable_stop_remove.sh
)

systemctl stop httpd
systemctl stop php-fpm

# install updates
yum clean expire-cache && yum -y update

systemctl start php-fpm
systemctl start httpd

# regenerate/restart firewall
vpn-server-node-generate-firewall --install
systemctl restart iptables
systemctl restart ip6tables

(
    ./openvpn_generate_enable_start
)
