#!/bin/sh

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
    echo ERROR: unable to restart firewall, we only support Debian and CentOS/Fedora
    exit 1
fi
