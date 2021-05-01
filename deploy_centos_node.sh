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

VPN_STABLE_REPO=1
VPN_DEV_REPO=${VPN_DEV_REPO:-0}
if [ "${VPN_DEV_REPO}" = 1 ]
then
    VPN_STABLE_REPO=0
fi

###############################################################################
# SYSTEM
###############################################################################

# SELinux enabled?

if ! /usr/sbin/selinuxenabled
then
    echo "Please **ENABLE** SELinux before running this script!"
    exit 1
fi

PACKAGE_MANAGER=/usr/bin/yum

###############################################################################
# SOFTWARE
###############################################################################

# disable and stop existing firewalling
systemctl disable --now firewalld >/dev/null 2>/dev/null || true
systemctl disable --now iptables >/dev/null 2>/dev/null || true
systemctl disable --now ip6tables >/dev/null 2>/dev/null || true

if grep -q "Red Hat" /etc/redhat-release
then
    # RHEL
    subscription-manager repos --enable=rhel-7-server-optional-rpms
    subscription-manager repos --enable=rhel-7-server-extras-rpms
    ${PACKAGE_MANAGER} -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
else
    # CentOS
    ${PACKAGE_MANAGER} -y install epel-release
fi

# import PGP key and add repository
rpm --import "https://repo.eduvpn.org/v2/rpm/centos+20210419@eduvpn.org.asc"
cat << EOF > /etc/yum.repos.d/LC-v2.repo
[LC-v2]
name=VPN Stable Packages (EL \$releasever)
baseurl=https://repo.letsconnect-vpn.org/2/rpm/epel-7-\$basearch
gpgcheck=1
enabled=${VPN_STABLE_REPO}
EOF

cat << EOF > /etc/yum.repos.d/eduVPN-dev.repo
[eduVPN-dev]
name=eduVPN Development Packages (EL 7)
baseurl=https://repo.tuxed.net/eduVPN/dev/rpm/epel-7-\$basearch
gpgcheck=1
gpgkey=https://repo.tuxed.net/fkooman+repo@tuxed.net.asc
enabled=${VPN_DEV_REPO}
EOF

# install software (dependencies)
${PACKAGE_MANAGER} -y install php-opcache iptables iptables-services php-cli \
    policycoreutils-python chrony

# install software (VPN packages)
${PACKAGE_MANAGER} -y install vpn-server-node vpn-maint-scripts

###############################################################################
# SELINUX
###############################################################################

# allow OpenVPN to bind to the management ports
semanage port -a -t openvpn_port_t -p tcp 11940-16036

# allow OpenVPN to bind to additional ports for client connections
semanage port -a -t openvpn_port_t -p tcp 1195-5290
semanage port -a -t openvpn_port_t -p udp 1195-5290

###############################################################################
# NETWORK
###############################################################################

cat << EOF > /etc/sysctl.d/70-vpn.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
# allow RA for IPv6 on external interface, NOT for static IPv6!
#net.ipv6.conf.eth0.accept_ra = 2
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

cp resources/firewall/node/iptables  /etc/sysconfig/iptables
cp resources/firewall/node/ip6tables /etc/sysconfig/ip6tables

systemctl enable --now iptables
systemctl enable --now ip6tables

###############################################################################
# DONE
###############################################################################
