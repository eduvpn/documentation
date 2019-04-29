#!/bin/sh

BACKUP_DIR=${HOME}/LC-backup
INSTANCE=default

#
# Remove Let's Connect! / eduVPN 1.0 from an existing server...
#
# NOTE:
# - it is still recommended to "wipe" the VM and start fresh with a 2.0 
#   deployment
# - it does NOT completely revert to pre-1.0 state, just removes the 
#   components / data that may cause conflict running the 2.0 deploy script
# - it does NOT touch /etc/httpd/saml (mod_auth_mellon) if you were using 
#   SAML authentication
# - it creates a backup of all the (relevant) configuration files, but you can
#   NOT copy them back over after the new installation!
# - it creates a copy of the (old) OAuth key and converts it to the new format,
#   you can copy this file ($HOME/LC-backup/vpn-user-portal-OAuth.key) to 
#   /etc/vpn-user-portal/oauth.key after the 2.0 deployment is complete to keep 
#   the same OAuth key (ONLY relevant for "Guest" / "Secure Internet" 
#   deployments)

###############################################################################
# CONFIGURATION
###############################################################################

MACHINE_HOSTNAME=$(hostname -f)

# DNS name of the Web Server
printf "DNS name of the Web Server [%s]: " "${MACHINE_HOSTNAME}"; read -r WEB_FQDN
WEB_FQDN=${WEB_FQDN:-${MACHINE_HOSTNAME}}

# Stop Services
(
    "$(dirname "$0")/openvpn_disable_stop_remove.sh"
)
systemctl stop php-fpm
systemctl stop httpd

# Backup Relevant Stuff
mkdir "${BACKUP_DIR}"
cp /etc/vpn-user-portal/${INSTANCE}/config.php ${BACKUP_DIR}/vpn-user-portal.php
cp /etc/vpn-admin-portal/${INSTANCE}/config.php ${BACKUP_DIR}/vpn-admin-portal.php
cp /etc/vpn-server-api/${INSTANCE}/config.php ${BACKUP_DIR}/vpn-server-api.php
cp /etc/vpn-server-node/${INSTANCE}/config.php ${BACKUP_DIR}/vpn-server-node.php
cp /etc/vpn-server-node/firewall.php ${BACKUP_DIR}/vpn-server-node-firewall.php
cat /var/lib/vpn-user-portal/${INSTANCE}/OAuth.key | tr '+/' '-_' | tr -d '=' | ${BACKUP_DIR}/vpn-user-portal-OAuth.key
cp /etc/httpd/conf.d/${WEB_FQDN}.conf ${BACKUP_DIR}/${WEB_FQDN}.conf

# remove (all) 1.0 software...
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

# make sure nothing is left behind...
rm -rf "/etc/vpn-user-portal/*"
rm -rf "/etc/vpn-admin-portal"
rm -rf "/etc/vpn-server-api/*"
rm -rf "/etc/vpn-server-node/*"

rm -rf "/var/lib/vpn-user-portal/*"
rm -rf "/var/lib/vpn-admin-portal"
rm -rf "/var/lib/vpn-server-api/*"

# delete PHP sessions
rm -rf "/var/lib/php/session/*"

# (old) httpd config snippets
rm -f /etc/httpd/conf.d/vpn-user-portal*
rm -f /etc/httpd/conf.d/vpn-admin-portal*
rm -f /etc/httpd/conf.d/vpn-server-api*

# Delete old repository file
rm /etc/yum.repos.d/LC.repo

# Delete SELinux rules as they changed in 2.0
semanage port -d -t openvpn_port_t -p tcp 11940-12195
semanage port -d -t openvpn_port_t -p tcp 1195-1263
semanage port -d -t openvpn_port_t -p udp 1195-1263

