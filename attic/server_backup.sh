#!/bin/sh

# this script creates a backup of all important configuration of a server that
# may have been modified

BACKUP_DIR=$PWD/backup-`date +%Y%m%d%H%M`

mkdir -p ${BACKUP_DIR}
cd ${BACKUP_DIR}

# software
tar -cf vpn-server-api.tar /var/lib/vpn-server-api /etc/vpn-server-api
tar -cf vpn-config-api.tar /var/lib/vpn-config-api /etc/vpn-config-api
tar -cf vpn-user-portal.tar /var/lib/vpn-user-portal /etc/vpn-user-portal
tar -cf vpn-admin-portal.tar /var/lib/vpn-admin-portal /etc/vpn-admin-portal

# OpenVPN
tar -cf openvpn.tar /var/lib/openvpn /etc/openvpn

# Apache
tar -cf httpd.tar /etc/httpd

# Network
tar -cf network.tar /etc/sysconfig/network /etc/sysconfig/network-scripts

# TLS
tar -cf tls.tar /etc/pki/tls

# Firewall
cp /etc/sysconfig/iptables /etc/sysconfig/ip6tables .

# sysctl 
cp /etc/sysctl.conf .

# sniproxy
cp /etc/sniproxy.conf .
