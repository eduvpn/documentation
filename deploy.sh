#!/bin/sh

#
# Deploy
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

# remove firewalld, too complicated
yum -y remove firewalld

# enable EPEL
yum -y install epel-release

# enable COPR repos
curl -L -o /etc/yum.repos.d/fkooman-eduvpn-dev-epel-7.repo https://copr.fedorainfracloud.org/coprs/fkooman/eduvpn-dev/repo/epel-7/fkooman-eduvpn-dev-epel-7.repo

# install NetworkManager, if not yet installed
yum -y install NetworkManager

# install software (dependencies)
yum -y install openvpn mod_ssl php-opcache httpd telnet openssl \
    policycoreutils-python iptables iptables-services patch sniproxy \
    iptables-services php-fpm php-cli psmisc net-tools php pwgen

# install software (VPN packages)
yum -y install vpn-server-node vpn-server-api vpn-ca-api vpn-admin-portal vpn-user-portal

###############################################################################
# SELINUX
###############################################################################

# allow Apache to connect to PHP-FPM
setsebool -P httpd_can_network_connect=1

# allow OpenVPN to listen on its management ports, and some additional VPN
# ports for load balancing
semanage port -a -t openvpn_port_t -p udp 1195-1201    # allow up to 8 instances
semanage port -a -t openvpn_port_t -p tcp 11940-11947  # allow up to 8 instances

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

# Make Apache not listen on port 80 anymore, sniproxy will take care of that
sed -i "s/Listen 80/#Listen 80/" /etc/httpd/conf/httpd.conf

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

# initialize the CA
mkdir /etc/vpn-ca-api/${HOSTNAME}
cp /usr/share/doc/vpn-ca-api-*/config.yaml.example /etc/vpn-ca-api/${HOSTNAME}/config.yaml

sudo -u apache vpn-ca-api-init --instance ${HOSTNAME}

###############################################################################
# VPN-SERVER-API
###############################################################################

mkdir /etc/vpn-server-api/${HOSTNAME}
cp /usr/share/doc/vpn-server-api-*/config.yaml.example /etc/vpn-server-api/${HOSTNAME}/config.yaml

# OTP log for two-factor auth
sudo -u apache vpn-server-api-init --instance ${HOSTNAME}

# update the IPv4 CIDR and IPv6 prefix to random IP ranges and set the extIf
vpn-server-api-update-ip --instance ${HOSTNAME} --profile internet --host ${HOSTNAME} --ext ${EXTERNAL_IF}

###############################################################################
# VPN-SERVER-NODE
###############################################################################

mkdir /etc/vpn-server-node/${HOSTNAME}
cp /usr/share/doc/vpn-server-node-*/config.yaml.example /etc/vpn-server-node/${HOSTNAME}/config.yaml

###############################################################################
# VPN-ADMIN-PORTAL
###############################################################################

mkdir /etc/vpn-admin-portal/${HOSTNAME}
cp /usr/share/doc/vpn-admin-portal-*/config.yaml.example /etc/vpn-admin-portal/${HOSTNAME}/config.yaml

###############################################################################
# VPN-USER-PORTAL
###############################################################################

mkdir /etc/vpn-user-portal/${HOSTNAME}
cp /usr/share/doc/vpn-user-portal-*/config.yaml.example /etc/vpn-user-portal/${HOSTNAME}/config.yaml

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
systemctl enable sniproxy
systemctl enable NetworkManager
# https://www.freedesktop.org/wiki/Software/systemd/NetworkTarget/
# we need this for sniproxy and openvpn to start only when the network is up
# because we bind to other addresses than 0.0.0.0 and ::
systemctl enable NetworkManager-wait-online

# start services
systemctl restart NetworkManager
systemctl restart NetworkManager-wait-online
systemctl restart php-fpm
systemctl restart httpd
systemctl restart sniproxy

# VMware tools, does nothing when not running on VMware
yum -y install open-vm-tools
systemctl enable vmtoolsd
systemctl restart vmtoolsd

###############################################################################
# OPENVPN SERVER CONFIG
###############################################################################

# generate the server configuration files
vpn-server-node-server-config --instance ${HOSTNAME} --profile internet --generate --cn ${HOSTNAME}

# enable and start OpenVPN
systemctl enable openvpn@server-${HOSTNAME}-internet-{0,1,2,3}
systemctl start openvpn@server-${HOSTNAME}-internet-{0,1,2,3}

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
echo "@daily root /usr/sbin/vpn-server-api-housekeeping --instance ${HOSTNAME}" > /etc/cron.d/vpn-server-api-housekeeping

# parse the journal and write out JSON file with logs every hour
echo '@hourly root /bin/journalctl -o json -t vpn-server-node-client-connect -t vpn-server-node-client-disconnect | /usr/sbin/vpn-server-api-parse-journal' > /etc/cron.d/vpn-server-api-log
# execute now
# XXX pipe fail so script stops here, bleh! 
#journalctl -o json -t vpn-server-api-client-connect -t vpn-server-api-client-disconnect 2>/dev/null | vpn-server-api-parse-journal

# automatically generate statistics @ 00:15
echo "@daily root /usr/sbin/vpn-server-api-stats --instance ${HOSTNAME}" > /etc/cron.d/vpn-server-api-stats
# execute now
# XXX pipe fail above so script stops here, bleh, do not run for now! 
#vpn-server-api-stats

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
vpn-user-portal-add-user  --instance ${HOSTNAME} --user me    --pass ${USER_PASS}
vpn-admin-portal-add-user --instance ${HOSTNAME} --user admin --pass ${ADMIN_PASS}

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
