#!/bin/sh

INSTANCE=default

#
# Generate new OpenVPN configurations
#
vpn-server-node-server-config --instance ${INSTANCE} --generate

#
# Enable and start all available OpenVPN processes
#

for i in $(ls /etc/openvpn/server/${INSTANCE}-*.conf)
do
    f=$(basename ${i} .conf)
    systemctl enable --now openvpn-server@${f}
done
