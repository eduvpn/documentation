#!/bin/sh

#
# Deploy Controller
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
${PACKAGE_MANAGER} -y install openssl NetworkManager mod_ssl php-opcache httpd openssl \
    php-fpm policycoreutils-python php-cli pwgen \
    iptables iptables-services open-vm-tools tinc bridge-utils

# install software (VPN packages)
${PACKAGE_MANAGER} -y install vpn-server-api vpn-admin-portal vpn-user-portal

###############################################################################
# SELINUX
###############################################################################

# allow Apache to connect to PHP-FPM
setsebool -P httpd_can_network_connect=1

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
cp resources/controller/ssl.conf /etc/httpd/conf.d/ssl.conf

# VirtualHost
cp resources/controller/vpn.example.conf /etc/httpd/conf.d/${INSTANCE}.conf
sed -i "s/vpn.example/${INSTANCE}/" /etc/httpd/conf.d/${INSTANCE}.conf

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
vpn-server-api-update-ip --instance ${INSTANCE} --profile internet --host internet.${INSTANCE} --ext ${EXTERNAL_IF}

# disable portShare, no need to share TCP/443 on dedicated nodes
sed -i "s/portShare: true/portShare: false/" /etc/vpn-server-api/${INSTANCE}/config.yaml
sed -i "s/managementIp: 127.0.0.1/#managementIp: 127.0.0.1/" /etc/vpn-server-api/${INSTANCE}/config.yaml
sed -i "s/processCount: 1/processCount: 4/" /etc/vpn-server-api/${INSTANCE}/config.yaml

# init the CA
sudo -u apache vpn-server-api-init --instance ${INSTANCE}

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
# UPDATE SECRETS
###############################################################################

# update API secret
vpn-server-api-update-api-secrets --instance ${INSTANCE}

###############################################################################
# NETWORK 
###############################################################################

# configure a bridge device as this IP address will be used for running the 
# management services, this can also be shared by running tinc
# if you have any other means to establish connection to the other nodes, e.g. 
# a private network between virtual machines that can also be used, just 
# add the interface to the bridge

cat << EOF > /etc/sysconfig/network-scripts/ifcfg-br0
DEVICE="br0"
ONBOOT="yes"
TYPE="Bridge"
IPADDR0=10.42.101.100
PREFIX0=16
EOF

# activate the interface
ifup br0

###############################################################################
# TINC
###############################################################################

TINC_INSTANCE_NAME=$(echo ${INSTANCE} | sed 's/\./_/g')

rm -rf /etc/tinc
mkdir -p /etc/tinc/vpn

cat << EOF > /etc/tinc/vpn/tinc.conf
Name = ${TINC_INSTANCE_NAME}
Mode = switch
EOF

cp resources/tinc-up /etc/tinc/vpn/tinc-up
cp resources/tinc-down /etc/tinc/vpn/tinc-down
chmod +x /etc/tinc/vpn/tinc-up /etc/tinc/vpn/tinc-down

mkdir -p /etc/tinc/vpn/hosts
cat << EOF > "/etc/tinc/vpn/hosts/${TINC_INSTANCE_NAME}"
Address ${INSTANCE}
EOF

printf "\n\n" | tincd -n vpn -K 4096

cp resources/tinc\@.service /etc/systemd/system

###############################################################################
# DAEMONS
###############################################################################

systemctl enable NetworkManager || true
systemctl enable NetworkManager-wait-online || true
systemctl enable php-fpm
systemctl enable httpd
systemctl enable tinc@vpn
systemctl enable vmtoolsd

# start services
systemctl restart NetworkManager || true
systemctl restart NetworkManager-wait-online || true
systemctl restart php-fpm
systemctl restart httpd
systemctl restart tinc@vpn
systemctl restart vmtoolsd

###############################################################################
# FIREWALL
###############################################################################

cp resources/controller/iptables /etc/sysconfig/iptables
cp resources/controller/ip6tables /etc/sysconfig/ip6tables

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

TINC_CONFIG=$(base64 -w 0 < "/etc/tinc/vpn/hosts/${TINC_INSTANCE_NAME}")
API_SECRET=$(grep vpn-server-node /etc/vpn-server-api/${INSTANCE}/config.yaml | cut -d ":" -f 2 | xargs)

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
echo
echo "########################################################################"
echo "# Variables for the top of the deploy_node.sh script:"
echo "# --- cut ---"
echo "INSTANCE=${INSTANCE}"
echo "EXTERNAL_IF=${EXTERNAL_IF}"
echo "MANAGEMENT_IP=10.42.101.101"
echo "PROFILE=internet"
echo "API_SECRET=${API_SECRET}"
echo "TINC_CONFIG=${TINC_CONFIG}"
echo "# --- /cut ---"
echo "#"
echo "########################################################################"

# ALL DONE!
