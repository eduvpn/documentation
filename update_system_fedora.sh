#!/bin/sh

#
# *ONLY* run this during a maintenance window!
#

OPENVPN_PROCESS_LIST=$(systemctl -a --no-legend | grep openvpn-server@ | awk {'print $1'})

# stop running OpenVPN processes
for OPENVPN_PROCESS in ${OPENVPN_PROCESS_LIST}
do
    echo "Stopping ${OPENVPN_PROCESS}..."
    sudo systemctl stop "${OPENVPN_PROCESS}"
done

sudo systemctl stop httpd
sudo systemctl stop php-fpm

# install updates
sudo dnf -y --refresh update

sudo systemctl start php-fpm
sudo systemctl start httpd

# regenerate OpenVPN config
sudo vpn-server-node-server-config

# start OpenVPN processes
for OPENVPN_PROCESS in ${OPENVPN_PROCESS_LIST}
do
    echo "Starting ${OPENVPN_PROCESS}..."
    sudo systemctl start "${OPENVPN_PROCESS}"
done
