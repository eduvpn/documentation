#!/bin/sh

#
# Deploy a VPN server on Debian/Ubuntu
#

###############################################################################
# VARIABLES
###############################################################################

# Try to detect external "Default Gateway" Interface, but allow admin override
EXTERNAL_IF=$(ip -4 ro show default | tail -1 | awk {'print $5'})
printf "External Network Interface [%s]: " "${EXTERNAL_IF}"; read -r EXT_IF
EXTERNAL_IF=${EXT_IF:-${EXTERNAL_IF}}

###############################################################################
# SOFTWARE
###############################################################################

apt update
apt install -y apt-transport-https curl iptables-persistent sudo lsb-release \
    tmux

DEBIAN_CODE_NAME=$(/usr/bin/lsb_release -cs)
PHP_VERSION=$(/usr/sbin/phpquery -V)

cp resources/repo+v3@eduvpn.org.asc /etc/apt/trusted.gpg.d/repo+v3@eduvpn.org.asc
echo "deb https://repo.eduvpn.org/v3/deb ${DEBIAN_CODE_NAME} main" | tee /etc/apt/sources.list.d/eduVPN_v3.list

apt update

# install software (VPN packages)
apt install -y vpn-server-node vpn-maint-scripts

###############################################################################
# NETWORK
###############################################################################

cat << EOF > /etc/sysctl.d/70-vpn.conf
# **ONLY** needed for IPv6 configuration through auto configuration. Do **NOT**
# use this in production, you SHOULD be using STATIC addresses!
net.ipv6.conf.${EXTERNAL_IF}.accept_ra = 2

# enable IPv4 and IPv6 forwarding
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
EOF

sysctl --system

###############################################################################
# DAEMONS
###############################################################################

systemctl enable --now crond

###############################################################################
# VPN SERVER CONFIG
###############################################################################

# increase the allowed number of processes for the OpenVPN service
mkdir -p /etc/systemd/system/openvpn-server@.service.d
cat << EOF > /etc/systemd/system/openvpn-server@.service.d/override.conf
[Service]
LimitNPROC=127
EOF

# we want to change the owner of the socket, so vpn-daemon can read it, this
# overrides /usr/lib/tmpfiles.d/openvpn.conf as installed by the distribution
# package
cat << EOF > /etc/tmpfiles.d/openvpn.conf
d	/run/openvpn-client	0710	root	root	-
d	/run/openvpn-server	0750	root	nogroup	-
d	/run/openvpn		0755	root	root	-	-
EOF
systemd-tmpfiles --create

###############################################################################
# FIREWALL
###############################################################################

cp resources/firewall/node/iptables  /etc/iptables/rules.v4
cp resources/firewall/node/ip6tables /etc/iptables/rules.v6
sed -i "s|-o eth0|-o ${EXTERNAL_IF}|" /etc/iptables/rules.v4
sed -i "s|-o eth0|-o ${EXTERNAL_IF}|" /etc/iptables/rules.v6

systemctl enable netfilter-persistent
systemctl restart netfilter-persistent
