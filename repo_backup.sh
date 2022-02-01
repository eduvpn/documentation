#!/bin/bash

# this script makes a backup of all, or at least I hope all, repositories that 
# are related to eduVPN / Let's Connect!
# 
# The goal is that if everyting is lost, e.g. all Git hosting servers are gone,
# we can recreate everything, except private keys, from a backup.
#
# You can add this to your personal crontab for example (`crontab -e`), make 
# sure `repo_backup.sh` has the +x bit set, i.e. `chmod +x repo_backup.sh`:
#
# @daily (cd /home/fkooman/eduVPN && ./repo_backup.sh)
#

GIT_PATH=/usr/bin/git

REPO_URL_LIST=(\
    # Misc
    https://git.sr.ht/~eduvpn/cdn \
    https://git.sr.ht/~eduvpn/disco.eduvpn.org \
    https://git.sr.ht/~eduvpn/app.eduvpn.org \
    https://git.sr.ht/~eduvpn/status.eduvpn.org \

    # Server Repositories
    https://git.sr.ht/~fkooman/builder.deb \
    https://git.sr.ht/~fkooman/nbuilder.deb \
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

    # Linux App
    https://github.com/eduvpn/python-eduvpn-client \

    # Android app
    https://github.com/eduvpn/android \
    https://github.com/eduvpn/ics-openvpn \
    https://github.com/eduvpn/AppAuth-Android \

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
    https://github.com/Amebis/eduLibsodium \
    https://github.com/Amebis/openvpn \
    https://github.com/Amebis/openvpn-build \
    https://github.com/Amebis/eduEx \
)

for REPO_URL in "${REPO_URL_LIST[@]}"
do
    echo "*** ${REPO_URL}"
    ENCODED_URL=${REPO_URL//[^a-zA-Z0-9]/_}
    (
        mkdir -p repos
        if [ -d "repos/${ENCODED_URL}" ]; then
            # already exists
            cd "repos/${ENCODED_URL}" || exit 1
            ${GIT_PATH} remote update
        else
            # does not yet exist
            ${GIT_PATH} clone -q --mirror "${REPO_URL}" "repos/${ENCODED_URL}"
        fi
    )
done

DATE_TIME=$(date +%Y%m%d%H%M%S)
echo "Creating archive..."
mkdir -p archives || exit 1
tar -cJf "archives/repoBackup-${DATE_TIME}".tar.xz repos || exit 1
