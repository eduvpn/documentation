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
# TODO:
# - make this script work on Fedora out of the box, not just CentOS

###############################################################################
# VARIABLES
###############################################################################

# VARIABLES
HOSTNAME=vpn.example
EXTERNAL_IF=eth0

###############################################################################
# SYSTEM
###############################################################################

# https://lobste.rs/c/4lfcnm (danielrheath)
set -e # stop the script on errors
set -u # unset variables are an error
set -o pipefail # piping a failed process into a successful one is an arror

###############################################################################
# LOGGING
###############################################################################

# CentOS forwards to syslog, but we want to use journald, enable persistent
# storage, but only for 31 days
sed -i 's/^#Storage=auto/Storage=persistent/' /etc/systemd/journald.conf
sed -i 's/^#MaxRetentionSec=/MaxRetentionSec=2678400/' /etc/systemd/journald.conf
systemctl restart systemd-journald

###############################################################################
# SOFTWARE
###############################################################################

# remove NetworkManager and firewalld
yum -y remove NetworkManager firewalld

# enable EPEL
yum -y install epel-release

# enable COPR repos
curl -L -o /etc/yum.repos.d/fkooman-eduvpn-dev-epel-7.repo https://copr.fedorainfracloud.org/coprs/fkooman/eduvpn-dev/repo/epel-7/fkooman-eduvpn-dev-epel-7.repo

# install software (dependencies)
yum -y install openvpn easy-rsa mod_ssl php-opcache httpd openssl \
    policycoreutils-python iptables iptables-services patch sniproxy \
    iptables-services php-fpm php-cli psmisc net-tools php pwgen \
    php-pecl-libsodium

# install software (VPN packages)
yum -y install vpn-server-api vpn-ca-api vpn-admin-portal vpn-user-portal

###############################################################################
# SELINUX
###############################################################################

# allow Apache to connect to PHP-FPM
setsebool -P httpd_can_network_connect=1

# allow OpenVPN to listen on its management ports, and some additional VPN
# ports for load balancing
semanage port -a -t openvpn_port_t -p udp 1195-1201    # allow up to 8 instances
semanage port -a -t openvpn_port_t -p tcp 11940-11947  # allow up to 8 instances

# install a custom module to allow reading/writing to OpenVPN/httpd paths
checkmodule -M -m -o resources/vpn-management.mod resources/vpn-management.te
semodule_package -o resources/vpn-management.pp -m resources/vpn-management.mod
semodule -i resources/vpn-management.pp

###############################################################################
# CERTIFICATE
###############################################################################

# Generate the private key
openssl genrsa -out /etc/pki/tls/private/${HOSTNAME}.key 4096
chmod 600 /etc/pki/tls/private/${HOSTNAME}.key

# Create the CSR (can be used to obtain real certificate!)
openssl req -subj "/CN=${HOSTNAME}" -sha256 -new -key /etc/pki/tls/private/${HOSTNAME}.key -out ${HOSTNAME}.csr

# Create the (self signed) certificate and install it
openssl req -subj "/CN=${HOSTNAME}" -sha256 -new -x509 -key /etc/pki/tls/private/${HOSTNAME}.key -out /etc/pki/tls/certs/${HOSTNAME}.crt

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
cp resources/vpn.example.conf /etc/httpd/conf.d/${HOSTNAME}.conf
sed -i "s/vpn.example/${HOSTNAME}/" /etc/httpd/conf.d/${HOSTNAME}.conf

# empty the RPM httpd configs instead of deleting so we do not get them back
# on package update
echo "# emptied by deploy.sh" > /etc/httpd/conf.d/vpn-server-api.conf
echo "# emptied by deploy.sh" > /etc/httpd/conf.d/vpn-ca-api.conf
echo "# emptied by deploy.sh" > /etc/httpd/conf.d/vpn-user-portal.conf
echo "# emptied by deploy.sh" > /etc/httpd/conf.d/vpn-admin-portal.conf

###############################################################################
# PHP
###############################################################################

# Set PHP timezone, to suppress errors in the log
sed -i 's/;date.timezone =/date.timezone = UTC/' /etc/php.ini

