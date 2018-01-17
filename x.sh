#!/bin/sh

printf "DNS name of the Web Server [vpn.example]: "; read -r WEB_FQDN
WEB_FQDN=${WEB_FQDN:-vpn.example}

printf "DNS name of the OpenVPN Server [%s]: " "${WEB_FQDN}"; read -r VPN_FQDN
VPN_FQDN=${VPN_FQDN:-${WEB_FQDN}}

printf "External interface connecting to the Internet [eth0]: "; read -r EXTERNAL_IF
EXTERNAL_IF=${EXTERNAL_IF:-eth0}

echo "${WEB_FQDN}"
echo "${VPN_FQDN}"
echo "${EXTERNAL_IF}"
