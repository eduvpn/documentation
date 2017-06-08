#!/bin/sh

#
# Deploy Controller
#

###############################################################################
# VARIABLES
###############################################################################

# **NOTE**: make sure WEB_FQDN and VPN_FQDN are valid DNS names with 
# appropriate A (and AAAA) records!

# VARIABLES
WEB_FQDN=vpn.example
VPN_FQDN=internet.${WEB_FQDN}

# The interface that connects to "the Internet"
EXTERNAL_IF=eth0

# The email address you want to use for Let's Encrypt (you won't be spammed)
LETSENCRYPT_MAIL=admin@example.org

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
${PACKAGE_MANAGER} -y install firewalld mod_ssl php-opcache httpd pwgen \
    certbot open-vm-tools php-fpm php-cli policycoreutils-python

# install software (VPN packages)
${PACKAGE_MANAGER} -y install vpn-server-api vpn-admin-portal vpn-user-portal

###############################################################################
# FIREWALL
###############################################################################

systemctl enable --now firewalld
firewall-cmd --permanent --zone=public --add-service=http --add-service=https
firewall-cmd --zone=public --add-service=http --add-service=https

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

# XXX update the httpd config thingies to not set the "default" instance_id

###############################################################################
# PHP
###############################################################################

# switch to unix socket, default in newer PHP versions, but not on CentOS 7
sed -i "s|^listen = 127.0.0.1:9000$|listen = /run/php-fpm/www.sock|" /etc/php-fpm.d/www.conf

# timezone
cp resources/70-timezone.ini /etc/php.d/70-timezone.ini
# session hardening
cp resources/75-session.ini /etc/php.d/75-session.ini

# work around to create the session directory, otherwise we have to install
# the PHP package, this is only on CentOS
mkdir -p /var/lib/php/session
chown -R root.apache /var/lib/php/session
chmod 0770 /var/lib/php/session
restorecon -R /var/lib/php

###############################################################################
# VPN-SERVER-API
###############################################################################

mkdir -p /etc/vpn-server-api/${WEB_FQDN}
cp /etc/vpn-server-api/default/config.php /etc/vpn-server-api/${WEB_FQDN}/config.php

# update the IPv4 CIDR and IPv6 prefix to random IP ranges and set the extIf
vpn-server-api-update-ip --instance ${WEB_FQDN} --profile internet --host ${VPN_FQDN} --ext ${EXTERNAL_IF}

sed -i "s|'managementIp' => '127.0.0.1'|//'managementIp' => '127.0.0.1'|" /etc/vpn-server-api/${WEB_FQDN}/config.php

# init the CA
sudo -u apache vpn-server-api-init --instance ${WEB_FQDN}

###############################################################################
# VPN-ADMIN-PORTAL
###############################################################################

mkdir -p /etc/vpn-admin-portal/${WEB_FQDN}
cp /etc/vpn-admin-portal/default/config.php /etc/vpn-admin-portal/${WEB_FQDN}/config.php

sed -i "s|http://localhost/vpn-server-api/api.php|https://${WEB_FQDN}/vpn-server-api/api.php|" /etc/vpn-admin-portal/default/config.php

###############################################################################
# VPN-USER-PORTAL
###############################################################################

mkdir -p /etc/vpn-user-portal/${WEB_FQDN}
cp /etc/vpn-user-portal/default/config.php /etc/vpn-user-portal/${WEB_FQDN}/config.php

sed -i "s|http://localhost/vpn-server-api/api.php|https://${WEB_FQDN}/vpn-server-api/api.php|" /etc/vpn-user-portal/default/config.php

# generate OAuth keypair
vpn-user-portal-init --instance ${WEB_FQDN}

###############################################################################
# UPDATE SECRETS
###############################################################################

# update API secret
vpn-server-api-update-api-secrets --instance ${WEB_FQDN}

###############################################################################
# LET'S ENCRYPT / CERTBOT
###############################################################################

certbot register --agree-tos --no-eff-email -m ${LETSENCRYPT_MAIL}
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
# POST INSTALL
###############################################################################

sed -i "s/--instance default/--instance ${WEB_FQDN}/" /etc/cron.d/vpn-server-api
sed -i "s/--instance default/--instance ${WEB_FQDN}/" /etc/cron.d/vpn-user-portal

###############################################################################
# USERS
###############################################################################

USER_PASS=$(pwgen 12 -n 1)
ADMIN_PASS=$(pwgen 12 -n 1)
vpn-user-portal-add-user  --instance ${WEB_FQDN} --user me    --pass "${USER_PASS}"
vpn-admin-portal-add-user --instance ${WEB_FQDN} --user admin --pass "${ADMIN_PASS}"

API_SECRET=$(grep vpn-server-node /etc/vpn-server-api/${WEB_FQDN}/config.php | cut -d "'" -f 4)

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
