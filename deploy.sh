#!/bin/sh

# Script to deploy eduVPN on a CentOS >= 7 installation.
#
# Tested on CentOS 7.2

# TODO: 
# - for all APIs the user:pass is admin:s3cr3t, this is not a problem because
#   the endpoints are not reachable from the outside anyway, but it is not
#   really good practise, update them!
# - there is a default user:pass for the user interface and admin interface,
#   foo:bar, which should be updated and printed at the end of the script so
#   they are unique for every instance!
# - look into deploying using php-fpm instead of mod_php to increase 
#   performance of the web interfaces

###############################################################################
# VARIABLES
###############################################################################

# VARIABLES
HOSTNAME=vpn.example
EXTERNAL_IF=eth0

###############################################################################
# SYSTEM
###############################################################################

sudo yum -y update

###############################################################################
# SOFTWARE
###############################################################################

# enable EPEL
sudo yum -y install epel-release

# enable COPR repos
sudo curl -o /etc/yum.repos.d/fkooman-php-base-epel-7.repo https://copr.fedoraproject.org/coprs/fkooman/php-base/repo/epel-7/fkooman-php-base-epel-7.repo
sudo curl -o /etc/yum.repos.d/fkooman-vpn-management-epel-7.repo https://copr.fedoraproject.org/coprs/fkooman/vpn-management/repo/epel-7/fkooman-vpn-management-epel-7.repo

# install software
sudo yum -y install openvpn easy-rsa mod_ssl php php-opcache httpd openssl \
    policycoreutils-python vpn-server-api vpn-config-api vpn-admin-portal \
    vpn-user-portal iptables iptables-services patch

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

# We took the default `/etc/httpd/conf.d/ssl.conf` file, hardened it and 
# pointed it to the generated certificates, gives A+ on 
# https://www.ssllabs.com/ssltest/
#
# See also https://wiki.mozilla.org/Security/Server_Side_TLS
sudo cp resources/hardened_ssl.conf.diff /etc/httpd/conf.d
(
  cd /etc/httpd/conf.d
  sudo patch -p0 < hardened_ssl.conf.diff
)

# update hostname in ssl.conf
sudo sed -i "s/vpn.example/${HOSTNAME}/" /etc/httpd/conf.d/ssl.conf

# change SSL and VirtualHost port to 8443
sudo sed -i "s/Listen 443/Listen 8443/" /etc/httpd/conf.d/ssl.conf
sudo sed -i "s/<VirtualHost _default_:443>/<VirtualHost _default_:8443>/" /etc/httpd/conf.d/ssl.conf
sudo sed -i "s/#ServerName www.example.com:443/ServerName ${HOSTNAME}:443/" /etc/httpd/conf.d/ssl.conf

###############################################################################
# PHP
###############################################################################

# Set PHP timezone, to suppress errors in the log
sudo sed -i 's/;date.timezone =/date.timezone = UTC/' /etc/php.ini

#https://secure.php.net/manual/en/ini.core.php#ini.expose-php
sudo sed -i 's/expose_php = On/expose_php = Off/' /etc/php.ini

# recommendation from https://php.net/manual/en/opcache.installation.php
sudo sed -i 's/;opcache.revalidate_freq=2/opcache.revalidate_freq=60/' /etc/php.d/opcache.ini

###############################################################################
# VPN-CONFIG-API
###############################################################################

# we are happy with 2048 bit key as 4096 DH param takes really too long
sudo sed -i "s/key_size: '4096'/key_size: '2048'" /etc/vpn-config-api/config.yaml
# initialize the CA
sudo -u apache vpn-config-api-init

