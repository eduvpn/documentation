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

VPN_STABLE_REPO=1
VPN_DEV_REPO=${VPN_DEV_REPO:-0}
if [ "${VPN_DEV_REPO}" = 1 ]
then
    VPN_STABLE_REPO=0
fi

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

# import PGP key and add repository
rpm --import "https://repo.eduvpn.org/v2/rpm/centos+20210419@eduvpn.org.asc"
cat << EOF > /etc/yum.repos.d/LC-v2.repo
[LC-v2]
name=VPN Stable Packages (Fedora \$releasever)
baseurl=https://repo.letsconnect-vpn.org/2/rpm/fedora-\$releasever-\$basearch
gpgcheck=1
enabled=${VPN_STABLE_REPO}
EOF

cat << EOF > /etc/yum.repos.d/eduVPN_v2-dev.repo
[eduVPN_v2-dev]
name=eduVPN 2.x Development Packages (Fedora \$releasever)
baseurl=https://repo.tuxed.net/eduVPN/v2-dev/rpm/fedora-\$releasever-\$basearch
gpgcheck=1
gpgkey=https://repo.tuxed.net/fkooman+repo@tuxed.net.asc
enabled=${VPN_DEV_REPO}
EOF

# install software (dependencies)
${PACKAGE_MANAGER} -y install mod_ssl php-opcache httpd iptables pwgen \
    iptables-services php-fpm php-cli policycoreutils-python-utils chrony

# install software (VPN packages)
${PACKAGE_MANAGER} -y install vpn-server-node vpn-server-api vpn-user-portal \
    vpn-maint-scripts

###############################################################################
# SELINUX
###############################################################################

# allow Apache to connect to PHP-FPM
setsebool -P httpd_can_network_connect=1

# allow OpenVPN to bind to the management ports
semanage port -a -t openvpn_port_t -p tcp 11940-16036

# allow OpenVPN to bind to additional ports for client connections
semanage port -a -t openvpn_port_t -p tcp 1195-5290
semanage port -a -t openvpn_port_t -p udp 1195-5290

###############################################################################
# APACHE
###############################################################################

# Use a hardened ssl.conf instead of the default, gives A+ on
# https://www.ssllabs.com/ssltest/
cp resources/ssl.fedora.conf /etc/httpd/conf.d/ssl.conf
cp resources/localhost.centos.conf /etc/httpd/conf.d/localhost.conf

# VirtualHost
cp resources/vpn.example.centos.conf "/etc/httpd/conf.d/${WEB_FQDN}.conf"
sed -i "s/vpn.example/${WEB_FQDN}/" "/etc/httpd/conf.d/${WEB_FQDN}.conf"

###############################################################################
# PHP
###############################################################################

# set timezone to UTC
cp resources/70-timezone.ini /etc/php.d/70-timezone.ini

###############################################################################
# VPN-SERVER-API
###############################################################################

# update hostname of VPN server
sed -i "s/vpn.example/${WEB_FQDN}/" "/etc/vpn-server-api/config.php"

# update the default IP ranges
sed -i "s|10.0.0.0/25|$(vpn-server-api-suggest-ip -4)|" "/etc/vpn-server-api/config.php"
sed -i "s|fd00:4242:4242:4242::/64|$(vpn-server-api-suggest-ip -6)|" "/etc/vpn-server-api/config.php"

# initialize the CA
sudo -u apache vpn-server-api-init

###############################################################################
# VPN-USER-PORTAL
###############################################################################

# DB init
sudo -u apache vpn-user-portal-init

###############################################################################
# NETWORK
###############################################################################

cat << EOF > /etc/sysctl.d/70-vpn.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
# allow RA for IPv6 which is disabled by default when enabling IPv6 forwarding 
# **REMOVE** for static IPv6 configurations!
net.ipv6.conf.all.accept_ra = 2
EOF

sysctl --system

###############################################################################
# UPDATE SECRETS
###############################################################################

# update internal API secrets from the defaults to something secure
SECRET_PORTAL_API=$(pwgen -s 32 -n 1)
SECRET_NODE_API=$(pwgen -s 32 -n 1)
sed -i "s|XXX-vpn-user-portal/vpn-server-api-XXX|${SECRET_PORTAL_API}|" "/etc/vpn-user-portal/config.php"
sed -i "s|XXX-vpn-server-node/vpn-server-api-XXX|${SECRET_NODE_API}|" "/etc/vpn-server-node/config.php"
sed -i "s|XXX-vpn-user-portal/vpn-server-api-XXX|${SECRET_PORTAL_API}|" "/etc/vpn-server-api/config.php"
sed -i "s|XXX-vpn-server-node/vpn-server-api-XXX|${SECRET_NODE_API}|" "/etc/vpn-server-api/config.php"

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
# DAEMONS
###############################################################################

systemctl enable --now php-fpm
systemctl enable --now httpd

###############################################################################
# OPENVPN SERVER CONFIG
###############################################################################

# NOTE: the openvpn-server systemd unit file only allows 10 OpenVPN processes
# by default! 

# generate (new) OpenVPN server configuration files and start OpenVPN
vpn-maint-apply-changes

###############################################################################
# FIREWALL
###############################################################################

cp resources/firewall/iptables  /etc/sysconfig/iptables
cp resources/firewall/ip6tables /etc/sysconfig/ip6tables

systemctl enable --now iptables
systemctl enable --now ip6tables

###############################################################################
# USERS
###############################################################################

REGULAR_USER="demo"
REGULAR_USER_PASS=$(pwgen 12 -n 1)

# the "admin" user is a special user, listed by ID to have access to "admin" 
# functionality in /etc/vpn-user-portal/config.php (adminUserIdList)
ADMIN_USER="admin"
ADMIN_USER_PASS=$(pwgen 12 -n 1)

sudo -u apache vpn-user-portal-add-user --user "${REGULAR_USER}" --pass "${REGULAR_USER_PASS}"
sudo -u apache vpn-user-portal-add-user --user "${ADMIN_USER}" --pass "${ADMIN_USER_PASS}"

###############################################################################
# SHOW INFO
###############################################################################

echo "########################################################################"
echo "# Portal"
echo "#     https://${WEB_FQDN}/"
echo "#         Regular User: ${REGULAR_USER}"
echo "#         Regular User Pass: ${REGULAR_USER_PASS}"
echo "#"
echo "#         Admin User: ${ADMIN_USER}"
echo "#         Admin User Pass: ${ADMIN_USER_PASS}"
echo "########################################################################"
