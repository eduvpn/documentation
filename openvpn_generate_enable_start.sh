#!/bin/sh

#
# Generate new OpenVPN configurations
#
vpn-server-node-server-config

#
# Enable and start all available OpenVPN processes
#

for i in /etc/openvpn/server/*.conf
do
    f=$(basename "${i}" .conf)
    systemctl enable --now "openvpn-server@${f}"
done
