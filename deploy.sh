#!/bin/sh

# Script to deploy eduvpn on a CentOS >= 7 installation.
#
# Tested on CentOS 7.2
#
# NOTE: make sure you installed all updates:
#     $ sudo yum clean all && sudo yum -y update
#
# NOTE: make sure the HOSTNAME used below can be resolved, either in DNS 
#       or with a /etc/hosts entry, e.g.:
#
#           10.20.30.44 vpn.example
#
# NOTE: edit the variables below if you need to. Set the correct HOSTNAME and
#       the interface connecting to the Internet from your machine
#

###############################################################################
# VARIABLES
###############################################################################

# VARIABLES
HOSTNAME=vpn.example
EXTERNAL_IF=eth0

###############################################################################
# SYSTEM
###############################################################################

# NOP

###############################################################################
# SOFTWARE
###############################################################################

# enable EPEL
sudo yum -y install epel-release

# enable COPR repos
sudo curl -L -o /etc/yum.repos.d/fkooman-php-base-epel-7.repo https://copr.fedorainfracloud.org/coprs/fkooman/php-base/repo/epel-7/fkooman-php-base-epel-7.repo
sudo curl -L -o /etc/yum.repos.d/fkooman-vpn-management-epel-7.repo https://copr.fedorainfracloud.org/coprs/fkooman/vpn-management/repo/epel-7/fkooman-vpn-management-epel-7.repo

# install software
sudo yum -y install openvpn easy-rsa mod_ssl php-opcache httpd openssl \
    policycoreutils-python vpn-server-api vpn-ca-api vpn-admin-portal \
    vpn-user-portal iptables iptables-services patch sniproxy \
    iptables-services php-fpm php-cli php pwgen php-pecl-libsodium

###############################################################################
# CERTIFICATE
###############################################################################

# Generate the private key
sudo openssl genrsa -out /etc/pki/tls/private/${HOSTNAME}.key 4096 
sudo chmod 600 /etc/pki/tls/private/${HOSTNAME}.key

# Create the CSR (can be used to obtain real certificate!)
sudo openssl req -subj "/CN=${HOSTNAME}" -sha256 -new -key /etc/pki/tls/private/${HOSTNAME}.key -out ${HOSTNAME}.csr

# Create the (self signed) certificate and install it
sudo openssl req -subj "/CN=${HOSTNAME}" -sha256 -new -x509 -key /etc/pki/tls/private/${HOSTNAME}.key -out /etc/pki/tls/certs/${HOSTNAME}.crt

###############################################################################
# APACHE
###############################################################################

# Don't have Apache advertise all version details
# https://httpd.apache.org/docs/2.4/mod/core.html#ServerTokens
sudo sh -c 'echo "ServerTokens ProductOnly" > /etc/httpd/conf.d/servertokens.conf'

# We took the default `/etc/httpd/conf.d/ssl.conf` file, hardened it, gives 
# A+ on https://www.ssllabs.com/ssltest/
sudo cp /etc/httpd/conf.d/ssl.conf /etc/httpd/conf.d/ssl.conf.BACKUP
sudo cp resources/ssl.conf /etc/httpd/conf.d/ssl.conf

# VirtualHost
sudo cp resources/vpn.example.conf /etc/httpd/conf.d/${HOSTNAME}.conf
sudo sed -i "s/vpn.example/${HOSTNAME}/" /etc/httpd/conf.d/${HOSTNAME}.conf

# empty the RPM httpd configs instead of deleting as we do not get them back
# on package update
echo "# emptied by deploy.sh" | sudo tee /etc/httpd/conf.d/vpn-server-api.conf >/dev/null
echo "# emptied by deploy.sh" | sudo tee /etc/httpd/conf.d/vpn-ca-api.conf >/dev/null
echo "# emptied by deploy.sh" | sudo tee /etc/httpd/conf.d/vpn-user-portal.conf >/dev/null
echo "# emptied by deploy.sh" | sudo tee /etc/httpd/conf.d/vpn-admin-portal.conf >/dev/null

###############################################################################
# PHP
###############################################################################

# Set PHP timezone, to suppress errors in the log
sudo sed -i 's/;date.timezone =/date.timezone = UTC/' /etc/php.ini

