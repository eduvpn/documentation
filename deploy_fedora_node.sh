#!/bin/sh

#
# Deploy a single VPN machine on Fedora
#

###############################################################################
# VARIABLES
###############################################################################

MACHINE_HOSTNAME=$(hostname -f)

# Try to detect external "Default Gateway" Interface, but allow admin override
EXTERNAL_IF=$(ip -4 ro show default | tail -1 | awk {'print $5'})
printf "External Network Interface [%s]: " "${EXTERNAL_IF}"; read -r EXTERNAL_IF

###############################################################################
# SYSTEM
###############################################################################

# SELinux enabled?

if ! /usr/sbin/selinuxenabled
then
    echo "Please **ENABLE** SELinux before running this script!"
    exit 1
fi

PACKAGE_MANAGER=/usr/bin/dnf

###############################################################################
# SOFTWARE
###############################################################################

# disable and stop existing firewalling
systemctl disable --now firewalld >/dev/null 2>/dev/null || true
systemctl disable --now iptables >/dev/null 2>/dev/null || true
systemctl disable --now ip6tables >/dev/null 2>/dev/null || true

cat << EOF > /etc/yum.repos.d/eduVPN_v3-dev.repo
[eduVPN_v3-dev]
name=eduVPN 3.x Development Packages (Fedora \$releasever)
baseurl=https://repo.tuxed.net/eduVPN/v3-dev/rpm/fedora-\$releasever-\$basearch
gpgcheck=1
gpgkey=https://repo.tuxed.net/fkooman+repo@tuxed.net.asc
enabled=1
EOF

# install software (dependencies)
${PACKAGE_MANAGER} -y install php-opcache iptables-nft iptables-services \
    php-cli policycoreutils-python-utils chrony wireguard-tools tmux

# install software (VPN packages)
${PACKAGE_MANAGER} -y install vpn-server-node vpn-maint-scripts vpn-daemon    

###############################################################################
# SELINUX
###############################################################################

# allow OpenVPN to bind to additional ports for client connections
semanage port -a -t openvpn_port_t -p tcp 1195-1258
semanage port -a -t openvpn_port_t -p udp 1195-1258

###############################################################################
# NETWORK
###############################################################################

cat << EOF > /etc/sysctl.d/70-vpn.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
# **ONLY** needed for IPv6 configuration through auto configuration. Do **NOT**
# use this in production as that requires STATIC IP addressess!
net.ipv6.conf.${EXTERNAL_IF}.accept_ra = 2
EOF

sysctl --system

###############################################################################
# DAEMONS
###############################################################################

systemctl enable --now vpn-daemon

###############################################################################
# FIREWALL
###############################################################################

cp resources/firewall/iptables.v3  /etc/sysconfig/iptables
cp resources/firewall/ip6tables.v3 /etc/sysconfig/ip6tables

systemctl enable --now iptables
systemctl enable --now ip6tables
