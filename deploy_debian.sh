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

# Try to detect external "Default Gateway" Interface, but allow admin override
EXTERNAL_IF=$(ip -4 ro show default | tail -1 | awk {'print $5'})
printf "External Network Interface [%s]: " "${EXTERNAL_IF}"; read -r EXT_IF
EXTERNAL_IF=${EXT_IF:-${EXTERNAL_IF}}

###############################################################################
# SOFTWARE
###############################################################################

apt update
apt install -y apt-transport-https curl apache2 php-fpm pwgen \
    iptables-persistent sudo lsb-release ipcalc-ng tmux

DEBIAN_CODE_NAME=$(/usr/bin/lsb_release -cs)
PHP_VERSION=$(/usr/sbin/phpquery -V)

curl -o /etc/apt/trusted.gpg.d/fkooman.asc https://repo.tuxed.net/fkooman+repo@tuxed.net.asc
echo "deb https://repo.tuxed.net/eduVPN/v3-dev/deb ${DEBIAN_CODE_NAME} main" | tee -a /etc/apt/sources.list.d/eduVPN_v3-dev.list

apt update

# install software (VPN packages)
apt install -y vpn-user-portal vpn-server-node vpn-maint-scripts

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
# NETWORK
###############################################################################

cat << EOF > /etc/sysctl.d/70-vpn.conf
# **ONLY** needed for IPv6 configuration through auto configuration. Do **NOT**
# use this in production, you SHOULD be using STATIC addresses!
net.ipv6.conf.${EXTERNAL_IF}.accept_ra = 2

# enable IPv4 and IPv6 forwarding
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
EOF

sysctl --system

###############################################################################
# UPDATE SECRETS
###############################################################################

cp /etc/vpn-user-portal/keys/node.0.key /etc/vpn-server-node/keys/node.key

###############################################################################
# DAEMONS
###############################################################################

systemctl enable --now php${PHP_VERSION}-fpm
systemctl enable --now apache2
systemctl enable --now vpn-daemon
systemctl enable --now crond

###############################################################################
# VPN SERVER CONFIG
###############################################################################

# increase the allowed number of processes for the OpenVPN service
mkdir -p /etc/systemd/system/openvpn-server@.service.d
cat << EOF > /etc/systemd/system/openvpn-server@.service.d/override.conf
[Service]
LimitNPROC=127
EOF

vpn-maint-apply-changes

###############################################################################
# FIREWALL
###############################################################################

cp resources/firewall/iptables  /etc/iptables/rules.v4
cp resources/firewall/ip6tables /etc/iptables/rules.v6
sed -i "s|-o eth0|-o ${EXTERNAL_IF}|" /etc/iptables/rules.v4
sed -i "s|-o eth0|-o ${EXTERNAL_IF}|" /etc/iptables/rules.v6

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
