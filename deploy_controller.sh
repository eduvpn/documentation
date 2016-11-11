#!/bin/sh

#
# Deploy Controller
#

###############################################################################
# VARIABLES
###############################################################################

# VARIABLES
INSTANCE=vpn.example

###############################################################################
# SYSTEM
###############################################################################

# https://lobste.rs/c/4lfcnm (danielrheath)
set -e # stop the script on errors
set -u # unset variables are an error
set -o pipefail # piping a failed process into a successful one is an arror

# update packages to make sure we have latest version of everything
yum -y clean expire-cache && yum -y update

###############################################################################
# SOFTWARE
###############################################################################

# remove firewalld, too complicated
yum -y remove firewalld

# enable EPEL
yum -y install epel-release

# enable COPR repos
curl -L -o /etc/yum.repos.d/fkooman-eduvpn-dev-epel-7.repo https://copr.fedorainfracloud.org/coprs/fkooman/eduvpn-dev/repo/epel-7/fkooman-eduvpn-dev-epel-7.repo

# install software (dependencies)
yum -y install NetworkManager mod_ssl php-opcache httpd telnet openssl \
    php-fpm policycoreutils-python patch php-cli psmisc net-tools php pwgen \
    iptables iptables-services open-vm-tools tinc bridge-utils

# install software (VPN packages)
yum -y install vpn-server-api vpn-ca-api vpn-admin-portal vpn-user-portal

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
vpn-server-api-update-ip --instance ${INSTANCE} --profile internet --host internet.${INSTANCE} --ext ethXXX

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
# UPDATE SECRETS
###############################################################################

# update API secret
php resources/update_api_secret.php ${INSTANCE}

###############################################################################
# NETWORK 
###############################################################################

# configure a bridge device as this IP address will be used for running the 
# management services, this is also shared by running tinc

# if you have any other means to establish connection to the other nodes, e.g. 
# a private network between virtual machines that can also be used, just 
# configure this IP on that device

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

mkdir -p /etc/tinc/vpn
yes | tincd -n vpn -K 4096

cat << EOF > /etc/tinc/vpn/tinc.conf
Name = $(echo ${INSTANCE} | sed 's/\./_/g')
Mode = switch
EOF

cat << EOF > /etc/tinc/vpn/tinc-up
#!/bin/sh
/sbin/ifconfig ${INTERFACE} 0.0.0.0
/sbin/brctl addif br0 ${INTERFACE}
EOF

cat << EOF > /etc/tinc/vpn/tinc-down
#!/bin/sh
/sbin/brctl delif br0 ${INTERFACE}
/sbin/ifconfig \${INTERFACE} down
EOF

chmod +x /etc/tinc/vpn/tinc-up /etc/tinc/vpn/tinc-down

PUBLIC_KEY=$(cat /etc/tinc/vpn/rsa_key.pub)

mkdir -p /etc/tinc/vpn/hosts
cat << EOF > /etc/tinc/vpn/hosts/$(echo ${INSTANCE} | sed 's/\./_/g')
Address ${INSTANCE}
${PUBLIC_KEY}
EOF

###############################################################################
# DAEMONS
###############################################################################

systemctl enable php-fpm
systemctl enable httpd
systemctl enable tinc@vpn
systemctl enable vmtoolsd

# start services
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

echo "@hourly root /usr/sbin/vpn-server-api-housekeeping --instance ${INSTANCE}" > /etc/cron.d/vpn-server-api-housekeeping
echo "@daily apache /usr/sbin/vpn-server-api-stats --instance ${INSTANCE}" > /etc/cron.d/vpn-server-api-stats

# run the statistics script for the first time to not generate errors in the
# admin
sudo -u apache vpn-server-api-stats --instance ${INSTANCE}

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
