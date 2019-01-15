#!/bin/sh

#
# Stop and disable all currently active OpenVPN processes
#
for i in $(systemctl -a --no-legend | grep openvpn-server@ | awk {'print $1'})
do
    systemctl disable --now "${i}"
done

#
# Remove all existing OpenVPN server configurations and server keys
#
rm -rf /etc/openvpn/server/*
