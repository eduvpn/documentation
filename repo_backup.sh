#!/bin/bash

# this script makes a backup of all, or at least I hope all, repositories that 
# are related to eduVPN / Let's Connect!
# 
# The goal is that if everyting is lost, e.g. all Git hosting servers are gone,
# we can recreate everything, except private keys, from a backup.
#

BACKUP_ROOT=${HOME}
GIT_PATH=/usr/bin/git

REPO_URL_LIST=(\
    # Misc
    https://git.sr.ht/~eduvpn/disco.eduvpn.org
    https://git.sr.ht/~eduvpn/app.eduvpn.org
    https://git.sr.ht/~eduvpn/status.eduvpn.org

    # Server Repositories
    https://git.sr.ht/~fkooman/builder.deb \
    https://git.sr.ht/~fkooman/builder.rpm \
    https://git.sr.ht/~fkooman/php-constant-time.deb \
    https://git.sr.ht/~fkooman/php-jwt \
    https://git.sr.ht/~fkooman/php-jwt.deb \
    https://git.sr.ht/~fkooman/php-jwt.rpm \
    https://git.sr.ht/~fkooman/php-oauth2-client \
    https://git.sr.ht/~fkooman/php-oauth2-server \
    https://git.sr.ht/~fkooman/php-oauth2-server.deb \
    https://git.sr.ht/~fkooman/php-oauth2-server.rpm \
    https://git.sr.ht/~fkooman/php-openvpn-connection-manager \
    https://git.sr.ht/~fkooman/php-openvpn-connection-manager.deb \
    https://git.sr.ht/~fkooman/php-openvpn-connection-manager.rpm \
    https://git.sr.ht/~fkooman/php-otp-verifier \
    https://git.sr.ht/~fkooman/php-otp-verifier.deb \
    https://git.sr.ht/~fkooman/php-otp-verifier.rpm \
    https://git.sr.ht/~fkooman/php-saml-sp \
    https://git.sr.ht/~fkooman/php-saml-sp-artwork-eduVPN \
    https://git.sr.ht/~fkooman/php-saml-sp-artwork-eduVPN.deb \
    https://git.sr.ht/~fkooman/php-saml-sp-artwork-eduVPN.rpm \
    https://git.sr.ht/~fkooman/php-saml-sp.deb \
    https://git.sr.ht/~fkooman/php-saml-sp.rpm \
    https://git.sr.ht/~fkooman/php-secookie \
    https://git.sr.ht/~fkooman/php-secookie.deb \
    https://git.sr.ht/~fkooman/php-secookie.rpm \
    https://git.sr.ht/~fkooman/php-sqlite-migrate \
    https://git.sr.ht/~fkooman/php-sqlite-migrate.deb \
    https://git.sr.ht/~fkooman/php-sqlite-migrate.rpm \
    https://git.sr.ht/~fkooman/php-yubitwee \
    https://git.sr.ht/~fkooman/vpn-ca \
    https://git.sr.ht/~fkooman/vpn-ca.deb \
    https://git.sr.ht/~fkooman/vpn-ca.rpm \
    https://git.sr.ht/~fkooman/vpn-daemon \
    https://git.sr.ht/~fkooman/vpn-daemon.deb \
    https://git.sr.ht/~fkooman/vpn-daemon.rpm \
    https://git.sr.ht/~fkooman/vpn-documentation \
    https://git.sr.ht/~fkooman/vpn-lib-common \
    https://git.sr.ht/~fkooman/vpn-lib-common.deb \
    https://git.sr.ht/~fkooman/vpn-lib-common.rpm \
    https://git.sr.ht/~fkooman/vpn-maint-scripts \
    https://git.sr.ht/~fkooman/vpn-maint-scripts.deb \
    https://git.sr.ht/~fkooman/vpn-maint-scripts.rpm \
    https://git.sr.ht/~fkooman/vpn-portal-artwork-eduVPN \
    https://git.sr.ht/~fkooman/vpn-portal-artwork-eduVPN.deb \
    https://git.sr.ht/~fkooman/vpn-portal-artwork-eduVPN.rpm \
    https://git.sr.ht/~fkooman/vpn-portal-artwork-LC \
    https://git.sr.ht/~fkooman/vpn-portal-artwork-LC.deb \
    https://git.sr.ht/~fkooman/vpn-portal-artwork-LC.rpm \
    https://git.sr.ht/~fkooman/vpn-server-api \
    https://git.sr.ht/~fkooman/vpn-server-api.deb \
    https://git.sr.ht/~fkooman/vpn-server-api.rpm \
    https://git.sr.ht/~fkooman/vpn-server-node \
    https://git.sr.ht/~fkooman/vpn-server-node.deb \
    https://git.sr.ht/~fkooman/vpn-server-node.rpm \
    https://git.sr.ht/~fkooman/vpn-user-portal \
    https://git.sr.ht/~fkooman/vpn-user-portal.deb \
    https://git.sr.ht/~fkooman/vpn-user-portal.rpm \
    https://git.sr.ht/~fkooman/wg-daemon \
    https://git.sr.ht/~fkooman/wg-daemon.rpm \

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
        ${GIT_PATH} clone --mirror "${REPO_URL}"
    )
done
