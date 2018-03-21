#!/bin/sh

INSTANCE=default

#
# Stop and disable all currently active OpenVPN processes
#
for i in $(systemctl | grep openvpn-server@${INSTANCE} | awk {'print $1'})
do
    systemctl disable --now "${i}"
done

#
# Remove all existing OpenVPN server configurations
#
rm -rf /etc/openvpn/server/${INSTANCE}-*
