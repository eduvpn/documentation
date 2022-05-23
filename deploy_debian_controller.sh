#!/bin/sh

#
# Deploy a VPN server on Debian/Ubuntu
#

###############################################################################
# VARIABLES
###############################################################################

MACHINE_HOSTNAME=$(hostname -f)

# DNS name of the Web Server
printf "DNS name of the Web Server [%s]: " "${MACHINE_HOSTNAME}"; read -r WEB_FQDN
WEB_FQDN=${WEB_FQDN:-${MACHINE_HOSTNAME}}
# convert hostname to lowercase
WEB_FQDN=$(echo "${WEB_FQDN}" | tr '[:upper:]' '[:lower:]')

###############################################################################
# SOFTWARE
###############################################################################

apt update
apt install -y apt-transport-https curl apache2 php-fpm pwgen \
    iptables-persistent sudo lsb-release ipcalc-ng tmux

DEBIAN_CODE_NAME=$(/usr/bin/lsb_release -cs)
PHP_VERSION=$(/usr/sbin/phpquery -V)

cp resources/repo+v3@eduvpn.org.asc /etc/apt/trusted.gpg.d/repo+v3@eduvpn.org.asc
echo "deb https://repo.eduvpn.org/v3/deb ${DEBIAN_CODE_NAME} main" | tee /etc/apt/sources.list.d/eduVPN_v3.list

apt update

# install software (VPN packages)
apt install -y vpn-user-portal

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
a2dismod status
a2enconf php${PHP_VERSION}-fpm

# VirtualHost
cp resources/ssl.debian.conf /etc/apache2/mods-available/ssl.conf
cp resources/vpn.example.debian.conf "/etc/apache2/sites-available/${WEB_FQDN}.conf"
cp resources/localhost.debian.conf /etc/apache2/sites-available/localhost.conf

# update hostname
sed -i "s/vpn.example/${WEB_FQDN}/" "/etc/apache2/sites-available/${WEB_FQDN}.conf"

a2enconf vpn-user-portal
a2ensite "${WEB_FQDN}" localhost
a2dissite 000-default

systemctl restart apache2

###############################################################################
# VPN-USER-PORTAL
###############################################################################

# update hostname of VPN server
sed -i "s/vpn.example/${WEB_FQDN}/" "/etc/vpn-user-portal/config.php"

# update the default IP ranges for the profile
# on Debian we can use ipcalc-ng
sed -i "s|10.42.42.0|$(ipcalc-ng -4 -r 24 -n --no-decorate)|" "/etc/vpn-user-portal/config.php"
sed -i "s|fd42::|$(ipcalc-ng -6 -r 64 -n --no-decorate)|" "/etc/vpn-user-portal/config.php"
sed -i "s|10.43.43.0|$(ipcalc-ng -4 -r 24 -n --no-decorate)|" "/etc/vpn-user-portal/config.php"
sed -i "s|fd43::|$(ipcalc-ng -6 -r 64 -n --no-decorate)|" "/etc/vpn-user-portal/config.php"

###############################################################################
# UPDATE SECRETS
###############################################################################

#cp /etc/vpn-user-portal/keys/node.0.key /etc/vpn-server-node/keys/node.key

###############################################################################
# DAEMONS
###############################################################################

systemctl enable --now php${PHP_VERSION}-fpm
systemctl enable --now apache2

###############################################################################
# FIREWALL
###############################################################################

cp resources/firewall/controller/iptables  /etc/iptables/rules.v4
cp resources/firewall/controller/ip6tables /etc/iptables/rules.v6

systemctl enable netfilter-persistent
systemctl restart netfilter-persistent

###############################################################################
# USERS
###############################################################################

USER_NAME="vpn"
USER_PASS=$(pwgen 12 -n 1)

sudo -u www-data vpn-user-portal-account --add "${USER_NAME}" --password "${USER_PASS}"

echo "########################################################################"
echo "# Portal"
echo "# ======"
echo "#     https://${WEB_FQDN}/"
echo "#         User Name: ${USER_NAME}"
echo "#         User Pass: ${USER_PASS}"
echo "#"
echo "# Admin"
echo "# ====="
echo "# Add 'vpn' to 'adminUserIdList' in /etc/vpn-user-portal/config.php in"
echo "# order to make yourself an admin in the portal."
echo "########################################################################"
