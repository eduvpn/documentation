#!/bin/sh

#
# Deploy a VPN controller
#

# XXX 
# * the public IP addresses from the node need to be whitelisted in the 
#   Apache config of vpn-server-api
#
# 

###############################################################################
# VARIABLES
###############################################################################

# **NOTE**: make sure WEB_FQDN and VPN_FQDN are valid DNS names with 
# appropriate A (and AAAA) records!

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
# XXX this is on the VPN node! not on the controller node!
EXTERNAL_IF=eth0

# the management IP of the first node
MANAGEMENT_IP=10.42.1.2

###############################################################################
# SYSTEM
###############################################################################

# SELinux enabled?
/usr/sbin/selinuxenabled
if [ "$?" -ne 0 ]
then
    echo "Please enable SELinux before running this script!"
    exit 1
fi

PACKAGE_MANAGER=/usr/bin/yum

###############################################################################
# SOFTWARE
###############################################################################

# enable EPEL
${PACKAGE_MANAGER} -y install epel-release

curl -L -o /etc/yum.repos.d/fkooman-eduvpn-testing-epel-7.repo \
    https://copr.fedorainfracloud.org/coprs/fkooman/eduvpn-testing/repo/epel-7/fkooman-eduvpn-testing-epel-7.repo

# install software (dependencies)
${PACKAGE_MANAGER} -y install mod_ssl firewalld php-opcache httpd \
    pwgen certbot open-vm-tools php-fpm php-cli \
    policycoreutils-python

# install software (VPN packages)
${PACKAGE_MANAGER} -y install vpn-server-api vpn-admin-portal vpn-user-portal

###############################################################################
# SELINUX
###############################################################################

# allow Apache to connect to PHP-FPM
setsebool -P httpd_can_network_connect=1

###############################################################################
# APACHE
###############################################################################

# Use a hardended ssl.conf instead of the default, gives A+ on
# https://www.ssllabs.com/ssltest/
cp resources/ssl.conf /etc/httpd/conf.d/ssl.conf

# VirtualHost
cp resources/vpn.example.conf /etc/httpd/conf.d/${WEB_FQDN}.conf
sed -i "s/vpn.example/${WEB_FQDN}/" /etc/httpd/conf.d/${WEB_FQDN}.conf

###############################################################################
# PHP
###############################################################################

# switch to unix socket, default in newer PHP versions, but not on CentOS 7
sed -i "s|^listen = 127.0.0.1:9000$|listen = /run/php-fpm/www.sock|" /etc/php-fpm.d/www.conf

# set timezone to UTC
cp resources/70-timezone.ini /etc/php.d/70-timezone.ini
# session hardening
cp resources/75-session.ini /etc/php.d/75-session.ini

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
vpn-server-api-update-ip --profile internet --host ${VPN_FQDN} --management-ip ${MANAGEMENT_IP} --ext ${EXTERNAL_IF}

# initialize the CA
sudo -u apache vpn-server-api-init

###############################################################################
# VPN-ADMIN-PORTAL
###############################################################################

sed -i "s|http://localhost/vpn-server-api/api.php|https://${WEB_FQDN}/vpn-server-api/api.php|" /etc/vpn-admin-portal/default/config.php

###############################################################################
# VPN-USER-PORTAL
###############################################################################

sed -i "s|http://localhost/vpn-server-api/api.php|https://${WEB_FQDN}/vpn-server-api/api.php|" /etc/vpn-user-portal/default/config.php

# generate OAuth public/private keys
vpn-user-portal-init

###############################################################################
# UPDATE SECRETS
###############################################################################

# update API secret
vpn-server-api-update-api-secrets

###############################################################################
# LET'S ENCRYPT / CERTBOT
###############################################################################

certbot register ${AGREE_TOS} --no-eff-email -m ${LETSENCRYPT_MAIL}
certbot certonly -n --standalone -d ${WEB_FQDN}

cat << EOF > /etc/sysconfig/certbot
PRE_HOOK="--pre-hook 'systemctl stop httpd'"
POST_HOOK="--post-hook 'systemctl start httpd'"
RENEW_HOOK=""
CERTBOT_ARGS=""
EOF

# enable automatic renewal
systemctl enable --now certbot-renew.timer

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
systemctl enable --now vmtoolsd

###############################################################################
# FIREWALL
###############################################################################

systemctl enable --now firewalld
firewall-cmd --permanent --zone=public --add-service=http --add-service=https
firewall-cmd --zone=public --add-service=http --add-service=https

###############################################################################
# USERS
###############################################################################

USER_PASS=$(pwgen 12 -n 1)
ADMIN_PASS=$(pwgen 12 -n 1)
vpn-user-portal-add-user  --user me    --pass "${USER_PASS}"
vpn-admin-portal-add-user --user admin --pass "${ADMIN_PASS}"

API_SECRET=$(grep vpn-server-node /etc/vpn-server-api/default/config.php | cut -d "'" -f 4)

echo "########################################################################"
echo "# Admin Portal"
echo "#     https://${WEB_FQDN}/vpn-admin-portal"
echo "#         User: admin"
echo "#         Pass: ${ADMIN_PASS}"
echo "# User Portal"
echo "#     https://${WEB_FQDN}/vpn-user-portal"
echo "#         User: me"
echo "#         Pass: ${USER_PASS}"
echo "# API Secret"
echo "#     ${API_SECRET}"
echo "########################################################################"
# ALL DONE!