#https://secure.php.net/manual/en/ini.core.php#ini.expose-php
sudo sed -i 's/expose_php = On/expose_php = Off/' /etc/php.ini

# more secure PHP sessions
# https://paragonie.com/blog/2015/04/fast-track-safe-and-secure-php-sessions
sudo sed -i 's/session.hash_function = 0/session.hash_function = sha256/' /etc/php.ini
sudo sed -i 's/;session.entropy_length = 32/session.entropy_length = 32/' /etc/php.ini

# recommendation from https://php.net/manual/en/opcache.installation.php
sudo sed -i 's/;opcache.revalidate_freq=2/opcache.revalidate_freq=60/' /etc/php.d/opcache.ini

###############################################################################
# vpn-ca-api
###############################################################################

# initialize the CA
sudo -u apache vpn-ca-api-init

# allow vpn-ca-api to run Easy-RSA scripts
sudo setsebool -P httpd_unified 1

###############################################################################
# VPN-SERVER-API
###############################################################################

# we also want to connect to the second OpenVPN instance
sudo sed -i 's|#- id: TCP|- id: TCP|' /etc/vpn-server-api/config.yaml
sudo sed -i "s|#  socket: 'tcp://localhost:7506'|  socket: 'tcp://localhost:7506'|" /etc/vpn-server-api/config.yaml

# allow vpn-server-api to connect to OpenVPN management interface
sudo setsebool -P httpd_can_network_connect=on

# we take the CRL from vpn-ca-api and install it in vpn-server-api so 
# OpenVPN will start
sudo -u apache cp /var/lib/vpn-ca-api/easy-rsa/pki/crl.pem /var/lib/vpn-server-api/ca.crl
sudo chmod 0644 /var/lib/vpn-server-api/ca.crl

# create a data directory for the connection log database and pool, initialize 
# the database and restore the SELinux context
sudo mkdir -p /var/lib/openvpn/pool
sudo chown -R openvpn.openvpn /var/lib/openvpn
sudo -u openvpn /usr/bin/vpn-server-api-init
sudo restorecon -R /var/lib/openvpn

# create directory for CN configurations
sudo -u apache mkdir -p /var/lib/vpn-server-api/config

# allow Apache to read the openvpn_var_lib_t sqlite file
checkmodule -M -m -o resources/httpd-allow-openvpn-var-lib-t-read.mod resources/httpd-allow-openvpn-var-lib-t-read.te
semodule_package -o resources/httpd-allow-openvpn-var-lib-t-read.pp -m resources/httpd-allow-openvpn-var-lib-t-read.mod 
sudo semodule -i resources/httpd-allow-openvpn-var-lib-t-read.pp

# install a crontab to cleanup the connection log database every day
# (remove entries older than one month)
echo '@daily openvpn vpn-server-api-housekeeping' | sudo tee /etc/cron.d/vpn-server-api-housekeeping >/dev/null

###############################################################################
# VPN-ADMIN-PORTAL
###############################################################################

# enable template cache
sudo sed -i "s/#templateCache/templateCache/" /etc/vpn-admin-portal/config.yaml

###############################################################################
# VPN-USER-PORTAL
###############################################################################

sudo -u apache vpn-user-portal-init

# enable template cache
sudo sed -i "s/#templateCache/templateCache/" /etc/vpn-user-portal/config.yaml

# copy the default config templates
sudo mkdir /etc/vpn-user-portal/views
sudo cp /usr/share/vpn-user-portal/views/client.twig /etc/vpn-user-portal/views

# update hostname in client.twig
sudo sed -i "s/remote vpn.example 1194 udp/remote ${HOSTNAME} 1194 udp/" /etc/vpn-user-portal/views/client.twig
sudo sed -i "s/remote vpn.example 443 tcp/remote ${HOSTNAME} 443 tcp/" /etc/vpn-user-portal/views/client.twig

###############################################################################
# OPENVPN
###############################################################################

# allow OpenVPN to listen on its management ports
sudo semanage port -a -t openvpn_port_t -p tcp 7505-7506

# allow OpenVPN to read the CRL from vpn-server-api
checkmodule -M -m -o resources/openvpn-allow-server-api-read.mod resources/openvpn-allow-server-api-read.te 
semodule_package -o resources/openvpn-allow-server-api-read.pp -m resources/openvpn-allow-server-api-read.mod 
sudo semodule -i resources/openvpn-allow-server-api-read.pp

