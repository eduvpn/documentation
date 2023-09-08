#!/bin/sh

#
# Deploy a VPN node on Fedora
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
systemctl disable --now nftables >/dev/null 2>/dev/null || true

if [ "${USE_DEV_REPO}" = "y" ]; then
    # import PGP key
    rpm --import https://repo.tuxed.net/fkooman+repo@tuxed.net.asc
    cat << EOF > /etc/yum.repos.d/eduVPN_v3-dev.repo
[eduVPN_v3-dev]
name=eduVPN 3.x Development Packages (Fedora \$releasever)
baseurl=https://repo.tuxed.net/eduVPN/v3-dev/rpm/fedora-\$releasever-\$basearch
gpgcheck=1
enabled=1
EOF
else
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
fi

# install software (dependencies)
/usr/bin/dnf -y install php-opcache nftables \
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

cp resources/firewall/node/nftables.conf /etc/sysconfig/nftables.conf
sed -i "s|define EXTERNAL_IF = eth0|define EXTERNAL_IF = ${EXTERNAL_IF}|" /etc/sysconfig/nftables.conf
systemctl enable --now nftables
