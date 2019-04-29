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

systemctl stop httpd
systemctl stop php-fpm

# remove the 1.0 software...
yum -y remove \
    php-fkooman-otp-verifier \
    php-fkooman-oauth2-client \
    php-fkooman-oauth2-server \
    php-fkooman-yubitwee \
    php-fkooman-secookie \
    php-fkooman-sqlite-migrate \
    php-LC-openvpn-connection-manager \
    vpn-lib-common \
    vpn-admin-portal \
    vpn-server-api \
    vpn-server-node \
    vpn-user-portal \
    php-saml-ds \
    php-json-signer \
    vpn-portal-artwork-eduVPN \
    vpn-portal-artwork-LC \
    php-saml-ds-artwork-eduVPN \
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
rm -rf "/var/lib/php/session/*"

# (old) httpd config snippets
rm -f /etc/httpd/conf.d/vpn-user-portal*
rm -f /etc/httpd/conf.d/vpn-admin-portal*
rm -f /etc/httpd/conf.d/vpn-server-api*

# Delete old repository file(s)
rm -f /etc/yum.repos.d/LC.repo
rm -f /etc/yum.repos.d/eduVPN.repo
