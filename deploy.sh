#!/bin/sh

#
# Deploy
#

###############################################################################
# VARIABLES
###############################################################################

# VARIABLES
INSTANCE=vpn.example
EXTERNAL_IF=eth0

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

# remove firewalld if it is installed, too complicated
${PACKAGE_MANAGER} -y remove firewalld

# enable EPEL
${PACKAGE_MANAGER} -y install epel-release

curl -L -o /etc/yum.repos.d/fkooman-eduvpn-testing-epel-7.repo \
    https://copr.fedorainfracloud.org/coprs/fkooman/eduvpn-testing/repo/epel-7/fkooman-eduvpn-testing-epel-7.repo

# install software (dependencies)
${PACKAGE_MANAGER} -y install openssl NetworkManager mod_ssl php-opcache httpd iptables pwgen \
    iptables-services sniproxy open-vm-tools php php-fpm php-cli bridge-utils

# install software (VPN packages)
${PACKAGE_MANAGER} -y install vpn-server-node vpn-server-api vpn-admin-portal vpn-user-portal

###############################################################################
# NETWORK 
###############################################################################

ifdown br0

# configure a bridge device as this IP address will be used for running the 
# management services, this can also be shared by running tinc
# if you have any other means to establish connection to the other nodes, e.g. 
# a private network between virtual machines that can also be used, just 
# add the interface to the bridge

cat << EOF > /etc/sysconfig/network-scripts/ifcfg-br0
DEVICE="br0"
ONBOOT="yes"
TYPE="Bridge"
# for the web services
IPADDR0=10.42.101.100
PREFIX0=16
# for the OpenVPN instances
IPADDR1=10.42.101.101
PREFIX1=16
EOF

# activate the interface
ifup br0

###############################################################################
# SELINUX
###############################################################################

# allow Apache to connect to PHP-FPM
setsebool -P httpd_can_network_connect=1

# allow OpenVPN to listen on its management ports, and some additional VPN
# ports for load balancing
semanage port -a -t openvpn_port_t -p udp 1195-1201     # allow up to 8 instances
semanage port -a -t openvpn_port_t -p tcp 1195-1201     # allow up to 8 instances
semanage port -a -t openvpn_port_t -p tcp 11940-11947   # allow up to 8 instances

###############################################################################
# CERTIFICATE
###############################################################################

# Generate the private key
openssl genrsa -out /etc/pki/tls/private/${INSTANCE}.key 4096
chmod 600 /etc/pki/tls/private/${INSTANCE}.key

# Create the CSR (can be used to obtain real certificate!)
openssl req -subj "/CN=${INSTANCE}" -sha256 -new -key /etc/pki/tls/private/${INSTANCE}.key -out ${INSTANCE}.csr

# Create the (self signed) certificate and install it
openssl req -subj "/CN=${INSTANCE}" -sha256 -new -x509 -key /etc/pki/tls/private/${INSTANCE}.key -out /etc/pki/tls/certs/${INSTANCE}.crt

###############################################################################
# APACHE
###############################################################################

# Don't have Apache advertise all version details
# https://httpd.apache.org/docs/2.4/mod/core.html#ServerTokens
echo "ServerTokens ProductOnly" > /etc/httpd/conf.d/servertokens.conf

# Use a hardended ssl.conf instead of the default, gives A+ on
# https://www.ssllabs.com/ssltest/
cp /etc/httpd/conf.d/ssl.conf /etc/httpd/conf.d/ssl.conf.BACKUP
cp resources/ssl.conf /etc/httpd/conf.d/ssl.conf

# VirtualHost
cp resources/vpn.example.conf /etc/httpd/conf.d/${INSTANCE}.conf
sed -i "s/vpn.example/${INSTANCE}/" /etc/httpd/conf.d/${INSTANCE}.conf

# Make Apache not listen on port 80 anymore, sniproxy will take care of that
sed -i "s/^Listen 80$/#Listen 80/" /etc/httpd/conf/httpd.conf

