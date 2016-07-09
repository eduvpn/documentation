#!/bin/sh
sudo systemctl restart sniproxy
sudo systemctl restart httpd
sudo systemctl restart php-fpm
sudo systemctl restart openvpn@server-default-{0,1,2,3}
sudo systemctl restart iptables
sudo systemctl restart ip6tables
