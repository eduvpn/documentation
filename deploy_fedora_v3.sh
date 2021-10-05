#!/bin/sh

#
# Deploy a single VPN machine on Fedora
#

###############################################################################
# VARIABLES
###############################################################################

MACHINE_HOSTNAME=$(hostname -f)

# DNS name of the Web Server
printf "DNS name of the Web Server [%s]: " "${MACHINE_HOSTNAME}"; read -r WEB_FQDN
WEB_FQDN=${WEB_FQDN:-${MACHINE_HOSTNAME}}

# Try to detect external "Default Gateway" Interface, but allow admin override
EXTERNAL_IF=$(ip -4 ro show default | tail -1 | awk {'print $5'})
printf "External Network Interface [%s]: " "${EXTERNAL_IF}"; read -r EXTERNAL_IF

###############################################################################
# SYSTEM
###############################################################################

# SELinux enabled?

if ! /usr/sbin/selinuxenabled
then
    echo "Please **ENABLE** SELinux before running this script!"
    exit 1
fi

PACKAGE_MANAGER=/usr/bin/dnf

###############################################################################
# SOFTWARE
###############################################################################

# disable and stop existing firewalling
systemctl disable --now firewalld >/dev/null 2>/dev/null || true
systemctl disable --now iptables >/dev/null 2>/dev/null || true
systemctl disable --now ip6tables >/dev/null 2>/dev/null || true

cat << EOF > /etc/yum.repos.d/eduVPN-v3.repo
[eduVPN-v3]
name=eduVPN Development Packages (Fedora \$releasever)
baseurl=https://repo.tuxed.net/eduVPN/v3/rpm/fedora-\$releasever-\$basearch
gpgcheck=1
gpgkey=https://repo.tuxed.net/fkooman+repo@tuxed.net.asc
enabled=1
EOF

# install software (dependencies)
${PACKAGE_MANAGER} -y install mod_ssl php-opcache httpd iptables-nft pwgen \
    iptables-services php-fpm php-cli policycoreutils-python-utils chrony \
    wireguard-tools

# install software (VPN packages)
${PACKAGE_MANAGER} -y install vpn-server-node vpn-user-portal \
    vpn-maint-scripts vpn-daemon

###############################################################################
# SELINUX
###############################################################################

# allow Apache to connect to PHP-FPM
setsebool -P httpd_can_network_connect=1

# allow OpenVPN to bind to additional ports for client connections
semanage port -a -t openvpn_port_t -p tcp 1195-1258
semanage port -a -t openvpn_port_t -p udp 1195-1258

###############################################################################
# APACHE
###############################################################################

# Use a hardened ssl.conf instead of the default, gives A+ on
# https://www.ssllabs.com/ssltest/
cp resources/ssl.fedora.v3.conf /etc/httpd/conf.d/ssl.conf
cp resources/localhost.centos.conf /etc/httpd/conf.d/localhost.conf

# VirtualHost
cp resources/vpn.example.centos.conf "/etc/httpd/conf.d/${WEB_FQDN}.conf"
sed -i "s/vpn.example/${WEB_FQDN}/" "/etc/httpd/conf.d/${WEB_FQDN}.conf"

###############################################################################
# PHP
###############################################################################

cat << EOF > /etc/php.d/70-vpn.ini
# @see https://www.php.net/manual/en/session.security.ini.php
# NOTE: we set the cookie parameters ourselves in PHP code
session.cookie_lifetime=0
session.use_cookies=On
session.use_only_cookies=On
session.use_strict_mode=On
session.use_trans_sid=Off
session.sid_length=48
session.sid_bits_per_character=6
EOF

###############################################################################
# VPN-USER-PORTAL
###############################################################################

# update hostname of VPN server
sed -i "s/vpn.example/${WEB_FQDN}/" "/etc/vpn-user-portal/config.php"

# DB init
# XXX would be nice if we could avoid this
sudo -u apache /usr/libexec/vpn-user-portal/init

# update the default IP ranges for the profiles
sed -i "s|10.42.42.0/24|$(vpn-user-portal-suggest-ip -4)|" "/etc/vpn-user-portal/config.php"
sed -i "s|fd42::/64|$(vpn-user-portal-suggest-ip -6)|" "/etc/vpn-user-portal/config.php"
sed -i "s|10.43.43.0/24|$(vpn-user-portal-suggest-ip -4)|" "/etc/vpn-user-portal/config.php"
sed -i "s|fd43::/64|$(vpn-user-portal-suggest-ip -6)|" "/etc/vpn-user-portal/config.php"

###############################################################################
# NETWORK
###############################################################################

cat << EOF > /etc/sysctl.d/70-vpn.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
# **ONLY** needed for IPv6 configuration through auto configuration. Do **NOT**
# use this in production as that requires STATIC IP addressess!
net.ipv6.conf.${EXTERNAL_IF}.accept_ra = 2
EOF

sysctl --system

###############################################################################
# UPDATE SECRETS
###############################################################################

cp /etc/vpn-user-portal/node.key /etc/vpn-server-node/node.key

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
    -keyout "/etc/pki/tls/private/${WEB_FQDN}.key" \
    -out "/etc/pki/tls/certs/${WEB_FQDN}.crt" \
    -days 90

###############################################################################
# WireGuard
###############################################################################

# generate the private key and store it out of reach of the web server, make
# the public key available to the portal
wg genkey | tee /etc/wireguard/private.key | wg pubkey > /etc/vpn-user-portal/wireguard.key

###############################################################################
# DAEMONS
###############################################################################

systemctl enable --now php-fpm
systemctl enable --now httpd
systemctl enable --now vpn-daemon

###############################################################################
# VPN SERVER CONFIG
###############################################################################

vpn-maint-apply-changes

###############################################################################
# FIREWALL
###############################################################################

cp resources/firewall/iptables.v3  /etc/sysconfig/iptables
cp resources/firewall/ip6tables.v3 /etc/sysconfig/ip6tables

systemctl enable --now iptables
systemctl enable --now ip6tables

###############################################################################
# USERS
###############################################################################

USER_NAME="vpn"
USER_PASS=$(pwgen 12 -n 1)

sudo -u apache vpn-user-portal-add-user --user "${USER_NAME}" --pass "${USER_PASS}"

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