# empty the RPM httpd configs instead of deleting so we do not get them back
# on package update
echo "# emptied by deploy.sh" > /etc/httpd/conf.d/vpn-server-api.conf
echo "# emptied by deploy.sh" > /etc/httpd/conf.d/vpn-user-portal.conf
echo "# emptied by deploy.sh" > /etc/httpd/conf.d/vpn-admin-portal.conf

###############################################################################
# PHP
###############################################################################

# switch to unix socket, default in newer PHP versions, but not on CentOS 7
sed -i "s|^listen = 127.0.0.1:9000$|listen = /run/php-fpm/www.sock|" /etc/php-fpm.d/www.conf

cp resources/99-eduvpn.ini /etc/php.d/99-eduvpn.ini

###############################################################################
# VPN-SERVER-API
###############################################################################

# delete existing data
rm -rf /etc/vpn-server-api/${INSTANCE}
rm -rf /var/lib/vpn-server-api/${INSTANCE}

mkdir -p /etc/vpn-server-api/${INSTANCE}
cp /etc/vpn-server-api/default/config.yaml /etc/vpn-server-api/${INSTANCE}/config.yaml

# update the IPv4 CIDR and IPv6 prefix to random IP ranges and set the extIf
vpn-server-api-update-ip --instance ${INSTANCE} --profile internet --host ${INSTANCE} --ext ${EXTERNAL_IF}

sed -i "s/managementIp: 127.0.0.1/#managementIp: 127.0.0.1/" /etc/vpn-server-api/${INSTANCE}/config.yaml
sed -i "s/processCount: 1/processCount: 4/" /etc/vpn-server-api/${INSTANCE}/config.yaml

# init the CA
sudo -u apache vpn-server-api-init --instance ${INSTANCE}

###############################################################################
# VPN-SERVER-NODE
###############################################################################

# deleting existing data
rm -rf /etc/vpn-server-node/${INSTANCE}

mkdir -p /etc/vpn-server-node/${INSTANCE}
cp /etc/vpn-server-node/default/config.yaml /etc/vpn-server-node/${INSTANCE}/config.yaml

# add instance for firewall generation instead of default
sed -i "s|- default|- ${INSTANCE}|" /etc/vpn-server-node/firewall.yaml

# point to our Server API
sed -i "s|localhost/vpn-server-api|10.42.101.100:8008|" /etc/vpn-server-node/${INSTANCE}/config.yaml

###############################################################################
# VPN-ADMIN-PORTAL
###############################################################################

# deleting existing data
rm -rf /etc/vpn-admin-portal/${INSTANCE}
rm -rf /var/lib/vpn-admin-portal/${INSTANCE}

mkdir -p /etc/vpn-admin-portal/${INSTANCE}
cp /etc/vpn-admin-portal/default/config.yaml /etc/vpn-admin-portal/${INSTANCE}/config.yaml

# enable secure cookies
sed -i "s|secureCookie: false|secureCookie: true|" /etc/vpn-admin-portal/${INSTANCE}/config.yaml 

# point to our Server API
sed -i "s|localhost/vpn-server-api|10.42.101.100:8008|" /etc/vpn-admin-portal/${INSTANCE}/config.yaml

###############################################################################
# VPN-USER-PORTAL
###############################################################################

# deleting existing data
rm -rf /etc/vpn-user-portal/${INSTANCE}
rm -rf /var/lib/vpn-user-portal/${INSTANCE}

mkdir -p /etc/vpn-user-portal/${INSTANCE}
cp /etc/vpn-user-portal/default/config.yaml /etc/vpn-user-portal/${INSTANCE}/config.yaml

# enable secure cookies
sed -i "s|secureCookie: false|secureCookie: true|" /etc/vpn-user-portal/${INSTANCE}/config.yaml 

# point to our Server API
sed -i "s|localhost/vpn-server-api|10.42.101.100:8008|" /etc/vpn-user-portal/${INSTANCE}/config.yaml

###############################################################################
# NETWORK
###############################################################################