#https://secure.php.net/manual/en/ini.core.php#ini.expose-php
sed -i 's/expose_php = On/expose_php = Off/' /etc/php.ini

# more secure PHP sessions
# https://paragonie.com/blog/2015/04/fast-track-safe-and-secure-php-sessions
sed -i 's/session.hash_function = 0/session.hash_function = sha256/' /etc/php.ini
sed -i 's/;session.entropy_length = 32/session.entropy_length = 32/' /etc/php.ini

# recommendation from https://php.net/manual/en/opcache.installation.php
sed -i 's/;opcache.revalidate_freq=2/opcache.revalidate_freq=60/' /etc/php.d/opcache.ini

# mbstring
sed -i 's/;mbstring.internal_encoding = EUC-JP/mbstring.internal_encoding = UTF-8/' /etc/php.ini
sed -i 's/;mbstring.http_input = auto/mbstring.http_input = UTF-8/' /etc/php.ini
sed -i 's/;mbstring.http_output = SJIS/mbstring.http_output = UTF-8/' /etc/php.ini

###############################################################################
# vpn-ca-api
###############################################################################

# initialize the CA
mkdir /etc/vpn-ca-api/${HOSTNAME}
cp /usr/share/doc/vpn-ca-api-*/config.yaml.example /etc/vpn-ca-api/${HOSTNAME}/config.yaml
chown root.apache /etc/vpn-ca-api/${HOSTNAME}/config.yaml
chmod 0640 /etc/vpn-ca-api/${HOSTNAME}/config.yaml

sudo -u apache vpn-ca-api-init -i ${HOSTNAME}

###############################################################################
# VPN-SERVER-API
###############################################################################

mkdir /etc/vpn-server-api/${HOSTNAME}
cp /usr/share/doc/vpn-server-api-*/config.yaml.example /etc/vpn-server-api/${HOSTNAME}/config.yaml
chown apache.openvpn /etc/vpn-server-api/${HOSTNAME}/config.yaml
chmod 0440 /etc/vpn-server-api/${HOSTNAME}/config.yaml

# update the IPv4 CIDR and IPv6 prefix to random IP ranges, enable NAT and
# set the extIf
php resources/update_ip.php ${HOSTNAME} ${EXTERNAL_IF}

# create a data directory for the OTP log, initialize the database
mkdir -p /var/lib/openvpn
chown -R openvpn.openvpn /var/lib/openvpn
sudo -u openvpn vpn-server-api-init -i ${HOSTNAME}

# fix SELinux label on /var/lib/openvpn, not sure why this is needed...
restorecon -R /var/lib/openvpn

###############################################################################
# VPN-ADMIN-PORTAL
###############################################################################

mkdir /etc/vpn-admin-portal/${HOSTNAME}
cp /usr/share/doc/vpn-admin-portal-*/config.yaml.example /etc/vpn-admin-portal/${HOSTNAME}/config.yaml
chown root.apache /etc/vpn-admin-portal/${HOSTNAME}/config.yaml
chmod 0640 /etc/vpn-admin-portal/${HOSTNAME}/config.yaml

###############################################################################
# VPN-USER-PORTAL
###############################################################################

mkdir /etc/vpn-user-portal/${HOSTNAME}
cp /usr/share/doc/vpn-user-portal-*/config.yaml.example /etc/vpn-user-portal/${HOSTNAME}/config.yaml
chown root.apache /etc/vpn-user-portal/${HOSTNAME}/config.yaml
chmod 0640 /etc/vpn-user-portal/${HOSTNAME}/config.yaml

###############################################################################
# OPENVPN
###############################################################################

# enable forwarding
echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
echo 'net.ipv6.conf.all.forwarding = 1' >> /etc/sysctl.conf

# forwarding disables accepting RAs on our external interface, so we have to
# explicitly enable it here to make IPv6 work. This is only needed for deploys
# with native IPv6 obtained via router advertisements, not for fixed IPv6
# configurations
echo "net.ipv6.conf.${EXTERNAL_IF}.accept_ra = 2" >> /etc/sysctl.conf
sysctl -p

###############################################################################
# SNIPROXY
###############################################################################

