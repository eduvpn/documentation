#!/bin/sh
EXTERNAL_IF=eth0
EXTERNAL_IP=$(ifconfig ${EXTERNAL_IF} | grep inet | grep netmask | awk {'print $2'})
dnf -y --refresh update
dnf -y copr enable fkooman/eduvpn-testing
dnf -y remove firewalld
dnf -y install vpn-server-api vpn-server-node vpn-user-portal vpn-admin-portal httpd php iptables iptables-services
echo 'net.ipv4.ip_forward = 1' | tee /etc/sysctl.conf > /dev/null
sysctl --system
setsebool -P httpd_can_network_connect=1
semanage port -a -t openvpn_port_t -p tcp 11940
systemctl enable httpd
sudo -u apache vpn-server-api-init
sed -i 's/Require local/#Require local/' /etc/httpd.conf/vpn-user-portal.conf
sed -i 's/Require local/#Require local/' /etc/httpd.conf/vpn-admin-portal.conf
sed -i 's/#Require all granted/Require all granted/' /etc/httpd.conf/vpn-user-portal.conf
sed -i 's/#Require all granted/Require all granted/' /etc/httpd.conf/vpn-admin-portal.conf
vpn-user-portal-add-user --user foo --pass bar
vpn-admin-portal-add-user --user foo --pass bar
vpn-server-api-update-ip --profile internet --host "${EXTERNAL_IP}" --ext "${EXTERNAL_IF}"
systemctl start httpd
vpn-server-node-server-config --profile internet --generate
systemctl enable openvpn@default-internet-0
systemctl start openvpn@default-internet-0
vpn-server-node-generate-firewall --install
systemctl enable iptables
systemctl restart iptables
