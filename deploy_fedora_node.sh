#!/bin/sh

#
# Deploy a VPN node on Fedora
#

###############################################################################
# VARIABLES
###############################################################################

# Try to detect external "Default Gateway" Interface, but allow admin override
EXTERNAL_IF=$(ip -4 ro show default | tail -1 | awk {'print $5'})
printf "External Network Interface [%s]: " "${EXTERNAL_IF}"; read -r EXT_IF
EXTERNAL_IF=${EXT_IF:-${EXTERNAL_IF}}

###############################################################################
# SYSTEM
###############################################################################

# SELinux enabled?

if ! /usr/sbin/selinuxenabled
then
    echo "Please **ENABLE** SELinux before running this script!"
    exit 1
fi

###############################################################################
# SOFTWARE
###############################################################################

# disable and stop existing firewalling
systemctl disable --now firewalld >/dev/null 2>/dev/null || true
systemctl disable --now iptables >/dev/null 2>/dev/null || true
systemctl disable --now ip6tables >/dev/null 2>/dev/null || true

# import PGP key
rpm --import resources/repo+v3@eduvpn.org.asc
# configure repository
cat << EOF > /etc/yum.repos.d/eduVPN_v3.repo
[eduVPN_v3]
name=eduVPN 3.x Packages (Fedora \$releasever)
baseurl=https://repo.eduvpn.org/v3/rpm/fedora-\$releasever-\$basearch
gpgcheck=1
enabled=1
EOF

# install software (dependencies)
/usr/bin/dnf -y install php-opcache iptables-nft iptables-services \
    php-cli policycoreutils-python-utils chrony cronie tmux

# install software (VPN packages)
/usr/bin/dnf -y install vpn-server-node vpn-maint-scripts

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

systemctl enable --now vpn-daemon
systemctl enable --now crond

###############################################################################
# FIREWALL
###############################################################################

cp resources/firewall/iptables.v3  /etc/sysconfig/iptables
cp resources/firewall/ip6tables.v3 /etc/sysconfig/ip6tables

sed -i "s|-o eth0|-o ${EXTERNAL_IF}|" /etc/sysconfig/iptables
sed -i "s|-o eth0|-o ${EXTERNAL_IF}|" /etc/sysconfig/ip6tables

systemctl enable --now iptables
systemctl enable --now ip6tables
