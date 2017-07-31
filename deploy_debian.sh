#!/bin/bash -ve

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
WEB_FQDN=eduvpn.nl

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
LETSENCRYPT_MAIL=gijs@pythonic.nl

# The interface that connects to "the Internet" (for firewall rules)
EXTERNAL_IF=enp0s3

###############################################################################
# SOFTWARE
###############################################################################

# enable our repository
apt install -y apt-transport-https
curl -L https://static.eduvpn.nl/debian/eduvpn.key  | apt-key add -
echo "deb https://static.eduvpn.nl/debian/ stretch main" > /etc/apt/sources.list.d/eduvpn.list
apt update

# install software (dependencies)
apt install -y apache2 php-fpm certbot pwgen

# install software (VPN packages)
apt install -y vpn-server-node vpn-server-api vpn-admin-portal vpn-user-portal

###############################################################################
# APACHE
###############################################################################

# Use a hardended ssl.conf instead of the default, gives A+ on
# https://www.ssllabs.com/ssltest/
# TODO: disabled for now, lets try it first with debian default
#cp resources/ssl.conf /etc/httpd/conf.d/ssl.conf
sudo a2enmod ssl
systemctl restart apache2

# VirtualHost
cp resources/vpn.example.conf /etc/apache2/sites-available/${WEB_FQDN}.conf
sed -i "s/vpn.example/${WEB_FQDN}/" /etc/apache2/sites-available//${WEB_FQDN}.conf

###############################################################################
# PHP
###############################################################################

# switch to unix socket, default in newer PHP versions, but not on CentOS 7
#$ TODO: is this required?
#sed -i "s|^listen = 127.0.0.1:9000$|listen = /run/php-fpm/www.sock|" /etc/php-fpm.d/www.conf

# set timezone to UTC
# TODO: is this required?
#cp resources/70-timezone.ini /etc/php.d/70-timezone.ini
# session hardening
#cp resources/75-session.ini /etc/php.d/75-session.ini

# work around to create the session directory, otherwise we have to install
# the PHP package, this is only on CentOS
# TODO: probably not required
#mkdir -p /var/lib/php/session
#chown -R root.apache /var/lib/php/session
#chmod 0770 /var/lib/php/session
#restorecon -R /var/lib/php/session

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

systemctl stop apache2
certbot register ${AGREE_TOS} -m ${LETSENCRYPT_MAIL} || true

# TODO: disable the || true, now for testing only
certbot certonly -n --standalone -d ${WEB_FQDN} || true

# not sure if these hooks are read by systemd on debian
cat << EOF > /etc/init.d/certbot
PRE_HOOK="--pre-hook 'systemctl stop apache2'"
POST_HOOK="--post-hook 'systemctl start apache2'"
RENEW_HOOK=""
CERTBOT_ARGS=""
EOF

# enable automatic renewal
systemctl enable --now certbot.timer

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
systemctl enable --now apache2

# TODO: ??
#systemctl enable --now vmtoolsd

###############################################################################
# OPENVPN SERVER CONFIG
###############################################################################

# NOTE: the openvpn-server systemd unit file only allows 10 OpenVPN processes
# by default! 

# generate the server configuration files
# TODO: remove || true
vpn-server-node-server-config --profile internet --generate || true

# enable and start OpenVPN
# TODO: below the fedora commands, why not use EXTERNAL_IF ?
#systemctl enable --now openvpn-server@default-internet-0
#systemctl enable --now openvpn-server@default-internet-1
systemctl enable --now openvpn-server@EXTERNAL_IF || true

###############################################################################
# FIREWALL
###############################################################################

# generate and install the firewall
# TODO: remove || true
vpn-server-node-generate-firewall --install || true

# TODO: looks like debian doesn't have systemd scripts for iptables
#systemctl enable --now iptables
#systemctl enable --now ip6tables

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
