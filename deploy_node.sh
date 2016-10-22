#!/bin/sh

#
# Deploy Node
#

###############################################################################
# VARIABLES
###############################################################################

# VARIABLES
HOSTNAME=vpn.example
EXTERNAL_IF=eth0

# replace the values below with the values from the controller
PEERVPN_PSK=12345678
CA_API_USER_PASS=aabbcc
SERVER_API_USER_PASS=ccbbaa

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
yum -y install openvpn php-opcache telnet openssl peervpn \
    policycoreutils-python iptables iptables-services patch \
    iptables-services php-cli psmisc net-tools pwgen

# install software (VPN packages)
yum -y install vpn-server-node

###############################################################################
# SELINUX
###############################################################################

# allow OpenVPN to listen on its management ports, and some additional VPN
# ports for load balancing
semanage port -a -t openvpn_port_t -p udp 1195-1201    # allow up to 8 instances
semanage port -a -t openvpn_port_t -p tcp 11940-11947  # allow up to 8 instances

###############################################################################
# PHP
###############################################################################

cp resources/99-eduvpn.ini /etc/php.d/99-eduvpn.ini

###############################################################################
# VPN-SERVER-NODE
###############################################################################

mkdir /etc/vpn-server-node/${HOSTNAME}
cp /usr/share/doc/vpn-server-node-*/config.yaml.example /etc/vpn-server-node/${HOSTNAME}/config.yaml
cp /usr/share/doc/vpn-server-node-*/firewall.yaml.example /etc/vpn-server-node/${HOSTNAME}/firewall.yaml

sed -i "s/#- tap0/- tap0/" /etc/vpn-server-node/${HOSTNAME}/firewall.yaml

sed -i "s/userPass: aabbcc/userPass: ${CA_API_USER_PASS}/" /etc/vpn-server-node/${HOSTNAME}/config.yaml
sed -i "s/userPass: ccbbaa/userPass: ${SERVER_API_USER_PASS}/" /etc/vpn-server-node/${HOSTNAME}/config.yaml

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
# PEERVPN
###############################################################################

cat << EOF > /etc/peervpn/vpn.conf
initpeers ${HOSTNAME} 7000
psk ${PEERVPN_PSK}
interface tap0
EOF

chmod 600 /etc/peervpn/vpn.conf

###############################################################################
# DAEMONS
###############################################################################

systemctl enable NetworkManager
# https://www.freedesktop.org/wiki/Software/systemd/NetworkTarget/
# we need this for sniproxy and openvpn to start only when the network is up
# because we bind to other addresses than 0.0.0.0 and ::
systemctl enable NetworkManager-wait-online
systemctl enable peervpn@vpn

# start services
systemctl restart NetworkManager
systemctl restart NetworkManager-wait-online
systemctl restart peervpn@vpn

# VMware tools, does nothing when not running on VMware
yum -y install open-vm-tools
systemctl enable vmtoolsd
systemctl restart vmtoolsd

###############################################################################
# OPENVPN SERVER CONFIG
###############################################################################

# generate the server configuration files
vpn-server-node-server-config --instance ${HOSTNAME} --profile internet --generate --cn internet.${HOSTNAME}

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
# POST INSTALL
###############################################################################

# Secure OpenSSH
sed -i "s/^#PermitRootLogin yes/PermitRootLogin no/" /etc/ssh/sshd_config
sed -i "s/^PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config 
# Override the algorithms and ciphers. By default CentOS 7 is not really secure
# See also: https://discovery.cryptosense.com
echo "" >> /etc/ssh/sshd_config # first newline, because default file does not end with new line
echo "KexAlgorithms curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group14-sha1" >> /etc/ssh/sshd_config
echo "Ciphers chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com" >> /etc/ssh/sshd_config
# restart OpenSSH
systemctl restart sshd

# ALL DONE!
