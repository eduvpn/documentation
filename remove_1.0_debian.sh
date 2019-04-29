#!/bin/sh

#
# Remove Let's Connect! / eduVPN 1.0 from an existing server...
#
# NOTE:
# - NO backup is made of anything!
# - it is still recommended to "wipe" the VM and start fresh with a 2.0 
#   deployment!

###############################################################################
# CONFIGURATION
###############################################################################

# Stop and disable all OpenVPN services
(
    "$(dirname "$0")/openvpn_disable_stop_remove.sh"
)

systemctl stop apache2
systemctl stop php7.0-fpm

# remove the 1.0 software...
apt-get -y remove \
    php-fkooman-otp-verifier \
    php-fkooman-oauth2-client \
    php-fkooman-oauth2-server \
    php-fkooman-yubitwee \
    php-fkooman-secookie \
    php-fkooman-sqlite-migrate \
    php-lc-openvpn-connection-manager \
    vpn-lib-common \
    vpn-admin-portal \
    vpn-server-api \
    vpn-server-node \
    vpn-user-portal \
    php-saml-ds \
    php-json-signer \
    vpn-portal-artwork-eduvpn \
    vpn-portal-artwork-lc \
    php-saml-ds-artwork-eduvpn \
    openvpn-plugin-auth-script \

# delete all config
rm -rf "/etc/vpn-user-portal"
rm -rf "/etc/vpn-admin-portal"
rm -rf "/etc/vpn-server-api"
rm -rf "/etc/vpn-server-node"
# delete all data
rm -rf "/var/lib/vpn-user-portal"
rm -rf "/var/lib/vpn-admin-portal"
rm -rf "/var/lib/vpn-server-api"

# delete PHP sessions
rm -rf /var/lib/php/sessions/*

# (old) httpd config snippets
a2disconf vpn-server-api
a2disconf vpn-user-portal
a2disconf vpn-admin-portal
rm -f /etc/apache2/conf-available/vpn-user-portal.conf
rm -f /etc/apache2/conf-available/vpn-admin-portal.conf
rm -f /etc/apache2/conf-available/vpn-server-api.conf

# Delete old repository file(s)
rm -f /etc/apt/sources.list.d/LC.list
rm -f /etc/apt/sources.list.d/eduVPN.list
