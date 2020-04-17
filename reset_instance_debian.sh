#!/bin/sh

# you can use this script to "reset" a VPN instance, i.e. remove all data and 
# reinitialize it to the state after fresh install using deploy_${DIST}.sh
#
# NOTE: *ALL* VPN configuration will stop working, all users need to obtain
# a new configuration! All OAuth access tokens will become invalid!
#

# Stop and Disable OpenVPN Server Process(es)
for CONFIG_NAME in $(systemctl list-units "openvpn-server@*" --no-legend | cut -d ' ' -f 1)
do
    systemctl disable --now "${CONFIG_NAME}"
done

# Remove all OpenVPN Server Configuration(s) and Certificate(s)
rm -rf /etc/openvpn/server/*

systemctl stop apache2
systemctl stop php7.0-fpm

# remove data
rm -rf /var/lib/vpn-server-api/*
rm -rf /var/lib/vpn-user-portal/*
rm -rf /var/lib/php/sessions/*
rm -f /etc/vpn-user-portal/oauth.key

# initialize
sudo -u www-data vpn-user-portal-init
vpn-user-portal-generate-oauth-key
sudo -u www-data vpn-server-api-init

# regenerate internal API secrets
vpn-server-api-update-api-secrets

systemctl start php7.0-fpm
systemctl start apache2

# (Re)generate OpenVPN Server Configuration(s) and Certificate(s)
vpn-server-node-server-config || exit

# Enable and Start OpenVPN Server Process(es)
for CONFIG_NAME in /etc/openvpn/server/*.conf
do
    CONFIG_NAME=$(basename "${CONFIG_NAME}" .conf)
    systemctl enable --now "openvpn-server@${CONFIG_NAME}"
done
