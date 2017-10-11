#!/bin/sh

# you can use this script to "reset" a VPN instance, i.e. remove all data and 
# reinitialize it to the state after fresh install using deploy.sh
#
# NOTE: *ALL* VPN configuration will stop working, all users need to obtain
# a new configuration! All OAuth access tokens will become invalid!
#

INSTANCE=default

systemctl stop php-fpm

# remove data
rm -rf /var/lib/vpn-server-api/${INSTANCE}
rm -rf /var/lib/vpn-user-portal/${INSTANCE}
rm -rf /var/lib/vpn-admin-portal/${INSTANCE}

# remove OpenVPN server configuration files for this instance
rm -f /etc/openvpn/server/${INSTANCE}-*.conf
rm -rf /etc/openvpn/server/tls/${INSTANCE}

# recreate data directories and initialize
mkdir /var/lib/vpn-user-portal/${INSTANCE}
chown apache.apache /var/lib/vpn-user-portal/${INSTANCE}
chmod 0700 /var/lib/vpn-user-portal/${INSTANCE}
sudo -u apache vpn-user-portal-init --instance ${INSTANCE}
sudo -u apache vpn-server-api-init --instance ${INSTANCE}

systemctl start php-fpm

# recreate configuration and certificates for "internet" profile, you MAY need
# to recreate for your other profiles as well...

vpn-server-node-server-config --instance ${INSTANCE} --profile internet --generate
systemctl restart "openvpn-server@${INSTANCE}-*"
