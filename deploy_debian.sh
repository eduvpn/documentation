#!/bin/sh

#
# Deploy a single VPN machine
#

###############################################################################
# VARIABLES
###############################################################################

# **NOTE**: make sure WEB_FQDN and VPN_FQDN are valid DNS names with 
# appropriate A (and AAAA) records!
#

# VARIABLES
WEB_FQDN=vpn.example

# we use a separate hostname for the VPN connections to allow for moving the
# VPN processes to another machine in the future when client configurations are
# already distributed
VPN_FQDN=internet.${WEB_FQDN}
#VPN_FQDN=${WEB_FQDN}

# Let's Encrypt
# TOS: https://letsencrypt.org/repository/
AGREE_TOS=""
# to agree to the TOS, add "#" the line above and remove "#" below this line
#AGREE_TOS="--agree-tos"

# The email address you want to use for Let's Encrypt (for issues with 
# renewing the certificate etc.)
LETSENCRYPT_MAIL=admin@example.org

# The interface that connects to "the Internet" (for firewall rules)
EXTERNAL_IF=eth0

###############################################################################
# SOFTWARE
###############################################################################

apt update

DEBIAN_FRONTEND=noninteractive apt install -y apt-transport-https curl apache2 \
    php-fpm certbot pwgen iptables-persistent sudo locales-all

curl -L https://repo.eduvpn.org/debian/eduvpn.key | apt-key add -
echo "deb https://repo.eduvpn.org/debian/ stretch main" > /etc/apt/sources.list.d/eduvpn.list
apt update

# install software (VPN packages)
DEBIAN_FRONTEND=noninteractive apt install -y vpn-server-node vpn-server-api \
    vpn-admin-portal vpn-user-portal

###############################################################################
# LOCALES
###############################################################################

# enable the NL locales
sed -i 's/^# nl_NL/nl_NL/' /etc/locale.gen

# Generate the enabled locales
locale-gen

###############################################################################
# APACHE
###############################################################################

a2enmod ssl headers rewrite proxy_fcgi setenvif 
a2enconf php7.0-fpm

# VirtualHost
cp resources/vpn.example.conf /etc/apache2/sites-available/${WEB_FQDN}.conf

# Update log paths
sed -i 's|ErrorLog logs/vpn.example_error_log|ErrorLog ${APACHE_LOG_DIR}/vpn.example_error_log|' /etc/apache2/sites-available/${WEB_FQDN}.conf
sed -i 's|TransferLog logs/vpn.example_access_log|TransferLog ${APACHE_LOG_DIR}/vpn.example_access_log|' /etc/apache2/sites-available/${WEB_FQDN}.conf
sed -i 's|ErrorLog logs/vpn.example_ssl_error_log|ErrorLog ${APACHE_LOG_DIR}/vpn.example_ssl_error_log|' /etc/apache2/sites-available/${WEB_FQDN}.conf
sed -i 's|TransferLog logs/vpn.example_ssl_access_log|TransferLog ${APACHE_LOG_DIR}/vpn.example_ssl_access_log|' /etc/apache2/sites-available/${WEB_FQDN}.conf

# update hostname
sed -i "s/vpn.example/${WEB_FQDN}/" /etc/apache2/sites-available/${WEB_FQDN}.conf

a2enconf vpn-server-api
a2enconf vpn-user-portal
a2enconf vpn-admin-portal
a2ensite ${WEB_FQDN}

###############################################################################
# PHP
###############################################################################

# set timezone to UTC
cp resources/70-timezone.ini /etc/php/7.0/mods-available/eduvpn-timezone.ini
phpenmod -v 7.0 -s ALL eduvpn-timezone

# session hardening
cp resources/75-session.debian.ini /etc/php/7.0/mods-available/eduvpn-session.ini
phpenmod -v 7.0 -s ALL eduvpn-session

# reload php-fpm service to read the new configuration
systemctl reload php7.0-fpm

###############################################################################
# VPN-SERVER-API
###############################################################################

