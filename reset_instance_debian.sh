#!/bin/sh

# you can use this script to "reset" a VPN instance, i.e. remove all data and 
# reinitialize it to the state after fresh install using deploy_${DIST}.sh
#
# NOTE: *ALL* VPN configuration will stop working, all users need to obtain
# a new configuration! All OAuth access tokens will become invalid!
#

(
    "$(dirname "$0")/openvpn_disable_stop_remove.sh"
)

systemctl stop apache2
systemctl stop php7.0-fpm

# remove data
rm -rf /var/lib/vpn-server-api/*
rm -rf /var/lib/vpn-user-portal/*
rm -rf /var/lib/php/sessions/*

# initialize
sudo -u www-data vpn-user-portal-init
sudo -u www-data vpn-server-api-init

# regenerate internal API secrets
vpn-server-api-update-api-secrets

systemctl start php7.0-fpm
systemctl start apache2

# regenerate/restart firewall
vpn-server-node-generate-firewall --install     
systemctl restart netfilter-persistent

(
    "$(dirname "$0")/openvpn_generate_enable_start.sh"
)