# copy the default config templates
sudo mkdir /etc/vpn-config-api/views
sudo cp /usr/share/vpn-config-api/views/*.twig /etc/vpn-config-api/views

# update hostname in client.twig
sudo sed -i "s/remote vpn.example 1194 udp/remote ${HOSTNAME} 1194 udp/" /etc/vpn-config-api/views/client.twig
sudo sed -i "s/remote vpn.example 443 tcp/remote ${HOSTNAME} 443 tcp/" /etc/vpn-config-api/views/client.twig

# generate a server configuration file
echo "**** GENERATING SERVER CONFIG, THIS WILL TAKE A LONG TIME... ****"
sudo -u apache vpn-config-api-server-config ${HOSTNAME} | sudo tee /etc/openvpn/server.conf >/dev/null
sudo chmod 0600 /etc/openvpn/server.conf

# enable CCD
sudo sed -i 's|#client-config-dir /var/lib/vpn-server-api/ccd|client-config-dir /var/lib/vpn-server-api/ccd|' /etc/openvpn/server.conf

# also create a TCP config, port share it with the web server on tcp/443
sudo cp /etc/openvpn/server.conf /etc/openvpn/server-tcp.conf

sudo sed -i "s/^proto udp/#proto udp/" /etc/openvpn/server-tcp.conf
sudo sed -i "s/^port 1194/#port 1194/" /etc/openvpn/server-tcp.conf
sudo sed -i "s/^#proto tcp-server/proto tcp-server/" /etc/openvpn/server-tcp.conf
sudo sed -i "s/^#port 443/port 443/" /etc/openvpn/server-tcp.conf
sudo sed -i "s/^#port-share localhost 8443/port-share localhost 8443/" /etc/openvpn/server-tcp.conf

sudo sed -i "s|server 10.42.42.0 255.255.255.0|server 10.43.43.0 255.255.255.0|" /etc/openvpn/server-tcp.conf
sudo sed -i "s|server-ipv6 fd00:4242:4242::/64|server-ipv6 fd00:4343:4343::/64|" /etc/openvpn/server-tcp.conf
sudo sed -i "s|management localhost 7505|management localhost 7506|" /etc/openvpn/server-tcp.conf

# allow vpn-config-api to run Easy-RSA scripts
sudo setsebool -P httpd_unified 1

###############################################################################
# VPN-SERVER-API
###############################################################################

# we also want to connect to the second OpenVPN instance
sudo sed -i 's|#- id: TCP|- id: TCP|' /etc/vpn-server-api/config.yaml
sudo sed -i "s|#  socket: 'tcp://localhost:7506'|  socket: 'tcp://localhost:7506'|" /etc/vpn-server-api/config.yaml

# allow vpn-server-api to connect to OpenVPN management interface
sudo setsebool -P httpd_can_network_connect=on

###############################################################################
# VPN-ADMIN-PORTAL
###############################################################################

# allow connections from everywhere
sudo sed -i "s/#Require all granted/Require all granted/" /etc/httpd/conf.d/vpn-admin-portal.conf

###############################################################################
# VPN-USER-PORTAL
###############################################################################

sudo -u apache vpn-user-portal-init

# allow connections from everywhere
sudo sed -i "s/#Require all granted/Require all granted/" /etc/httpd/conf.d/vpn-user-portal.conf

###############################################################################
# OPENVPN
###############################################################################

# allow OpenVPN to listen on its management ports
sudo semanage port -a -t openvpn_port_t -p tcp 7505-7506

# allow OpenVPN to listen on tcp/443
sudo semanage port -m -t openvpn_port_t -p tcp 443

# allow OpenVPN to read the CRL from vpn-server-api
checkmodule -M -m -o resources/openvpn-allow-server-api-read.mod resources/openvpn-allow-server-api-read.te 
semodule_package -o resources/openvpn-allow-server-api-read.pp -m resources/openvpn-allow-server-api-read.mod 
sudo semodule -i resources/openvpn-allow-server-api-read.pp

# Firewall
sudo cp resources/iptables /etc/sysconfig/iptables
sudo cp resources/ip6tables /etc/sysconfig/ip6tables
# update firewall outgoing interface
sudo sed -i "s/eth0/${EXTERNAL_IF}/" /etc/sysconfig/iptables
sudo sed -i "s/eth0/${EXTERNAL_IF}/" /etc/sysconfig/ip6tables

# enable forwarding
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf >/dev/null
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.conf >/dev/null

# forwarding disables accepting RAs on our external interface, so we have to 
# explicitly enable it here to make IPv6 work
echo "net.ipv6.conf.${EXTERNAL_IF}.accept_ra = 2" | sudo tee -a /etc/sysctl.conf >/dev/null
sudo sysctl -p

# create CCD directory
sudo -u apache mkdir -p /var/lib/vpn-server-api/ccd

###############################################################################
# DAEMONS
###############################################################################

sudo systemctl enable httpd
sudo systemctl enable openvpn@server
sudo systemctl enable openvpn@server-tcp
sudo systemctl enable iptables
sudo systemctl enable ip6tables

sudo systemctl start httpd
sudo systemctl start openvpn@server
sudo systemctl start openvpn@server-tcp
# flush existing firewall rules if they exist and activate the new ones
sudo systemctl restart iptables
sudo systemctl restart ip6tables

###############################################################################
# POST INSTALL
###############################################################################

# XXX: move this to the init script of vpn-config-api, there should be a CRL
# by default
# we need to create a CRL before we can start OpenVPN with CRL checking enabled
curl -u admin:s3cr3t -d 'commonName=revoke@example.org' http://localhost/vpn-config-api/api.php/config/ >/dev/null
curl -u admin:s3cr3t -X DELETE http://localhost/vpn-config-api/api.php/config/revoke@example.org
# reload the CRL
curl -u admin:s3cr3t -X POST http://localhost/vpn-server-api/api.php/refreshCrl

# enable CRL
sudo sed -i "s|#crl-verify /etc/openvpn/ca.crl|crl-verify /var/lib/vpn-server-api/ca.crl|" /etc/openvpn/server.conf
sudo sed -i "s|#crl-verify /etc/openvpn/ca.crl|crl-verify /var/lib/vpn-server-api/ca.crl|" /etc/openvpn/server-tcp.conf

# restart OpenVPN
sudo systemctl restart openvpn@server
sudo systemctl restart openvpn@server-tcp

# Copy index page
sudo cp resources/index.html /var/www/html/index.html
sudo sed -i "s/vpn.example/${HOSTNAME}/" /var/www/html/index.html

# ALL DONE!
