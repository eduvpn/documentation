#!/bin/sh

#
# Backup
# 
# NOTE: this script only backs-up the VPN configuration and data, NOT things
# like SAML configuration, installed LDAP certificates and/or network 
# configuration.
#
# This is only for the installations performed with the "deploy_${DIST}.sh" 
# scripts for the various platforms.

TMP_DIR=$(mktemp -d)
DATETIME=$(date +%Y%m%d%H%M%S)

tar --selinux -cpJf "${TMP_DIR}/backup-${DATETIME}.tar.xz" \
    /etc/vpn-user-portal \
    /etc/vpn-server-api \
    /etc/vpn-server-node \
    /var/lib/vpn-user-portal \
    /var/lib/vpn-server-api

echo "${TMP_DIR}/backup-${DATETIME}.tar.xz"

#
# Restore (as root)
#
# first run the "deploy_${DIST}.sh" script, same as for a new deploy
#
# cd / && tar --selinux -xJf <file.tar.xz>
# vpn-server-node-server-config
#
# enable all the OpenVPN processes (systemctl) if necessary and start them!
# reboot server to make sure everything comes up as expected!