cat << EOF > /etc/sysctl.d/42-eduvpn.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
# disable below for static IPv6 configurations
net.ipv6.conf.${EXTERNAL_IF}.accept_ra = 2
EOF

sysctl --system

###############################################################################
# SNIPROXY
###############################################################################

# install the config file
cp resources/sniproxy.conf /etc/sniproxy.conf
sed -i "s/vpn.example/${INSTANCE}/" /etc/sniproxy.conf

###############################################################################
# UPDATE SECRETS
###############################################################################

# update API secret
vpn-server-api-update-api-secrets --instance ${INSTANCE}

###############################################################################
# DAEMONS
###############################################################################

systemctl enable php-fpm
systemctl enable httpd
systemctl enable sniproxy
systemctl enable NetworkManager || true
# https://www.freedesktop.org/wiki/Software/systemd/NetworkTarget/
# we need this for sniproxy and openvpn to start only when the network is up
# because we bind to other addresses than 0.0.0.0 and ::
systemctl enable NetworkManager-wait-online || true
systemctl enable vmtoolsd

# start services
systemctl restart NetworkManager || true
systemctl restart NetworkManager-wait-online || true
systemctl restart php-fpm
systemctl restart httpd
systemctl restart sniproxy
systemctl restart vmtoolsd

###############################################################################
# OPENVPN SERVER CONFIG
###############################################################################

# remove existing configurations
rm -rf /etc/openvpn/*

# generate the server configuration files
vpn-server-node-server-config --instance ${INSTANCE} --profile internet --generate

# symlink to work with new systemd unit file
ln -s /etc/openvpn /etc/openvpn/server

# enable and start OpenVPN
systemctl enable openvpn@${INSTANCE}-internet-0
systemctl enable openvpn@${INSTANCE}-internet-1
systemctl enable openvpn@${INSTANCE}-internet-2
systemctl enable openvpn@${INSTANCE}-internet-3

systemctl start openvpn@${INSTANCE}-internet-0
systemctl start openvpn@${INSTANCE}-internet-1
systemctl start openvpn@${INSTANCE}-internet-2
systemctl start openvpn@${INSTANCE}-internet-3

###############################################################################
# FIREWALL
###############################################################################

# generate and install the firewall
vpn-server-node-generate-firewall --install

systemctl enable iptables
systemctl enable ip6tables

# flush existing firewall rules if they exist and activate the new ones
systemctl restart iptables
systemctl restart ip6tables

###############################################################################
# SSHD
###############################################################################

cp resources/sshd_config /etc/ssh/sshd_config
chmod 0600 /etc/ssh/sshd_config
systemctl restart sshd

###############################################################################
# POST INSTALL
###############################################################################

sed -i "s/--instance default/--instance ${INSTANCE}/" /etc/cron.d/vpn-server-api

###############################################################################
# WEB
###############################################################################

mkdir -p /var/www/${INSTANCE}
cp resources/index.html /var/www/${INSTANCE}/index.html
sed -i "s/vpn.example/${INSTANCE}/" /var/www/${INSTANCE}/index.html
# Copy server info JSON file
cp resources/info.json /var/www/${INSTANCE}/info.json
sed -i "s/vpn.example/${INSTANCE}/" /var/www/${INSTANCE}/info.json

###############################################################################
# USERS
###############################################################################

USER_PASS=$(pwgen 12 -n 1)
ADMIN_PASS=$(pwgen 12 -n 1)
vpn-user-portal-add-user  --instance ${INSTANCE} --user me    --pass "${USER_PASS}"
vpn-admin-portal-add-user --instance ${INSTANCE} --user admin --pass "${ADMIN_PASS}"

echo "########################################################################"
echo "# Admin Portal"
echo "#     https://${INSTANCE}/admin"
echo "#         User: admin"
echo "#         Pass: ${ADMIN_PASS}"
echo "# User Portal"
echo "#     https://${INSTANCE}/portal"
echo "#         User: me"
echo "#         Pass: ${USER_PASS}"
echo "########################################################################"
# ALL DONE!
