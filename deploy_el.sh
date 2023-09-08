#!/bin/sh

#
# Deploy a VPN server on EL
#

if ! [ "root" = "$(id -u -n)" ]; then
    echo "ERROR: ${0} must be run as root!"; exit 1
fi

###############################################################################
# VARIABLES
###############################################################################

MACHINE_HOSTNAME=$(hostname -f)

# DNS name of the Web Server
printf "DNS name of the Web Server [%s]: " "${MACHINE_HOSTNAME}"; read -r WEB_FQDN
WEB_FQDN=${WEB_FQDN:-${MACHINE_HOSTNAME}}
# convert hostname to lowercase
WEB_FQDN=$(echo "${WEB_FQDN}" | tr '[:upper:]' '[:lower:]')

# Try to detect external "Default Gateway" Interface, but allow admin override
EXTERNAL_IF=$(ip -4 ro show default | tail -1 | awk {'print $5'})
printf "External Network Interface [%s]: " "${EXTERNAL_IF}"; read -r EXT_IF
EXTERNAL_IF=${EXT_IF:-${EXTERNAL_IF}}

printf "Enable *Weekly* Automatic Update & Reboot? [y/n] (default=y)? "; read -r AUTO_UPDATE
AUTO_UPDATE=${AUTO_UPDATE:-y}

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

# allow Apache to connect to PHP-FPM
# XXX is this still needed?
setsebool -P httpd_can_network_connect=1

###############################################################################
# SOFTWARE
###############################################################################

# disable and stop existing firewalling
systemctl disable --now firewalld >/dev/null 2>/dev/null || true
systemctl disable --now iptables >/dev/null 2>/dev/null || true
systemctl disable --now ip6tables >/dev/null 2>/dev/null || true
systemctl disable --now nftables >/dev/null 2>/dev/null || true

# stop daemons we use (if they are already running)
systemctl disable --now httpd >/dev/null 2>/dev/null || true
systemctl disable --now php-fpm >/dev/null 2>/dev/null || true
systemctl disable --now vpn-daemon >/dev/null 2>/dev/null || true

# configure repository
if grep "AlmaLinux" /etc/os-release >/dev/null; then
    REPO_DIR_PREFIX=alma+epel-9
elif grep "Rocky Linux" /etc/os-release >/dev/null; then
    REPO_DIR_PREFIX=rocky+epel-9
elif grep "CentOS Stream" /etc/os-release >/dev/null; then
    REPO_DIR_PREFIX=centos-stream+epel-next-9
elif grep "Red Hat Enterprise Linux" /etc/os-release >/dev/null; then
    REPO_DIR_PREFIX=rhel+epel-9
else
    echo "OS not supported!"
    exit 1
fi

if grep "Red Hat Enterprise Linux" /etc/os-release >/dev/null; then
    # on Red Hat Enterprise we need to do some extra stuff to enable EPEL
    # @see https://docs.fedoraproject.org/en-US/epel/
    /usr/bin/subscription-manager repos --enable codeready-builder-for-rhel-9-$(arch)-rpms
    /usr/bin/dnf -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm
fi

if [ "${USE_DEV_REPO}" = "y" ]; then
    # import PGP key
    rpm --import https://repo.tuxed.net/fkooman+repo@tuxed.net.asc
    cat << EOF > /etc/yum.repos.d/eduVPN_v3-dev.repo
[eduVPN_v3-dev]
name=eduVPN 3.x Development Packages (EL 9)
baseurl=https://repo.tuxed.net/eduVPN/v3-dev/rpm/${REPO_DIR_PREFIX}-\$basearch
gpgcheck=1
enabled=1
EOF
else
    # import PGP key
    rpm --import resources/repo+v3@eduvpn.org.asc
    cat << EOF > /etc/yum.repos.d/eduVPN_v3.repo
[eduVPN_v3]
name=eduVPN 3.x Packages (EL 9)
baseurl=https://repo.eduvpn.org/v3/rpm/${REPO_DIR_PREFIX}-\$basearch
gpgcheck=1
enabled=1
EOF
fi

# install software (dependencies)
/usr/bin/dnf -y install epel-release
if grep "CentOS Stream" /etc/os-release >/dev/null; then
    # on CentOS Stream we enable the "epel-next" repository
    /usr/bin/dnf -y install epel-next-release
