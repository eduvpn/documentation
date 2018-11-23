#!/bin/sh

#
# Deploy a single VPN machine
#

###############################################################################
# CONFIGURATION
###############################################################################

MACHINE_HOSTNAME=$(hostname -f)

# DNS name of the Web Server
printf "DNS name of the Web Server [${MACHINE_HOSTNAME}]: "; read -r WEB_FQDN
WEB_FQDN=${WEB_FQDN:-${MACHINE_HOSTNAME}}

# DNS name of the OpenVPN Server (defaults to DNS name of the Web Server
# use different name if you want to allow moving the OpenVPN processes to 
# another machine in the future without breaking client configuration files
printf "DNS name of the OpenVPN Server [%s]: " "${WEB_FQDN}"; read -r VPN_FQDN
VPN_FQDN=${VPN_FQDN:-${WEB_FQDN}}

# The interface that connects to "the Internet" (for firewall rules)
printf "External interface connecting to the Internet [eth0]: "; read -r EXTERNAL_IF
EXTERNAL_IF=${EXTERNAL_IF:-eth0}    

###############################################################################
# SOFTWARE
###############################################################################

apt update

DEBIAN_FRONTEND=noninteractive apt install -y apt-transport-https curl \
    apache2 php-fpm pwgen iptables-persistent sudo locales-all

curl -L https://repo.letsconnect-vpn.org/deb/release/eduVPN.key | apt-key add -
echo "deb https://repo.letsconnect-vpn.org/deb/release/stretch stretch main" > /etc/apt/sources.list.d/LC.list
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
# CERTIFICATE
###############################################################################

# generate self signed certificate and key
openssl req \
    -nodes \
    -subj "/CN=${WEB_FQDN}" \
    -x509 \
    -sha256 \
    -newkey rsa:2048 \
    -keyout "/etc/ssl/private/${WEB_FQDN}.key" \
    -out "/etc/ssl/certs/${WEB_FQDN}.crt" \
    -days 90

###############################################################################
# APACHE
###############################################################################

a2enmod ssl headers rewrite proxy_fcgi setenvif 
a2enconf php7.0-fpm

# VirtualHost
cp resources/ssl.debian.conf /etc/apache2/mods-available/ssl.conf 
cp resources/vpn.example.debian.conf /etc/apache2/sites-available/${WEB_FQDN}.conf
cp resources/localhost.debian.conf /etc/apache2/sites-available/localhost.conf

# update hostname
sed -i "s/vpn.example/${WEB_FQDN}/" /etc/apache2/sites-available/${WEB_FQDN}.conf

a2enconf vpn-server-api
a2enconf vpn-user-portal
a2enconf vpn-admin-portal
a2dissite 000-default
a2ensite ${WEB_FQDN}
a2ensite localhost

###############################################################################
# PHP
###############################################################################

# set timezone to UTC
cp resources/70-timezone.ini /etc/php/7.0/mods-available/eduvpn-timezone.ini
phpenmod -v 7.0 -s ALL eduvpn-timezone

# session hardening
cp resources/75-session.debian.ini /etc/php/7.0/mods-available/eduvpn-session.ini
phpenmod -v 7.0 -s ALL eduvpn-session

# restart php-fpm to read the new configuration
systemctl restart php7.0-fpm

###############################################################################
# VPN-SERVER-API
###############################################################################

# update the IPv4 CIDR and IPv6 prefix to random IP ranges and set the extIf
vpn-server-api-update-ip --profile internet --host ${VPN_FQDN} --ext ${EXTERNAL_IF}

# initialize the CA
sudo -u www-data vpn-server-api-init

###############################################################################
# VPN-USER-PORTAL
###############################################################################

# generate OAuth public/private keys
sudo -u www-data vpn-user-portal-init

###############################################################################
# VPN-SERVER-NODE
###############################################################################

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
systemctl restart apache2

###############################################################################
# OPENVPN SERVER CONFIG
###############################################################################

# NOTE: the openvpn-server systemd unit file only allows 10 OpenVPN processes
# by default! 

# generate the OpenVPN server configuration files and certificates
vpn-server-node-server-config

systemctl enable --now openvpn-server@default-internet-0
systemctl enable --now openvpn-server@default-internet-1

###############################################################################
# FIREWALL
###############################################################################

vpn-server-node-generate-firewall --install
systemctl enable netfilter-persistent
systemctl restart netfilter-persistent

###############################################################################
# USERS
###############################################################################

USER_PASS=$(pwgen 12 -n 1)
ADMIN_PASS=$(pwgen 12 -n 1)
sudo -u www-data vpn-user-portal-add-user  --user me    --pass "${USER_PASS}"
sudo -u www-data vpn-admin-portal-add-user --user admin --pass "${ADMIN_PASS}"

echo "########################################################################"
echo "# Admin Portal"
echo "#     https://${WEB_FQDN}/vpn-admin-portal"
echo "#         User: admin"
echo "#         Pass: ${ADMIN_PASS}"
echo "# User Portal"
echo "#     https://${WEB_FQDN}/vpn-user-portal"
echo "#         User: me"
echo "#         Pass: ${USER_PASS}"
echo "# OAuth Public Key:"
echo "#     $(vpn-user-portal-show-public-key)"
echo "########################################################################"
# ALL DONE!
