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

sudo systemctl stop apache2
sudo systemctl stop php7.0-fpm

# install updates
sudo apt-get update && sudo apt-get -y dist-upgrade 

sudo systemctl start php7.0-fpm
sudo systemctl start apache2

# regenerate OpenVPN config
sudo vpn-server-node-server-config

# start OpenVPN processes
for OPENVPN_PROCESS in ${OPENVPN_PROCESS_LIST}
do
    echo "Starting ${OPENVPN_PROCESS}..."
    sudo systemctl start "${OPENVPN_PROCESS}"
done
