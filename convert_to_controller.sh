#!/bin/sh

#
# Convert a full VPN install to just a controller
#

dnf -y remove vpn-server-node
rm -rf /etc/vpn-server-node

# allow OpenVPN to bind to the management ports
semanage port -d -t openvpn_port_t -p tcp 11940-16036
# allow OpenVPN to bind to additional ports for client connections
semanage port -d -t openvpn_port_t -p tcp 1195-5290
semanage port -d -t openvpn_port_t -p udp 1195-5290

rm /etc/sysctl.d/70-vpn.conf
sysctl --system

for CONFIG_NAME in $(systemctl list-units "openvpn-server@*" --no-legend | awk '{print $1}')
do
    systemctl disable --now "${CONFIG_NAME}"
done

for CONFIG_NAME in $(systemctl list-units "wg-quick@*" --no-legend | awk '{print $1}')
do
    systemctl disable --now "${CONFIG_NAME}"
done

rm -rf /etc/openvpn/server/*
rm -rf /etc/wireguard/*

cp resources/firewall/controller/iptables /etc/sysconfig/iptables
cp resources/firewall/controller/ip6tables /etc/sysconfig/ip6tables

systemctl restart iptables
systemctl restart ip6tables
