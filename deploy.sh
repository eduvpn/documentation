#!/bin/sh

# Script to deploy eduVPN on a CentOS >= 7 installation.
#
# Tested on CentOS 7.2

# TODO: 
# - there is a default user:pass for the user interface and admin interface,
#   foo:bar, which should be updated and printed at the end of the script so
#   they are unique for every instance!

###############################################################################
# VARIABLES
###############################################################################

# VARIABLES
HOSTNAME=vpn.example
EXTERNAL_IF=eth0
KEY_SIZE=4096

# only change if you know what you are doing!
API_USER=api
API_SECRET=`openssl rand -hex 16`

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
sudo curl -L -o /etc/yum.repos.d/fkooman-php-base-epel-7.repo https://copr.fedorainfracloud.org/coprs/fkooman/php-base/repo/epel-7/fkooman-php-base-epel-7.repo
sudo curl -L -o /etc/yum.repos.d/fkooman-vpn-management-epel-7.repo https://copr.fedorainfracloud.org/coprs/fkooman/vpn-management/repo/epel-7/fkooman-vpn-management-epel-7.repo

# install software
sudo yum -y install openvpn easy-rsa mod_ssl php-opcache httpd openssl \
    policycoreutils-python vpn-server-api vpn-config-api vpn-admin-portal \
    vpn-user-portal iptables iptables-services patch sniproxy \
    iptables-services php-fpm php-cli

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
echo "# emptied by deploy.sh" | sudo tee /etc/httpd/conf.d/vpn-config-api.conf >/dev/null
echo "# emptied by deploy.sh" | sudo tee /etc/httpd/conf.d/vpn-user-portal.conf >/dev/null
echo "# emptied by deploy.sh" | sudo tee /etc/httpd/conf.d/vpn-admin-portal.conf >/dev/null

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

sudo sed -i "s/key_size: '4096'/key_size: '${KEY_SIZE}'/" /etc/vpn-config-api/config.yaml
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

# enable the client-connect and client-disconnect scripts
sudo sed -i "s|#client-connect /usr/bin/vpn-server-api-client-connect|client-connect /usr/bin/vpn-server-api-client-connect|" /etc/openvpn/server.conf
sudo sed -i "s|#client-disconnect /usr/bin/vpn-server-api-client-disconnect|client-disconnect /usr/bin/vpn-server-api-client-disconnect|" /etc/openvpn/server.conf

# also create a TCP config
sudo cp /etc/openvpn/server.conf /etc/openvpn/server-tcp.conf

sudo sed -i "s/^dev tun-udp/dev tun-tcp/" /etc/openvpn/server-tcp.conf
sudo sed -i "s/^proto udp6/#proto udp6/" /etc/openvpn/server-tcp.conf
sudo sed -i "s/^port 1194/#port 1194/" /etc/openvpn/server-tcp.conf
sudo sed -i "s/^#proto tcp-server/proto tcp-server/" /etc/openvpn/server-tcp.conf
sudo sed -i "s/^#port 1194/port 1194/" /etc/openvpn/server-tcp.conf
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

# we take the CRL from vpn-config-api and install it in vpn-server-api so 
# OpenVPN will start
sudo -u apache cp /var/lib/vpn-config-api/easy-rsa/pki/crl.pem /var/lib/vpn-server-api/ca.crl
sudo chmod 0644 /var/lib/vpn-server-api/ca.crl

# create a data directory for the connection log database and pool, initialize 
# the database and restore the SELinux context
sudo mkdir -p /var/lib/openvpn/pool
sudo chown -R openvpn.openvpn /var/lib/openvpn
sudo -u openvpn /usr/bin/vpn-server-api-init
sudo restorecon -R /var/lib/openvpn

# allow Apache to read the openvpn_var_lib_t sqlite file
checkmodule -M -m -o resources/httpd-allow-openvpn-var-lib-t-read.mod resources/httpd-allow-openvpn-var-lib-t-read.te
semodule_package -o resources/httpd-allow-openvpn-var-lib-t-read.pp -m resources/httpd-allow-openvpn-var-lib-t-read.mod 
sudo semodule -i resources/httpd-allow-openvpn-var-lib-t-read.pp

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

# create static directory
sudo -u apache mkdir -p /var/lib/vpn-server-api/static

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
sudo php resources/update_api_secret.php ${API_USER} ${API_SECRET}

###############################################################################
# DAEMONS
###############################################################################

sudo systemctl enable httpd
sudo systemctl enable openvpn@server
sudo systemctl enable openvpn@server-tcp
sudo systemctl enable sniproxy
sudo systemctl enable iptables
sudo systemctl enable ip6tables
sudo systemctl enable php-fpm

# flush existing firewall rules if they exist and activate the new ones
sudo systemctl restart iptables
sudo systemctl restart ip6tables

# start services
sudo systemctl start php-fpm
sudo systemctl start httpd
sudo systemctl start openvpn@server
sudo systemctl start openvpn@server-tcp
sudo systemctl start sniproxy

###############################################################################
# POST INSTALL
###############################################################################

# Copy index page
sudo mkdir -p /var/www/${HOSTNAME}
sudo cp resources/index.html /var/www/${HOSTNAME}/index.html
sudo sed -i "s/vpn.example/${HOSTNAME}/" /var/www/${HOSTNAME}/index.html

# ALL DONE!
