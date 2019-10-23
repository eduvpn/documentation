#!/bin/sh

# list of packages to build, in order
PACKAGE_LIST=(\
    php-fkooman-saml-sp \
    php-fkooman-jwt \
    php-fkooman-otp-verifier \
    php-fkooman-oauth2-server \
    php-fkooman-secookie \
    php-fkooman-sqlite-migrate \
    php-LC-openvpn-connection-manager \
    php-LC-common \
    vpn-server-api \
    vpn-server-node \
    vpn-user-portal \
    php-saml-ds \
    php-json-signer \
    vpn-portal-artwork-eduVPN \
    vpn-portal-artwork-LC \
    php-saml-ds-artwork-eduVPN \
)

# Create Source RPMs
SRPM_LIST=""

cd rpm || exit 1
cp ./*.pub ./*.conf ./*.cron ./*.patch ./gpgkey-* "${HOME}/rpmbuild/SOURCES"
for f in "${PACKAGE_LIST[@]}"
do
    spectool -g -R "${f}".spec || exit 1
    SRPM_FILE=$(rpmbuild -bs "${f}".spec | cut -d ':' -f 2)
    SRPM_LIST+=" ${SRPM_FILE}"
done

echo "Build in progress, this may take a long time..."
(
    mock --chain -r "${MOCK_CONFIG}" --localrepo="${REPO_ROOT}" --arch "${ARCH}" ${SRPM_LIST} 
)

(
    # Create Archive
    DATETIME=$(date +%Y%m%d%H%M%S)
    (
        cd "${REPO_ROOT}" || exit 1
        tar -cJf "${HOME}/rpmRepo-v2-${MOCK_CONFIG}-${DATETIME}.tar.xz" .
    )
)