fi

/usr/bin/dnf -y install mod_ssl php-opcache httpd pwgen cronie \
    nftables php-fpm php-cli policycoreutils-python-utils chrony \
    ipcalc tmux

# install software (VPN packages)
/usr/bin/dnf -y install vpn-server-node vpn-user-portal vpn-maint-scripts

###############################################################################
# AUTO UDPATE
###############################################################################

if [ "${AUTO_UPDATE}" = "y" ]; then
    cat << EOF > /etc/cron.weekly/vpn-maint-update-system
#!/bin/sh
/usr/sbin/vpn-maint-update-system && /usr/sbin/reboot
EOF
    chmod +x /etc/cron.weekly/vpn-maint-update-system
fi

###############################################################################
# APACHE
###############################################################################

# Use a hardened ssl.conf instead of the default, gives A+ on
# https://www.ssllabs.com/ssltest/
cp resources/ssl.fedora.conf /etc/httpd/conf.d/ssl.conf
cp resources/localhost.fedora.conf /etc/httpd/conf.d/localhost.conf

cp resources/vpn.example.fedora.conf "/etc/httpd/conf.d/${WEB_FQDN}.conf"
sed -i "s/vpn.example/${WEB_FQDN}/" "/etc/httpd/conf.d/${WEB_FQDN}.conf"

###############################################################################
# VPN-USER-PORTAL
###############################################################################

# update hostname of VPN server
sed -i "s/vpn.example/${WEB_FQDN}/" "/etc/vpn-user-portal/config.php"

# update the default IP ranges for the profile
# on Debian we can use ipcalc-ng
sed -i "s|10.42.42.0|$(ipcalc -4 -r 24 -n --no-decorate)|" "/etc/vpn-user-portal/config.php"
sed -i "s|fd42::|$(ipcalc -6 -r 64 -n --no-decorate)|" "/etc/vpn-user-portal/config.php"
sed -i "s|10.43.43.0|$(ipcalc -4 -r 24 -n --no-decorate)|" "/etc/vpn-user-portal/config.php"
sed -i "s|fd43::|$(ipcalc -6 -r 64 -n --no-decorate)|" "/etc/vpn-user-portal/config.php"

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
# UPDATE SECRETS
###############################################################################

cp /etc/vpn-user-portal/keys/node.0.key /etc/vpn-server-node/keys/node.key

###############################################################################
# CERTIFICATE
###############################################################################

# generate self signed certificate and key
openssl req \
    -nodes \
    -subj "/CN=${WEB_FQDN}" \
    -x509 \
    -sha256 \
    -newkey rsa:2048 \
    -keyout "/etc/pki/tls/private/${WEB_FQDN}.key" \
    -out "/etc/pki/tls/certs/${WEB_FQDN}.crt" \
    -days 90

###############################################################################
# DAEMONS
###############################################################################

systemctl enable --now php-fpm
systemctl enable --now httpd
systemctl enable --now vpn-daemon
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

/usr/libexec/vpn-server-node/server-config
# in case the deploy script is run multiple times, make sure the services are 
# properly (re)enabled/started with the new configuration
for S in openvpn-server@default-0 openvpn-server@default-1 wg-quick@wg0; do
    systemctl disable --now "${S}"
    systemctl enable --now "${S}"
done

###############################################################################
# FIREWALL
###############################################################################

cp resources/firewall/nftables.conf /etc/sysconfig/nftables.conf
sed -i "s|define EXTERNAL_IF = eth0|define EXTERNAL_IF = ${EXTERNAL_IF}|" /etc/sysconfig/nftables.conf
systemctl enable --now nftables

###############################################################################
# USERS
###############################################################################

USER_NAME="vpn"
USER_PASS=$(pwgen 12 -n 1)

sudo -u apache vpn-user-portal-account --add "${USER_NAME}" --password "${USER_PASS}"

echo "########################################################################"
echo "# Portal"
echo "# ======"
echo "#     https://${WEB_FQDN}/"
echo "#         User Name: ${USER_NAME}"
echo "#         User Pass: ${USER_PASS}"
echo "#"
echo "# Admin"
echo "# ====="
echo "# Add 'vpn' to 'adminUserIdList' in /etc/vpn-user-portal/config.php in"
echo "# order to make yourself an admin in the portal."
echo "########################################################################"
