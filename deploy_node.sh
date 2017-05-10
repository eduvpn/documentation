#!/bin/sh

#
# Deploy Node
#

###############################################################################
# VARIABLES
###############################################################################

# VARIABLES
# copy/paste these from the output of the deploy_controller.sh script
INSTANCE=vpn.example
EXTERNAL_IF=eth0
MANAGEMENT_IP=10.42.101.101
PROFILE=internet
API_SECRET=abcdef
TINC_CONFIG=AABBCC==

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
${PACKAGE_MANAGER} -y install NetworkManager php-opcache tinc \
    policycoreutils-python iptables iptables-services \
    php-cli open-vm-tools bridge-utils

# install software (VPN packages)
${PACKAGE_MANAGER} -y install vpn-server-node

###############################################################################
# NETWORK
###############################################################################

systemctl enable NetworkManager
systemctl restart NetworkManager

nmcli connection del bridge-br0 2>/dev/null # delete if it is already there...
# create a bridge for the management service(s)
nmcli connection add type bridge ifname br0 ip4 ${MANAGEMENT_IP}/16

###############################################################################
# SELINUX
###############################################################################

# allow OpenVPN to listen on its management ports, and some additional VPN
# ports for load balancing

semanage port -a -t openvpn_port_t -p udp 1195-1201     # allow up to 8 instances
semanage port -a -t openvpn_port_t -p tcp 1195-1201     # allow up to 8 instances
semanage port -a -t openvpn_port_t -p tcp 11940-11947   # allow up to 8 instances

###############################################################################
# PHP
###############################################################################

cp resources/99-eduvpn.ini /etc/php.d/99-eduvpn.ini

###############################################################################
# VPN-SERVER-NODE
###############################################################################

# remove existing data
rm -rf /etc/vpn-server-node/${INSTANCE}

mkdir -p /etc/vpn-server-node/${INSTANCE}
cp /etc/vpn-server-node/default/config.php /etc/vpn-server-node/${INSTANCE}/config.php

sed -i "s|//'br0'|'br0'|" /etc/vpn-server-node/firewall.php
# add instance for firewall generation instead of default
sed -i "s|'default'|'${INSTANCE}'|" /etc/vpn-server-node/firewall.php

sed -i "s|XXX-vpn-server-node/vpn-server-api-XXX|${API_SECRET}|" /etc/vpn-server-node/${INSTANCE}/config.php

# point to our CA API and Server API
sed -i "s|localhost/vpn-server-api|10.42.101.100:8008|" /etc/vpn-server-node/${INSTANCE}/config.php

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
# TINC
###############################################################################

TINC_INSTANCE_NAME=$(echo ${INSTANCE} | sed 's/\./_/g')
TINC_NODE_NAME=$(echo ${PROFILE}.${INSTANCE} | sed 's/\./_/g')

rm -rf /etc/tinc
mkdir -p /etc/tinc/vpn

cat << EOF > /etc/tinc/vpn/tinc.conf
Name = ${TINC_NODE_NAME}
ConnectTo = ${TINC_INSTANCE_NAME}
Mode = switch
EOF

cp resources/tinc-up /etc/tinc/vpn/tinc-up
cp resources/tinc-down /etc/tinc/vpn/tinc-down
chmod +x /etc/tinc/vpn/tinc-up /etc/tinc/vpn/tinc-down

mkdir -p /etc/tinc/vpn/hosts
touch "/etc/tinc/vpn/hosts/${TINC_NODE_NAME}"

printf "\n\n" | tincd -n vpn -K 4096

cp resources/tinc\@.service /etc/systemd/system
systemctl daemon-reload

echo ${TINC_CONFIG} | base64 -d | tee "/etc/tinc/vpn/hosts/${TINC_INSTANCE_NAME}" >/dev/null

# now we have to copy the public key to the controller, out of band for now
echo "---- cut ----"
cat "/etc/tinc/vpn/hosts/${TINC_NODE_NAME}"
echo "---- /cut ----"
echo
echo "Put the above in /etc/tinc/vpn/hosts/${TINC_NODE_NAME} on the controller"
echo "And reload tinc:"
echo "    sudo systemctl reload tinc@vpn"
echo 
echo "Press enter to continue..."
read -r

###############################################################################
# DAEMONS
###############################################################################

systemctl enable NetworkManager-wait-online
systemctl enable tinc@vpn
systemctl enable vmtoolsd

# start services
systemctl restart tinc@vpn
systemctl restart vmtoolsd

# wait a bit, so hopefully tinc is up and we can reach the controller...
sleep 10

# ping the controller, hopefully the connection will be established...
ping -c 4 10.42.101.100

###############################################################################
# OPENVPN SERVER CONFIG
###############################################################################

# NOTE: the openvpn-server systemd unit file only allows 10 OpenVPN processes
# by default! 

# remove existing config
rm -rf /etc/openvpn/server/*

# generate the server configuration files
vpn-server-node-server-config --instance ${INSTANCE} --profile ${PROFILE} --generate

# enable and start OpenVPN
systemctl enable openvpn-server@${INSTANCE}-${PROFILE}-0
systemctl enable openvpn-server@${INSTANCE}-${PROFILE}-1
systemctl enable openvpn-server@${INSTANCE}-${PROFILE}-2
systemctl enable openvpn-server@${INSTANCE}-${PROFILE}-3

systemctl restart openvpn-server@${INSTANCE}-${PROFILE}-0
systemctl restart openvpn-server@${INSTANCE}-${PROFILE}-1
systemctl restart openvpn-server@${INSTANCE}-${PROFILE}-2
systemctl restart openvpn-server@${INSTANCE}-${PROFILE}-3

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

# ALL DONE!
