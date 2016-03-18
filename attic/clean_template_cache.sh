#!/bin/sh
sudo systemctl stop httpd
sudo systemctl stop php-fpm

# clear tpl cache
sudo rm -rf /var/lib/vpn-user-portal/tpl
sudo rm -rf /var/lib/vpn-admin-portal/tpl

sudo systemctl start php-fpm
sudo systemctl start httpd