# update the IPv4 CIDR and IPv6 prefix to random IP ranges and set the extIf
vpn-server-api-update-ip --profile internet --host ${VPN_FQDN} --ext ${EXTERNAL_IF}

# initialize the CA
sudo -u www-data vpn-server-api-init

###############################################################################
# VPN-ADMIN-PORTAL
###############################################################################

sed -i "s|http://localhost/vpn-server-api/api.php|https://${WEB_FQDN}/vpn-server-api/api.php|" /etc/vpn-admin-portal/default/config.php

###############################################################################
# VPN-USER-PORTAL
###############################################################################

sed -i "s|http://localhost/vpn-server-api/api.php|https://${WEB_FQDN}/vpn-server-api/api.php|" /etc/vpn-user-portal/default/config.php

# generate OAuth public/private keys
sudo -u www-data vpn-user-portal-init

###############################################################################
# VPN-SERVER-NODE
###############################################################################

sed -i "s|http://localhost/vpn-server-api/api.php|https://${WEB_FQDN}/vpn-server-api/api.php|" /etc/vpn-server-node/default/config.php

# On Debian different user/group for running OpenVPN
sed -i "s|'vpnUser' => 'openvpn'|'vpnUser' => 'nobody'|" /etc/vpn-server-node/default/config.php
sed -i "s|'vpnGroup' => 'openvpn'|'vpnGroup' => 'nogroup'|" /etc/vpn-server-node/default/config.php

###############################################################################
# NETWORK
###############################################################################

cat << EOF > /etc/sysctl.d/70-vpn.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
# allow RA for IPv6 on external interface, NOT for static IPv6!
net.ipv6.conf.${EXTERNAL_IF}.accept_ra = 2
EOF

sysctl --system

###############################################################################
# UPDATE SECRETS
###############################################################################

# update API secret
vpn-server-api-update-api-secrets

###############################################################################
# LET'S ENCRYPT / CERTBOT
###############################################################################

# setup the hooks to stop and start Apache on renewal
cat << EOF >> /etc/letsencrypt/cli.ini
pre-hook systemctl stop apache2
post-hook systemctl start apache2
EOF

certbot register ${AGREE_TOS} -m ${LETSENCRYPT_MAIL}
certbot certonly -n --standalone -d ${WEB_FQDN}

###############################################################################
# WEB
###############################################################################

mkdir -p /var/www/${WEB_FQDN}
# Copy server info JSON file
cp resources/info.json /var/www/${WEB_FQDN}/info.json
sed -i "s/vpn.example/${WEB_FQDN}/" /var/www/${WEB_FQDN}/info.json

###############################################################################
# DAEMONS
###############################################################################

systemctl enable --now php7.0-fpm

###############################################################################
# OPENVPN SERVER CONFIG
###############################################################################

# NOTE: the openvpn-server systemd unit file only allows 10 OpenVPN processes
# by default! 

vpn-server-node-server-config --profile internet --generate

systemctl enable --now openvpn-server@default-internet-0
systemctl enable --now openvpn-server@default-internet-1

###############################################################################
# FIREWALL
###############################################################################

vpn-server-node-generate-firewall --install --debian
systemctl enable netfilter-persistent
systemctl restart netfilter-persistent

###############################################################################
# USERS
###############################################################################

USER_PASS=$(pwgen 12 -n 1)
ADMIN_PASS=$(pwgen 12 -n 1)
vpn-user-portal-add-user  --user me    --pass "${USER_PASS}"
vpn-admin-portal-add-user --user admin --pass "${ADMIN_PASS}"

echo "########################################################################"
echo "# Admin Portal"
echo "#     https://${WEB_FQDN}/vpn-admin-portal"
echo "#         User: admin"
echo "#         Pass: ${ADMIN_PASS}"
echo "# User Portal"
echo "#     https://${WEB_FQDN}/vpn-user-portal"
echo "#         User: me"
echo "#         Pass: ${USER_PASS}"
echo "########################################################################"
# ALL DONE!
