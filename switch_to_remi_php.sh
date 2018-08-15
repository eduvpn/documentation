#!/bin/sh

#
# Update a CentOS 7 instance to use a modern PHP version instead of the default 
# PHP 5.4
#

PHP_VERSION=72                  # 7.2
PACKAGE_MANAGER=/usr/bin/yum

# install and enable remi repository
${PACKAGE_MANAGER} install -y yum-utils https://rpms.remirepo.net/enterprise/remi-release-7.rpm
yum-config-manager --enable remi-php${PHP_VERSION} >/dev/null

# remove old php-fpm "www.conf" file before update so we'll get the new one
rm -f /etc/php-fpm.d/www.conf

# install updated packages
${PACKAGE_MANAGER} -y update

# remove PECL sodium module, and use native sodium
${PACKAGE_MANAGER} -y install php-sodium
${PACKAGE_MANAGER} -y remove php-pecl-libsodium

# switch to unix socket and secure it, the default in newer PHP versions, but 
# not on CentOS 7, also not in remi repository
sed -i "s|^listen = 127.0.0.1:9000$|listen = /run/php-fpm/www.sock|" /etc/php-fpm.d/www.conf
sed -i "s|;listen.group = nobody|listen.group = apache|" /etc/php-fpm.d/www.conf

# use Fedora's session hardening now because we have modern PHP!
cp -f resources/75-session.fedora.ini /etc/php.d/75-session.ini

systemctl restart php-fpm
