#!/bin/sh

#
# This script fully applies changes made in LC/eduVPN configurations. It stops
# all active OpenVPN processes, removes their config, regenerates their config
# and restart them all. Also the firewall gets updated and restarted
#

# Stop and Disable OpenVPN Server Process(es)
for CONFIG_NAME in $(systemctl list-units "openvpn-server@*" --no-legend | cut -d ' ' -f 1)
do
    systemctl disable --now "${CONFIG_NAME}"
done

# Remove all OpenVPN Server Configuration(s) and Certificate(s)
rm -rf /etc/openvpn/server/*

# (Re)generate OpenVPN Server Configuration(s) and Certificate(s)
vpn-server-node-server-config || exit

# Enable and Start OpenVPN Server Process(es)
for CONFIG_NAME in /etc/openvpn/server/*.conf
do
    CONFIG_NAME=$(basename "${CONFIG_NAME}" .conf)
    systemctl enable --now "openvpn-server@${CONFIG_NAME}"
done
