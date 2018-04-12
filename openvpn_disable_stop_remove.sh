#!/bin/sh

INSTANCE=default

#
# Stop and disable all currently active OpenVPN processes
#
for i in $(systemctl -a | grep openvpn-server@${INSTANCE} | awk {'print $1'})
do
    systemctl disable --now "${i}"
done

#
# Remove all existing OpenVPN server configurations and server keys
#
rm -rf /etc/openvpn/server/${INSTANCE}-*
rm -rf /etc/openvpn/server/tls/${INSTANCE}
