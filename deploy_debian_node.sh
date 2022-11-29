#!/bin/sh

#
# Deploy a VPN Node
#

###############################################################################
# CONFIGURATION
###############################################################################

DEFAULT_API_URL=http://localhost/vpn-server-api/api.php
printf "API URL of VPN 'Controller' [http://localhost/vpn-server-api/api.php]: "; read -r API_URL
API_URL=${API_URL:-${DEFAULT_API_URL}}

printf "API Secret (from /etc/vpn-server-api/config.php on 'Controller'): "; read -r API_SECRET

###############################################################################
# SOFTWARE
###############################################################################

apt update

# until ALL composer.json of the packages using sqlite have "ext-sqlite3" we'll 
# install it manually here...
DEBIAN_FRONTEND=noninteractive apt install -y apt-transport-https curl \
    iptables-persistent sudo gnupg php-cli lsb-release

DEBIAN_CODE_NAME=$(/usr/bin/lsb_release -cs)

cp resources/debian+20200817@eduvpn.org.asc /etc/apt/trusted.gpg.d/debian+20200817@eduvpn.org.asc
echo "deb https://repo.eduvpn.org/v2/deb ${DEBIAN_CODE_NAME} main" > /etc/apt/sources.list.d/eduVPN_v2.list
apt update

# install software (VPN packages)
DEBIAN_FRONTEND=noninteractive apt install -y vpn-server-node vpn-maint-scripts

###############################################################################
# NETWORK
###############################################################################

cat << EOF > /etc/sysctl.d/70-vpn.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
# allow RA for IPv6 which is disabled by default when enabling IPv6 forwarding 
# **REMOVE** for static IPv6 configurations!
net.ipv6.conf.all.accept_ra = 2
EOF

sysctl --system

###############################################################################
# VPN-SERVER-NODE
###############################################################################
sed -i "s|http://localhost/vpn-server-api/api.php|${API_URL}|" /etc/vpn-server-node/config.php
sed -i "s|XXX-vpn-server-node/vpn-server-api-XXX|${API_SECRET}|" /etc/vpn-server-node/config.php

###############################################################################
# OPENVPN SERVER CONFIG
###############################################################################

# NOTE: the openvpn-server systemd unit file only allows 10 OpenVPN processes
# by default! 

# generate (new) OpenVPN server configuration files and start OpenVPN
vpn-maint-apply-changes

###############################################################################
# FIREWALL
###############################################################################

cp resources/firewall/node/iptables  /etc/iptables/rules.v4
cp resources/firewall/node/ip6tables /etc/iptables/rules.v6

systemctl enable netfilter-persistent
systemctl restart netfilter-persistent

###############################################################################
# DONE
###############################################################################