# allow OpenVPN to execute sudo for setting routes
checkmodule -M -m -o resources/openvpn-allow-sudo.mod resources/openvpn-allow-sudo.te 
semodule_package -o resources/openvpn-allow-sudo.pp -m resources/openvpn-allow-sudo.mod 
sudo semodule -i resources/openvpn-allow-sudo.pp

# enable forwarding
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf >/dev/null
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.conf >/dev/null

# forwarding disables accepting RAs on our external interface, so we have to 
# explicitly enable it here to make IPv6 work
echo "net.ipv6.conf.${EXTERNAL_IF}.accept_ra = 2" | sudo tee -a /etc/sysctl.conf >/dev/null
sudo sysctl -p

# set sane ARP responses on interfaces
# XXX maybe use "default" instead of all?
# XXX enable it
#echo "net.ipv4.conf.all.arp_announce = 2" | sudo tee -a /etc/sysctl.conf >/dev/null
#echo "net.ipv4.conf.all.arp_notify = 1" | sudo tee -a /etc/sysctl.conf >/dev/null
#echo "net.ipv4.conf.all.arp_ignore=1" | sudo tee -a /etc/sysctl.conf >/dev/null

# allow OpenVPN user to run /sbin/ip 
echo "openvpn ALL=(ALL:ALL) NOPASSWD:/sbin/ip" | sudo tee /etc/sudoers.d/openvpn >/dev/null
# disable requiretty, https://bugzilla.redhat.com/show_bug.cgi?id=1020147
sudo sed -i "s/Defaults    requiretty/#Defaults    requiretty/" /etc/sudoers

###############################################################################
# SNIPROXY
###############################################################################

# install the config file
sudo cp resources/sniproxy.conf /etc/sniproxy.conf
sudo sed -i "s/vpn.example/${HOSTNAME}/" /etc/sniproxy.conf

###############################################################################
# UPDATE SECRETS
###############################################################################

# update API secret
sudo php resources/update_api_secret.php

###############################################################################
# DAEMONS
###############################################################################

sudo systemctl enable php-fpm
sudo systemctl enable httpd
sudo systemctl enable sniproxy

# start services
sudo systemctl start php-fpm
sudo systemctl start httpd
sudo systemctl start sniproxy

###############################################################################
# OPENVPN SERVER CONFIG
###############################################################################

# generate the server configuration files
echo "**** GENERATING SERVER CONFIG, THIS WILL TAKE A LONG TIME... ****"
sudo vpn-server-api-server-config ${HOSTNAME} 
sudo chmod 0600 /etc/openvpn/*.conf

# enable and start OpenVPN
sudo systemctl enable openvpn@server-udp
sudo systemctl enable openvpn@server-tcp
sudo systemctl start openvpn@server-udp
sudo systemctl start openvpn@server-tcp

###############################################################################
# FIREWALL
###############################################################################

# the firewall is generated based on the /etc/vpn-server-api/ip.yaml file
sudo vpn-server-api-generate-firewall --nat --install ${EXTERNAL_IF}

sudo systemctl enable iptables
sudo systemctl enable ip6tables

# flush existing firewall rules if they exist and activate the new ones
sudo systemctl restart iptables
sudo systemctl restart ip6tables

###############################################################################
# POST INSTALL
###############################################################################

# Copy index page
sudo mkdir -p /var/www/${HOSTNAME}
sudo cp resources/index.html /var/www/${HOSTNAME}/index.html
sudo sed -i "s/vpn.example/${HOSTNAME}/" /var/www/${HOSTNAME}/index.html

# adding users
USER_PASS=`pwgen 12 -n 1`
ADMIN_PASS=`pwgen 12 -n 1`
sudo vpn-user-portal-add-user me ${USER_PASS}
sudo vpn-admin-portal-add-user admin ${ADMIN_PASS}

echo "########################################################################"
echo "#"
echo "# Admin Portal"
echo "#     https://${HOSTNAME}/admin"
echo "#         User: admin"
echo "#         Pass: ${ADMIN_PASS}"
echo "# User Portal"
echo "#     https://${HOSTNAME}/portal"
echo "#         User: me"
echo "#         Pass: ${USER_PASS}"
echo "#"
echo "########################################################################"
# ALL DONE!
