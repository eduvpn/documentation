#!/bin/sh

#
# Deploy a single VPN machine
#

###############################################################################
# VARIABLES
###############################################################################

# DNS name of the Web Server
WEB_FQDN=vpn.example

# DNS name of the OpenVPN Server
# use different name if you want to allow moving the OpenVPN processes to 
# another machine in the future without breaking client configuration files
VPN_FQDN=${WEB_FQDN}
#VPN_FQDN=internet.${WEB_FQDN}

# The interface that connects to "the Internet" (for firewall rules)
EXTERNAL_IF=eth0

###############################################################################
# SYSTEM
###############################################################################

# SELinux enabled?

if ! /usr/sbin/selinuxenabled
then
    echo "Please **ENABLE** SELinux before running this script!"
    exit 1
fi

PACKAGE_MANAGER=/usr/bin/yum

###############################################################################
# SOFTWARE
###############################################################################

# disable and stop existing firewalling
systemctl disable --now firewalld
systemctl disable --now iptables
systemctl disable --now ip6tables

# RHEL 7
# subscription-manager repos --enable=rhel-7-server-optional-rpms
# subscription-manager repos --enable=rhel-7-server-extras-rpms
# ${PACKAGE_MANAGER} -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

# CentOS 7
# enable EPEL
${PACKAGE_MANAGER} -y install epel-release

# Production RPMs
curl -L -o /etc/yum.repos.d/eduVPN.repo \
    https://repo.eduvpn.org/rpm/eduVPN.repo

# Development RPMs (COPR)
#curl -L -o /etc/yum.repos.d/eduVPN.repo \
#   https://copr.fedorainfracloud.org/coprs/fkooman/eduvpn-testing/repo/epel-7/fkooman-eduvpn-testing-epel-7.repo

# install software (dependencies)
${PACKAGE_MANAGER} -y install mod_ssl php-opcache httpd iptables pwgen \
    iptables-services php-fpm php-cli policycoreutils-python chrony

# install software (VPN packages)
${PACKAGE_MANAGER} -y install vpn-server-node vpn-server-api vpn-admin-portal \
    vpn-user-portal

###############################################################################
# SELINUX
###############################################################################

# allow Apache to connect to PHP-FPM
setsebool -P httpd_can_network_connect=1

# allow OpenVPN to bind to the management ports
semanage port -a -t openvpn_port_t -p tcp 11940-12195

###############################################################################
# APACHE
###############################################################################

# Use a hardended ssl.conf instead of the default, gives A+ on
# https://www.ssllabs.com/ssltest/
cp resources/ssl.conf /etc/httpd/conf.d/ssl.conf
cp resources/localhost.conf /etc/httpd/conf.d/localhost.conf

# Switch to MPM event (https://httpd.apache.org/docs/2.4/mod/event.html)
sed -i "s|^LoadModule mpm_prefork_module modules/mod_mpm_prefork.so$|#LoadModule mpm_prefork_module modules/mod_mpm_prefork.so|" /etc/httpd/conf.modules.d/00-mpm.conf
sed -i "s|^#LoadModule mpm_event_module modules/mod_mpm_event.so$|LoadModule mpm_event_module modules/mod_mpm_event.so|" /etc/httpd/conf.modules.d/00-mpm.conf

# php-fpm configuration (taken from Fedora php-fpm package, only required on
# CentOS)
cp resources/php.conf /etc/httpd/conf.d/php.conf

# VirtualHost
cp resources/vpn.example.conf /etc/httpd/conf.d/${WEB_FQDN}.conf
sed -i "s/vpn.example/${WEB_FQDN}/" /etc/httpd/conf.d/${WEB_FQDN}.conf

###############################################################################
# PHP
###############################################################################

# switch to unix socket and secure it, the default in newer PHP versions, but 
# not on CentOS 7
sed -i "s|^listen = 127.0.0.1:9000$|listen = /run/php-fpm/www.sock|" /etc/php-fpm.d/www.conf
sed -i "s|;listen.mode = 0666|listen.mode = 0660|" /etc/php-fpm.d/www.conf
sed -i "s|;listen.group = nobody|listen.group = apache|" /etc/php-fpm.d/www.conf

# set timezone to UTC
cp resources/70-timezone.ini /etc/php.d/70-timezone.ini
# session hardening
cp resources/75-session.centos.ini /etc/php.d/75-session.ini

# work around to create the session directory, otherwise we have to install
# the PHP package, this is only on CentOS
mkdir -p /var/lib/php/session
chown -R root.apache /var/lib/php/session
chmod 0770 /var/lib/php/session
restorecon -R /var/lib/php/session

###############################################################################
# VPN-SERVER-API
###############################################################################

# update the IPv4 CIDR and IPv6 prefix to random IP ranges and set the extIf
vpn-server-api-update-ip --profile internet --host ${VPN_FQDN} --ext ${EXTERNAL_IF}

# initialize the CA
sudo -u apache vpn-server-api-init

###############################################################################
# VPN-USER-PORTAL
###############################################################################

# generate OAuth public/private keys
sudo -u apache vpn-user-portal-init

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
# CERTIFICATE
###############################################################################

# generate self signed certificate and key
openssl req \
    -nodes \
    -subj "/CN=${WEB_FQDN}" \
    -x509 \
    -sha256 \
    -newkey rsa:2048 \
    -keyout /etc/pki/tls/private/${WEB_FQDN}.key \
    -out /etc/pki/tls/certs/${WEB_FQDN}.crt \
    -days 90

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

systemctl enable --now php-fpm
systemctl enable --now httpd

###############################################################################
# OPENVPN SERVER CONFIG
###############################################################################

# NOTE: the openvpn-server systemd unit file only allows 10 OpenVPN processes
# by default! 

# generate the OpenVPN server configuration files and certificates
vpn-server-node-server-config --generate

# enable and start OpenVPN
systemctl enable --now openvpn-server@default-internet-0
systemctl enable --now openvpn-server@default-internet-1

###############################################################################
# FIREWALL
###############################################################################

# generate and install the firewall
vpn-server-node-generate-firewall --install

systemctl enable --now iptables
systemctl enable --now ip6tables

###############################################################################
# USERS
###############################################################################

USER_PASS=$(pwgen 12 -n 1)
ADMIN_PASS=$(pwgen 12 -n 1)
vpn-user-portal-add-user  --user me    --pass "${USER_PASS}"
vpn-admin-portal-add-user --user admin --pass "${ADMIN_PASS}"

###############################################################################
# SHOW INFO
###############################################################################

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
