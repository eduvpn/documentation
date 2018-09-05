#!/bin/sh

# you can use this script to "reset" a VPN instance, i.e. remove all data and 
# reinitialize it to the state after fresh install using deploy_${DIST}.sh
#
# NOTE: *ALL* VPN configuration will stop working, all users need to obtain
# a new configuration! All OAuth access tokens will become invalid!
#

INSTANCE=default

(
    $(dirname "$0")/openvpn_disable_stop_remove.sh
)

systemctl stop apache2
systemctl stop php7.0-fpm

# remove data
rm -rf /var/lib/vpn-server-api/${INSTANCE}
rm -rf /var/lib/vpn-user-portal/${INSTANCE}
rm -rf /var/lib/vpn-admin-portal/${INSTANCE}

# initialize
sudo -u www-data vpn-user-portal-init --instance ${INSTANCE}
sudo -u www-data vpn-server-api-init --instance ${INSTANCE}

# regenerate internal API secrets
vpn-server-api-update-api-secrets --instance ${INSTANCE}

systemctl start php7.0-fpm
systemctl start apache2

# regenerate/restart firewall
vpn-server-node-generate-firewall --install     
systemctl restart netfilter-persistent

(
    $(dirname "$0")/openvpn_generate_enable_start.sh
)
