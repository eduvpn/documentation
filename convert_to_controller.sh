#!/bin/sh

#
# Convert a full VPN install to just a controller
#

yum remove -y vpn-server-node
rm -rf /etc/vpn-server-node

semanage port -d -t openvpn_port_t -p tcp 11940-16036
semanage port -d -t openvpn_port_t -p tcp 1195-5290
semanage port -d -t openvpn_port_t -p udp 1195-5290

rm /etc/sysctl.d/70-vpn.conf
sysctl --system

for i in $(systemctl -a --no-legend | grep openvpn-server@ | awk {'print $1'})
do
    systemctl disable --now "${i}"
done
rm -rf /etc/openvpn/server/*

yum remove -y openvpn

cp resources/firewall/controller/iptables /etc/sysconfig/iptables
cp resources/firewall/controller/ip6tables /etc/sysconfig/ip6tables

systemctl restart iptables
systemctl restart ip6tables
