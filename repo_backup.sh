#!/bin/bash

# this script makes a backup of all, or at least I hope all, repositories that 
# are related to eduVPN / Let's Connect!
# 
# The goal is that if everyting is lost, e.g. all Git hosting servers are gone,
# we can recreate everything, except private keys, from a backup.
#

BACKUP_ROOT=${HOME}

REPO_URL_LIST=(\
    # Website
    https://github.com/eduvpn/eduvpn.org \
    https://github.com/eduvpn/discovery \

    # Server Components
    https://github.com/eduvpn/vpn-lib-common \
    https://github.com/eduvpn/vpn-server-api \
    https://github.com/eduvpn/vpn-user-portal \
    https://github.com/eduvpn/vpn-server-node \
    https://github.com/eduvpn/vpn-admin-portal \
    https://github.com/eduvpn/documentation \
    https://github.com/eduvpn/vpn-portal-artwork \
    https://github.com/eduvpn/php-saml-sp-artwork \
    https://github.com/letsconnectvpn/vpn-portal-artwork \

    # Server Debian Packages \
    https://github.com/eduvpn/eduvpn-debian

    # Server RPM Builder 
    https://github.com/eduvpn/builder \

    # Server RPM Packages \
    https://git.tuxed.net/rpm/vpn-server-node \
    https://git.tuxed.net/rpm/vpn-server-api \
    https://git.tuxed.net/rpm/vpn-user-portal \
    https://git.tuxed.net/rpm/vpn-daemon \
    https://git.tuxed.net/rpm/vpn-ca \
    https://git.tuxed.net/rpm/vpn-portal-artwork-LC \
    https://git.tuxed.net/rpm/vpn-portal-artwork-eduVPN \
    https://git.tuxed.net/rpm/builder \
    https://git.tuxed.net/rpm/php-json-signer \
    https://git.tuxed.net/rpm/php-fkooman-sqlite-migrate \
    https://git.tuxed.net/rpm/php-fkooman-secookie \
    https://git.tuxed.net/rpm/php-LC-openvpn-connection-manager \
    https://git.tuxed.net/rpm/php-fkooman-saml-sp \
    https://git.tuxed.net/rpm/php-fkooman-otp-verifier \
    https://git.tuxed.net/rpm/php-fkooman-oauth2-server \
    https://git.tuxed.net/rpm/php-fkooman-jwt \
    https://git.tuxed.net/rpm/php-LC-common \

    # Extras
    https://github.com/fkooman/php-json-signer \

    # Server Dependencies
    https://github.com/fkooman/php-otp-verifier \
    https://github.com/fkooman/php-saml-sp \
    https://github.com/fkooman/php-jwt \
    https://github.com/fkooman/php-oauth2-server \
    https://github.com/fkooman/php-secookie \
    https://github.com/fkooman/php-sqlite-migrate \
    https://github.com/fkooman/php-oauth2-client \
    https://github.com/letsconnectvpn/vpn-ca \
    https://github.com/letsconnectvpn/vpn-daemon \
    https://github.com/letsconnectvpn/php-openvpn-connection-manager \

    # Apps
    https://github.com/eduvpn/app-update \

    # Linux App
    https://github.com/eduvpn/python-eduvpn-client \

    # Android app
    https://github.com/eduvpn/android \
    https://github.com/eduvpn/ics-openvpn \

    # iOS/macOS app
    https://github.com/eduvpn/apple \
    https://github.com/passepartoutvpn/tunnelkit \

    # DEPRECATED macOS app
    https://github.com/eduvpn/macos \

    # Windows app
    https://github.com/Amebis/eduVPN \
    https://github.com/Amebis/eduOpenVPN \
    https://github.com/Amebis/eduOAuth \
    https://github.com/Amebis/eduJSON \
    https://github.com/Amebis/eduEd25519 \
)

DATE_TIME=$(date +%Y%m%d%H%M%S)
mkdir -p "${BACKUP_ROOT}/repoBackup-${DATE_TIME}" || exit 1
cd "${BACKUP_ROOT}/repoBackup-${DATE_TIME}" || exit 1

for REPO_URL in "${REPO_URL_LIST[@]}"
do
	ENCODED_URL=${REPO_URL//[^a-zA-Z0-9]/_}
    (
        mkdir -p "${ENCODED_URL}" || exit 1
        cd "${ENCODED_URL}" || exit 1
        git clone --bare "${REPO_URL}" || exit 1
    )
done
