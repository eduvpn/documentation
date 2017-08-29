#!/bin/sh

# you can use this script to "reset" a VPN instance, i.e. remove all data and 
# reinitialize it to the state after fresh install using deploy.sh
#
# NOTE: *ALL* VPN configuration will stop working, all users need to obtain
# a new configuration! All OAuth access tokens will become invalid!
#

INSTANCE=default

systemctl stop php-fpm

rm -rf /var/lib/vpn-server-api/${INSTANCE}
rm -rf /var/lib/vpn-user-portal/${INSTANCE}
rm -rf /var/lib/vpn-admin-portal/${INSTANCE}

mkdir /var/lib/vpn-user-portal/${INSTANCE}
chown apache.apache /var/lib/vpn-user-portal/${INSTANCE}
chmod 0700 /var/lib/vpn-user-portal/${INSTANCE}
sudo -u apache vpn-user-portal-init --instance ${INSTANCE}
sudo -u apache vpn-server-api-init --instance ${INSTANCE}

systemctl start php-fpm

vpn-server-node-server-config --instance ${INSTANCE} --profile internet --generate
systemctl restart "openvpn-server@*"
