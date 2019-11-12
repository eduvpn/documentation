#!/bin/bash

# this script makes a backup of all repositories that are related to eduVPN /
# Let's Connect!

REPO_URL_LIST=(\
    # Website
    https://github.com/eduvpn/eduvpn.org \
    https://github.com/eduvpn/discovery \

    # Server
    https://github.com/eduvpn/vpn-lib-common \
    https://github.com/eduvpn/vpn-server-api \
    https://github.com/eduvpn/vpn-user-portal \
    https://github.com/eduvpn/vpn-server-node \
    https://github.com/eduvpn/documentation \
    https://git.tuxed.net/LC/vpn-portal-artwork-eduVPN \
    https://git.tuxed.net/LC/vpn-portal-artwork-LC \

    # Extras
    https://github.com/fkooman/php-saml-ds \
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

    # Android app
    https://github.com/eduvpn/android \
    https://github.com/eduvpn/ics-openvpn \

    # iOS app
    https://github.com/eduvpn/ios \

    # macOS app
    https://github.com/eduvpn/macos \

    # Windows app
    https://github.com/Amebis/eduVPN \
    https://github.com/Amebis/eduOpenVPN \
    https://github.com/Amebis/eduOAuth \
    https://github.com/Amebis/eduJSON \
    https://github.com/Amebis/eduEd25519 \
)

DATE_TIME=$(date +%Y%m%d%H%M%S)
mkdir -p "${HOME}/repoBackup-${DATE_TIME}" || exit 1
cd "${HOME}/repoBackup-${DATE_TIME}" || exit 1

for REPO_URL in "${REPO_URL_LIST[@]}"
do
    git clone --bare "${REPO_URL}" || exit 1
done
