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
# SOFTWARE
###############################################################################

apt update
apt install -y apt-transport-https curl apache2 php-fpm pwgen \
    nftables sudo lsb-release ipcalc-ng tmux cron

DEBIAN_ARCH=$(dpkg --print-architecture)
DEBIAN_CODE_NAME=$(/usr/bin/lsb_release -cs)
PHP_VERSION=$(/usr/sbin/phpquery -V)

if [ "${USE_DEV_REPO}" = "y" ]; then
    cp resources/fkooman+repo@tuxed.net.gpg /usr/share/keyrings/fkooman+repo@tuxed.net.gpg
    echo "deb [arch=${DEBIAN_ARCH} signed-by=/usr/share/keyrings/fkooman+repo@tuxed.net.gpg] https://repo.tuxed.net/eduVPN/v3-dev/deb ${DEBIAN_CODE_NAME} main" > /etc/apt/sources.list.d/eduVPN_v3-dev.list
else
    cp resources/repo+v3@eduvpn.org.gpg /usr/share/keyrings/repo+v3@eduvpn.org.gpg
    echo "deb [arch=${DEBIAN_ARCH} signed-by=/usr/share/keyrings/repo+v3@eduvpn.org.gpg] https://repo.eduvpn.org/v3/deb ${DEBIAN_CODE_NAME} main" > /etc/apt/sources.list.d/eduVPN_v3.list
fi

apt update

# install software (VPN packages)
apt install -y vpn-user-portal vpn-server-node vpn-maint-scripts

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
# CERTIFICATE
###############################################################################

# generate self signed certificate and key
openssl req \
    -nodes \
    -subj "/CN=${WEB_FQDN}" \
    -x509 \
    -sha256 \
    -newkey rsa:2048 \
    -keyout "/etc/ssl/private/${WEB_FQDN}.key" \
    -out "/etc/ssl/certs/${WEB_FQDN}.crt" \
    -days 90

###############################################################################
# APACHE
###############################################################################

a2enmod ssl headers rewrite proxy_fcgi setenvif 
a2dismod status
a2enconf "php${PHP_VERSION}-fpm"

# VirtualHost
cp resources/ssl.debian.conf /etc/apache2/mods-available/ssl.conf
cp resources/vpn.example.debian.conf "/etc/apache2/sites-available/${WEB_FQDN}.conf"
cp resources/localhost.debian.conf /etc/apache2/sites-available/localhost.conf

# update hostname
sed -i "s/vpn.example/${WEB_FQDN}/" "/etc/apache2/sites-available/${WEB_FQDN}.conf"

a2enconf vpn-user-portal
a2ensite "${WEB_FQDN}" localhost
a2dissite 000-default

systemctl restart apache2

###############################################################################
# PHP
###############################################################################

# update some php-fpm defaults to make PHP on Debian/Ubuntu better suited for
# production loads

cat << EOF > /etc/php/${PHP_VERSION}/fpm/pool.d/www_vpn.conf
[www]
pm = dynamic
pm.max_children = 50
pm.start_servers = 5
pm.min_spare_servers = 5
pm.max_spare_servers = 35
EOF

###############################################################################
# VPN-USER-PORTAL
###############################################################################

# update hostname of VPN server
sed -i "s/vpn.example/${WEB_FQDN}/" "/etc/vpn-user-portal/config.php"

# update the default IP ranges for the profile
# on Debian we can use ipcalc-ng
sed -i "s|10.42.42.0|$(ipcalc-ng -4 -r 24 -n --no-decorate)|" "/etc/vpn-user-portal/config.php"
sed -i "s|fd42::|$(ipcalc-ng -6 -r 64 -n --no-decorate)|" "/etc/vpn-user-portal/config.php"
sed -i "s|10.43.43.0|$(ipcalc-ng -4 -r 24 -n --no-decorate)|" "/etc/vpn-user-portal/config.php"
sed -i "s|fd43::|$(ipcalc-ng -6 -r 64 -n --no-decorate)|" "/etc/vpn-user-portal/config.php"

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
# DAEMONS
###############################################################################

systemctl enable --now "php${PHP_VERSION}-fpm"
systemctl enable --now apache2

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

cp resources/firewall/nftables.conf /etc/nftables.conf
sed -i "s|define EXTERNAL_IF = eth0|define EXTERNAL_IF = ${EXTERNAL_IF}|" /etc/nftables.conf
systemctl enable --now nftables

###############################################################################
# USERS
###############################################################################

USER_NAME="vpn"
USER_PASS=$(pwgen 12 -n 1)

sudo -u www-data vpn-user-portal-account --add "${USER_NAME}" --password "${USER_PASS}"

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
