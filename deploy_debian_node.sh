#!/bin/sh

#
# Deploy Node
#

###############################################################################
# VARIABLES
###############################################################################

# VARIABLES
INSTANCE=vpn.example
EXTERNAL_IF=eth0
VPN_SERVER_NODE_VPN_CA_API=aabbcc
VPN_SERVER_NODE_VPN_SERVER_API=ccbbaa
MANAGEMENT_IP=10.42.101.101
PROFILE=debian

# **NOTE**: 
# the file /etc/tinc/vpn/hosts/${INSTANCE} from the controller should be placed
# here in the same directory, this will allow tinc to connect to the controller
# and perform the node configuration

###############################################################################
# SYSTEM
###############################################################################

# https://lobste.rs/c/4lfcnm (danielrheath)
set -e # stop the script on errors
set -u # unset variables are an error
set -o pipefail # piping a failed process into a successful one is an arror

# update packages to make sure we have latest version of everything
apt-get update && apt-get dist-upgrade

###############################################################################
# SOFTWARE
###############################################################################

apt-get install openvpn php5-cli tinc open-vm-tools bridge-utils xz-utils \
    curl git php5-curl

###############################################################################
# NETWORK 
###############################################################################

cat << EOF > /etc/network/interfaces.d/br0
auto br0
iface br0 inet static
    address ${MANAGEMENT_IP}
    netmask 255.255.0.0
    bridge_ports none
EOF

# activate the interface
ifup br0

cat << EOF > /etc/sysctl.d/42-eduvpn.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
# disable below for static IPv6 configurations
net.ipv6.conf.${EXTERNAL_IF}.accept_ra = 2
EOF

sysctl --system

###############################################################################
# PHP
###############################################################################

cp resources/99-eduvpn.ini /etc/php5/cli/conf.d/99-eduvpn.ini

###############################################################################
# VPN-SERVER-NODE
###############################################################################

(
cd /opt
rm -rf vpn-server-node
git clone https://github.com/eduvpn/vpn-server-node.git
cd vpn-server-node
curl -O https://getcomposer.org/download/1.2.2/composer.phar
php composer.phar install
cd config
mkdir vpn.example
cp config.yaml.example vpn.example/config.yaml
cp firewall.yaml.example firewall.yaml
sed -i "s/#- br0/- br0/" firewall.yaml
sed -i "s/userPass: aabbcc/userPass: ${VPN_SERVER_NODE_VPN_CA_API}/" ${INSTANCE}/config.yaml
sed -i "s/userPass: ccbbaa/userPass: ${VPN_SERVER_NODE_VPN_SERVER_API}/" ${INSTANCE}/config.yaml
sed -i "s/vpnUser: openvpn/vpnUser: nobody/" ${INSTANCE}/config.yaml
sed -i "s/vpnGroup: openvpn/vpnGroup: nogroup/" ${INSTANCE}/config.yaml

ln -s /etc/openvpn /opt/vpn-server-node/openvpn-config

ln -s /opt/vpn-server-node/libexec/vpn-server-node-client-connect /usr/libexec/vpn-server-node-client-connect
ln -s /opt/vpn-server-node/libexec/vpn-server-node-client-disconnect /usr/libexec/vpn-server-node-client-disconnect
ln -s /opt/vpn-server-node/libexec/vpn-server-node-verify-otp /usr/libexec/vpn-server-node-verify-otp

ln -s /opt/vpn-server-node/bin/vpn-server-node-generate-firewall /usr/bin/vpn-server-node-generate-firewall
ln -s /opt/vpn-server-node/bin/vpn-server-node-server-config /usr/bin/vpn-server-node-server-config
)

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

# copy controller file to the correct place
# XXX check if the file is there, bail otherwise, at start of this script!
cp "${TINC_INSTANCE_NAME}" /etc/tinc/vpn/hosts

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
read

###############################################################################
# DAEMONS
###############################################################################

systemctl enable tinc@vpn
systemctl restart tinc@vpn

###############################################################################
# OPENVPN SERVER CONFIG
###############################################################################

# remove existing config
rm -rf /etc/openvpn/*

# generate the server configuration files
vpn-server-node-server-config --instance ${INSTANCE} --profile ${PROFILE} --generate --cn ${PROFILE}01.${INSTANCE}

# enable and start OpenVPN
systemctl enable openvpn@server-${INSTANCE}-${PROFILE}-0
systemctl enable openvpn@server-${INSTANCE}-${PROFILE}-1
systemctl enable openvpn@server-${INSTANCE}-${PROFILE}-2
systemctl enable openvpn@server-${INSTANCE}-${PROFILE}-3

systemctl start openvpn@server-${INSTANCE}-${PROFILE}-0
systemctl start openvpn@server-${INSTANCE}-${PROFILE}-1
systemctl start openvpn@server-${INSTANCE}-${PROFILE}-2
systemctl start openvpn@server-${INSTANCE}-${PROFILE}-3

###############################################################################
# FIREWALL
###############################################################################

# generate and install the firewall
#vpn-server-node-generate-firewall --install

#systemctl enable iptables
#systemctl enable ip6tables

# flush existing firewall rules if they exist and activate the new ones
#systemctl restart iptables
#systemctl restart ip6tables

###############################################################################
# SSHD
###############################################################################

#cp resources/sshd_config /etc/ssh/sshd_config
#chmod 0600 /etc/ssh/sshd_config
#systemctl restart sshd

# ALL DONE!
