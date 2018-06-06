#!/bin/sh

PACKAGE_LIST=(\
    php-christian-riesen-otp \
    php-fkooman-oauth2-client \
    php-fkooman-oauth2-server \
    php-fkooman-yubitwee \
    php-fkooman-secookie \
    php-LC-openvpn-connection-manager \
    vpn-lib-common \
    vpn-admin-portal \
    vpn-server-api \
    vpn-server-node \
    vpn-user-portal \
    php-saml-ds \
    php-json-signer \
    vpn-portal-artwork-eduVPN \
    vpn-portal-artwork-LC \
    php-saml-ds-artwork-eduVPN \
)

rpmdev-setuptree
mkdir -p "${RPM_DIR}/unsigned"
mkdir -p "${SRPM_DIR}/unsigned"

# Create Source RPMs
SRPM_LIST=""
cd rpm || exit
cp ./*.conf ./*.cron ./*.patch "${HOME}/rpmbuild/SOURCES"
for f in "${PACKAGE_LIST[@]}"
do
    spectool -g -R "${f}".spec
    SRPM_FILE=$(rpmbuild -bs "${f}".spec | cut -d ':' -f 2)
    SRPM_LIST+=" $(basename ${SRPM_FILE})"
done

echo "Build in progress, this may take a long time..."

(
    # Build RPMs
    cd "${HOME}/rpmbuild/SRPMS" || exit
    RESULT_DIR=$(mockchain -r "${MOCK_CONFIG}" ${SRPM_LIST} | grep "results dir" | cut -d ':' -f 2 | xargs)
    cp ${RESULT_DIR}/*/*.src.rpm "${SRPM_DIR}/unsigned"
    cp ${RESULT_DIR}/*/*.noarch.rpm ${RESULT_DIR}/*/*.x86_64.rpm "${RPM_DIR}/unsigned"
)

(
    # Sign RPMs
    rpm --addsign ${RPM_DIR}/unsigned/* ${SRPM_DIR}/unsigned/*
    cp ${RPM_DIR}/unsigned/* "${RPM_DIR}/"
    cp ${SRPM_DIR}/unsigned/* "${SRPM_DIR}/"
    rm -rf "${RPM_DIR}/unsigned" "${SRPM_DIR}/unsigned"

    # Create Repositories
    cd "${RPM_DIR}" || exit
    createrepo_c .
    cd "${SRPM_DIR}" || exit
    createrepo_c .
)

(
    # Create Archive
    DATETIME=$(date +%Y%m%d%H%M%S)
    (
        cd "${REPO_ROOT}" || exit
        tar -cJf "${HOME}/rpmRepo-${MOCK_CONFIG}-${DATETIME}.tar.xz" .
    )
)
