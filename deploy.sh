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

# https://lobste.rs/c/4lfcnm (danielrheath)
set -e # stop the script on errors
set -u # unset variables are an error
set -o pipefail # piping a failed process into a successful one is an arror

###############################################################################
# NETWORK 
###############################################################################

# configure the TAP device as this IP address will be used for running the 
# management services, this is also shared by running PeerVPN

# if you have any other means to establish connection to the other nodes, e.g. 
# a private network between virtual machines that can also be used, just 
# configure this IP on that device

cat << EOF > /etc/sysconfig/network-scripts/ifcfg-tap0
DEVICE="tap0"
ONBOOT="yes"
TYPE="Tap"
# for the web services
IPADDR0=10.42.101.100
PREFIX0=16
# for the OpenVPN instances
IPADDR1=10.42.101.101
PREFIX1=16
EOF

# activate the interface
ifup tap0

###############################################################################
# SOFTWARE
###############################################################################

# remove firewalld, too complicated to get to work reliably for now
yum -y remove firewalld

# enable EPEL
yum -y install epel-release

# enable COPR repos
curl -L -o /etc/yum.repos.d/fkooman-eduvpn-dev-epel-7.repo https://copr.fedorainfracloud.org/coprs/fkooman/eduvpn-dev/repo/epel-7/fkooman-eduvpn-dev-epel-7.repo

# install software (dependencies)
yum -y install NetworkManager openvpn mod_ssl php-opcache httpd telnet \
    openssl policycoreutils-python iptables iptables-services patch sniproxy \
    open-vm-tools iptables-services php-fpm php-cli psmisc net-tools php pwgen

# install software (VPN packages)
yum -y install vpn-server-node vpn-server-api vpn-ca-api vpn-admin-portal vpn-user-portal

# update packages to make sure we have latest version of everything
yum -y update

###############################################################################
# SELINUX
###############################################################################

# allow Apache to connect to PHP-FPM
setsebool -P httpd_can_network_connect=1

# allow OpenVPN to listen on its management ports, and some additional VPN
# ports for load balancing
semanage port -a -t openvpn_port_t -p udp 1195-1201 || true   # allow up to 8 instances
semanage port -a -t openvpn_port_t -p tcp 1195-1201 || true   # allow up to 8 instances
semanage port -a -t openvpn_port_t -p tcp 11940-11947 || true # allow up to 8 instances

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
echo "# emptied by deploy.sh" > /etc/httpd/conf.d/vpn-ca-api.conf
echo "# emptied by deploy.sh" > /etc/httpd/conf.d/vpn-user-portal.conf
echo "# emptied by deploy.sh" > /etc/httpd/conf.d/vpn-admin-portal.conf

###############################################################################
# PHP
###############################################################################

cp resources/99-eduvpn.ini /etc/php.d/99-eduvpn.ini

###############################################################################
# VPN-CA-API
###############################################################################

# delete existing data
rm -rf /etc/vpn-ca-api/*
rm -rf /var/lib/vpn-ca-api/*

mkdir -p /etc/vpn-ca-api/${INSTANCE}
cp /usr/share/doc/vpn-ca-api-*/config.yaml.example /etc/vpn-ca-api/${INSTANCE}/config.yaml

sudo -u apache vpn-ca-api-init --instance ${INSTANCE}

###############################################################################
# VPN-SERVER-API
###############################################################################

# delete existing data
rm -rf /etc/vpn-server-api/*
rm -rf /var/lib/vpn-server-api/*

mkdir -p /etc/vpn-server-api/${INSTANCE}
cp /usr/share/doc/vpn-server-api-*/config.yaml.example /etc/vpn-server-api/${INSTANCE}/config.yaml

# OTP log for two-factor auth
sudo -u apache vpn-server-api-init --instance ${INSTANCE}

# update the IPv4 CIDR and IPv6 prefix to random IP ranges and set the extIf
vpn-server-api-update-ip --instance ${INSTANCE} --profile internet --host ${INSTANCE} --ext ${EXTERNAL_IF}

###############################################################################
# VPN-SERVER-NODE
###############################################################################

# deleting existing data
rm -rf /etc/vpn-server-node/*

mkdir -p /etc/vpn-server-node/${INSTANCE}

cp /usr/share/doc/vpn-server-node-*/dh.pem /etc/vpn-server-node/dh.pem
cp /usr/share/doc/vpn-server-node-*/firewall.yaml.example /etc/vpn-server-node/firewall.yaml
cp /usr/share/doc/vpn-server-node-*/config.yaml.example /etc/vpn-server-node/${INSTANCE}/config.yaml

###############################################################################
# VPN-ADMIN-PORTAL
###############################################################################

# deleting existing data
rm -rf /etc/vpn-admin-portal/*
rm -rf /var/lib/vpn-admin-portal/*

mkdir -p /etc/vpn-admin-portal/${INSTANCE}
cp /usr/share/doc/vpn-admin-portal-*/config.yaml.example /etc/vpn-admin-portal/${INSTANCE}/config.yaml

###############################################################################
# VPN-USER-PORTAL
###############################################################################

# deleting existing data
rm -rf /etc/vpn-user-portal/*
rm -rf /var/lib/vpn-user-portal/*

mkdir -p /etc/vpn-user-portal/${INSTANCE}
cp /usr/share/doc/vpn-user-portal-*/config.yaml.example /etc/vpn-user-portal/${INSTANCE}/config.yaml

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
php resources/update_api_secret.php ${INSTANCE}

###############################################################################
# DAEMONS
###############################################################################

systemctl enable php-fpm
systemctl enable httpd
systemctl enable sniproxy
systemctl enable NetworkManager
# https://www.freedesktop.org/wiki/Software/systemd/NetworkTarget/
# we need this for sniproxy and openvpn to start only when the network is up
# because we bind to other addresses than 0.0.0.0 and ::
systemctl enable NetworkManager-wait-online
systemctl enable vmtoolsd

# start services
systemctl restart NetworkManager
systemctl restart NetworkManager-wait-online
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
vpn-server-node-server-config --instance ${INSTANCE} --profile internet --generate --cn ${INSTANCE}

# enable and start OpenVPN
systemctl enable openvpn@server-${INSTANCE}-internet-0
systemctl enable openvpn@server-${INSTANCE}-internet-1
systemctl enable openvpn@server-${INSTANCE}-internet-2
systemctl enable openvpn@server-${INSTANCE}-internet-3

systemctl start openvpn@server-${INSTANCE}-internet-0
systemctl start openvpn@server-${INSTANCE}-internet-1
systemctl start openvpn@server-${INSTANCE}-internet-2
systemctl start openvpn@server-${INSTANCE}-internet-3

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

# install a crontab to cleanup the old OTP entries stored to protect against
# 2FA code reuse
echo "@hourly root /usr/sbin/vpn-server-api-housekeeping --instance ${INSTANCE}" > /etc/cron.d/vpn-server-api-housekeeping

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
