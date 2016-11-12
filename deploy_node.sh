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
PROFILE=internet

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
yum -y clean expire-cache && yum -y update

###############################################################################
# NETWORK 
###############################################################################

cat << EOF > /etc/sysconfig/network-scripts/ifcfg-br0
DEVICE="br0"
ONBOOT="yes"
TYPE="Bridge"
IPADDR0=${MANAGEMENT_IP}
PREFIX0=16
EOF

# activate the interface
ifup br0

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
yum -y install NetworkManager openvpn php-opcache telnet openssl tinc \
    policycoreutils-python iptables iptables-services patch \
    iptables-services php-cli psmisc net-tools pwgen open-vm-tools bridge-utils

# install software (VPN packages)
yum -y install vpn-server-node

###############################################################################
# SELINUX
###############################################################################

# allow OpenVPN to listen on its management ports, and some additional VPN
# ports for load balancing
semanage port -a -t openvpn_port_t -p udp 1195-1201 || true   # allow up to 8 instances
semanage port -a -t openvpn_port_t -p tcp 1195-1201 || true   # allow up to 8 instances
semanage port -a -t openvpn_port_t -p tcp 11940-11947 || true # allow up to 8 instances

###############################################################################
# PHP
###############################################################################

cp resources/99-eduvpn.ini /etc/php.d/99-eduvpn.ini

###############################################################################
# VPN-SERVER-NODE
###############################################################################

# remove existing data
rm -rf /etc/vpn-server-node/*

mkdir -p /etc/vpn-server-node/${INSTANCE}
cp /usr/share/doc/vpn-server-node-*/config.yaml.example /etc/vpn-server-node/${INSTANCE}/config.yaml
cp /usr/share/doc/vpn-server-node-*/dh.pem /etc/vpn-server-node/dh.pem
cp /usr/share/doc/vpn-server-node-*/firewall.yaml.example /etc/vpn-server-node/${INSTANCE}/firewall.yaml

sed -i "s/#- br0/- br0/" /etc/vpn-server-node/${INSTANCE}/firewall.yaml

sed -i "s/userPass: aabbcc/userPass: ${VPN_SERVER_NODE_VPN_CA_API}/" /etc/vpn-server-node/${INSTANCE}/config.yaml
sed -i "s/userPass: ccbbaa/userPass: ${VPN_SERVER_NODE_VPN_SERVER_API}/" /etc/vpn-server-node/${INSTANCE}/config.yaml

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
Name = ${TINC_NAME}
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
echo 
echo "Press enter to continue..."
read

###############################################################################
# DAEMONS
###############################################################################

systemctl enable NetworkManager
systemctl enable NetworkManager-wait-online
systemctl enable tinc@vpn
systemctl enable vmtoolsd

# start services
systemctl restart NetworkManager
systemctl restart NetworkManager-wait-online
systemctl restart tinc@vpn
systemctl restart vmtoolsd

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
