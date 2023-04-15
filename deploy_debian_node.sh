#!/bin/sh

#
# Deploy a VPN server on Debian/Ubuntu
#

if ! [ "root" = "$(id -u -n)" ]; then
    echo "ERROR: ${0} must be run as root!"; exit 1
fi

###############################################################################
# VARIABLES
###############################################################################

# Try to detect external "Default Gateway" Interface, but allow admin override
EXTERNAL_IF=$(ip -4 ro show default | tail -1 | awk {'print $5'})
printf "External Network Interface [%s]: " "${EXTERNAL_IF}"; read -r EXT_IF
EXTERNAL_IF=${EXT_IF:-${EXTERNAL_IF}}

# whether or not to use the "development" repository (for experimental builds 
# or platforms not yet officially supported)
USE_DEV_REPO=${USE_DEV_REPO:-n}

###############################################################################
# SOFTWARE
###############################################################################

apt update
apt install -y apt-transport-https curl iptables-persistent sudo lsb-release \
    tmux

DEBIAN_ARCH=$(dpkg --print-architecture)
DEBIAN_CODE_NAME=$(/usr/bin/lsb_release -cs)

if [ "${USE_DEV_REPO}" = "y" ]; then
    cp resources/fkooman+repo@tuxed.net.gpg /usr/share/keyrings/fkooman+repo@tuxed.net.gpg
    echo "deb [arch=${DEBIAN_ARCH} signed-by=/usr/share/keyrings/fkooman+repo@tuxed.net.gpg] https://repo.tuxed.net/eduVPN/v3-dev/deb ${DEBIAN_CODE_NAME} main" > /etc/apt/sources.list.d/eduVPN_v3-dev.list
else
    cp resources/repo+v3@eduvpn.org.gpg /usr/share/keyrings/repo+v3@eduvpn.org.gpg
    echo "deb [arch=${DEBIAN_ARCH} signed-by=/usr/share/keyrings/repo+v3@eduvpn.org.gpg] https://repo.eduvpn.org/v3/deb ${DEBIAN_CODE_NAME} main" > /etc/apt/sources.list.d/eduVPN_v3.list
fi

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
