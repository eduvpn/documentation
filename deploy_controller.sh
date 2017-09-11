#!/bin/sh

#
# Deploy a VPN controller
#

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
    pwgen certbot open-vm-tools php-fpm php-cli policycoreutils-python chrony

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

echo "########################################################################"
echo "# Please modify:"
echo "#"
echo "#     /etc/httpd/conf.d/vpn-server-api.conf"
echo "#"
echo "# Make 'Require ip' list the IPv4 & IPv6 addresses of the VPN server"
echo "# node(s) and restart Apache:"
echo "#"
echo "#     systemctl restart httpd"
echo "#"
echo "########################################################################"

# ALL DONE!
