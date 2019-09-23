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

# (Re)generate Firewall
vpn-server-node-generate-firewall --install || exit

# (Re)start Firewall
if [ -f /etc/debian_version ]
then
    systemctl restart netfilter-persistent
elif [ -f /etc/redhat-release ] 
then
    systemctl restart iptables
    systemctl restart ip6tables
else 
    echo "WARNING: we only know how to restart the firewall on Debian and CentOS/Fedora..."
fi

# Enable and Start OpenVPN Server Process(es)
for CONFIG_NAME in /etc/openvpn/server/*.conf
do
    CONFIG_NAME=$(basename "${CONFIG_NAME}" .conf)
    systemctl enable --now "openvpn-server@${CONFIG_NAME}"
done
