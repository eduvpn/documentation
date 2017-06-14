#!/bin/sh

#
# Deploy a VPN node
#

###############################################################################
# VARIABLES
###############################################################################

# **NOTE**: make sure WEB_FQDN is a valid DNS names with appropriate A 
# (and AAAA) record!

# VARIABLES
# same as in `deploy_controller.sh`
WEB_FQDN=vpn.example

# The interface that connects to "the Internet" (for sysctl)
EXTERNAL_IF=eth0

# the API secret that was in the output of the `deploy_controller.sh` script
API_SECRET=12345

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

# remove firewalld if it is installed, too complicated for our routing
${PACKAGE_MANAGER} -y remove firewalld

# enable EPEL
${PACKAGE_MANAGER} -y install epel-release

curl -L -o /etc/yum.repos.d/fkooman-eduvpn-testing-epel-7.repo \
    https://copr.fedorainfracloud.org/coprs/fkooman/eduvpn-testing/repo/epel-7/fkooman-eduvpn-testing-epel-7.repo

# install software (dependencies)
${PACKAGE_MANAGER} -y install php-opcache iptables iptables-services \
    open-vm-tools php-cli policycoreutils-python

# install software (VPN packages)
${PACKAGE_MANAGER} -y install vpn-server-node

###############################################################################
# SELINUX
###############################################################################

# allow OpenVPN to bind to the management ports
semanage port -a -t openvpn_port_t -p tcp 11940-11955

###############################################################################
# PHP
###############################################################################

# set timezone to UTC
cp resources/70-timezone.ini /etc/php.d/70-timezone.ini

###############################################################################
# VPN-SERVER-NODE
###############################################################################

sed -i "s|http://localhost/vpn-server-api/api.php|https://${WEB_FQDN}/vpn-server-api/api.php|" /etc/vpn-server-node/default/config.php

# the API secret
sed -i "s|XXX-vpn-server-node/vpn-server-api-XXX|${API_SECRET}|" /etc/vpn-server-node/default/config.php

###############################################################################
# NETWORK
###############################################################################

cat << EOF > /etc/sysctl.d/70-vpn.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
# allow RA for IPv6 on external interface, NOT for static IPv6!
net.ipv6.conf.${EXTERNAL_IF}.accept_ra = 2
EOF

sysctl --system

###############################################################################
# DAEMONS
###############################################################################

systemctl enable --now vmtoolsd

###############################################################################
# OPENVPN SERVER CONFIG
###############################################################################

# NOTE: the openvpn-server systemd unit file only allows 10 OpenVPN processes
# by default! 

# generate the server configuration files
vpn-server-node-server-config --profile internet --generate

# enable and start OpenVPN
systemctl enable --now openvpn-server@default-internet-{0,1}

###############################################################################
# FIREWALL
###############################################################################

# generate and install the firewall
vpn-server-node-generate-firewall --install

systemctl enable --now iptables
systemctl enable --now ip6tables

# ALL DONE!