# install the config file
cp resources/sniproxy.conf /etc/sniproxy.conf
sed -i "s/vpn.example/${HOSTNAME}/" /etc/sniproxy.conf

###############################################################################
# UPDATE SECRETS
###############################################################################

# update API secret
php resources/update_api_secret.php ${HOSTNAME}

###############################################################################
# DAEMONS
###############################################################################

systemctl enable php-fpm
systemctl enable httpd

# XXX also here copy the service file and start after network-online.target
systemctl enable sniproxy

# start services
systemctl start php-fpm
systemctl start httpd
systemctl start sniproxy

###############################################################################
# OPENVPN SERVER CONFIG
###############################################################################

# generate the server configuration files
echo "**** CREATING SERVER CONFIG, MAY TAKE A LONG TIME DUE TO DH PARAMS... ****"
vpn-server-api-server-config -i ${HOSTNAME} --generate ${HOSTNAME}

# we need to make a copy of the openvpn service as we want it to only start on
# boot when the network is available. We need this because in 
# multi-pool/multi-instance we do not bind to 0.0.0.0 any longer
# As we don't yet use networkd we have to modify the service file a bit, see 
# https://www.freedesktop.org/wiki/Software/systemd/NetworkTarget/
cp /usr/lib/systemd/system/openvpn@.service /etc/systemd/system/openvpn@.service
sed -i 's/After=network.target/After=network-online.target/' /etc/systemd/system/openvpn@.service

# enable and start OpenVPN
systemctl enable openvpn@server-${HOSTNAME}-internet-{0,1,2,3}
systemctl start openvpn@server-${HOSTNAME}-internet-{0,1,2,3}

###############################################################################
# FIREWALL
###############################################################################

# generate and install the firewall
vpn-server-api-generate-firewall --install

systemctl enable iptables
systemctl enable ip6tables

# flush existing firewall rules if they exist and activate the new ones
systemctl restart iptables
systemctl restart ip6tables

###############################################################################
# POST INSTALL
###############################################################################

# install a crontab to cleanup the old OTP entries stored to protect against
# 2FA code reuse
echo '@daily openvpn vpn-server-api-housekeeping' > /etc/cron.d/vpn-server-api-housekeeping

# parse the journal and write out JSON file with logs every hour
echo '@hourly root journalctl -o json -t vpn-server-api-client-connect -t vpn-server-api-client-disconnect 2>/dev/null | vpn-server-api-parse-journal' > /etc/cron.d/vpn-server-api-log
# execute now
# XXX pipe fail so script stops here, bleh! 
#journalctl -o json -t vpn-server-api-client-connect -t vpn-server-api-client-disconnect 2>/dev/null | vpn-server-api-parse-journal

# automatically generate statistics @ 00:15
echo "15 0 * * * root vpn-server-api-stats -i ${HOSTNAME}" > /etc/cron.d/vpn-server-api-stats
# execute now
# XXX pipe fail above so script stops here, bleh, do not run for now! 
#vpn-server-api-stats

# Secure OpenSSH
# Override the algorithms and ciphers. By default CentOS 7 is not really secure
# See also: https://discovery.cryptosense.com
echo "KexAlgorithms curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group14-sha1" >> /etc/ssh/sshd_config
echo "Ciphers chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com" >> /etc/ssh/sshd_config
# restart OpenSSH
systemctl restart sshd

# Copy index page
mkdir -p /var/www/${HOSTNAME}
cp resources/index.html /var/www/${HOSTNAME}/index.html
sed -i "s/vpn.example/${HOSTNAME}/" /var/www/${HOSTNAME}/index.html
# Copy server info JSON file
cp resources/info.json /var/www/${HOSTNAME}/info.json
sed -i "s/vpn.example/${HOSTNAME}/" /var/www/${HOSTNAME}/info.json

# adding users
USER_PASS=`pwgen 12 -n 1`
ADMIN_PASS=`pwgen 12 -n 1`
vpn-user-portal-add-user  -i ${HOSTNAME} -u me    -p ${USER_PASS}
vpn-admin-portal-add-user -i ${HOSTNAME} -u admin -p ${ADMIN_PASS}

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
