#!/bin/sh

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

rpmdev-setuptree
mkdir -p "${RPM_DIR}/unsigned"
mkdir -p "${SRPM_DIR}/unsigned"

# Create Source RPMs
SRPM_LIST=""

cd rpm || exit
cp ./*.pub ./*.conf ./*.cron ./*.patch ./gpgkey-* "${HOME}/rpmbuild/SOURCES"
for f in "${PACKAGE_LIST[@]}"
do
    spectool -g -R "${f}".spec || exit 1
    SRPM_FILE=$(rpmbuild -bs "${f}".spec | cut -d ':' -f 2)
    SRPM_LIST+=" $(basename ${SRPM_FILE})"
done

echo "Build in progress, this may take a long time..."

(
    # Build RPMs
    cd "${HOME}/rpmbuild/SRPMS" || exit
    if [ -z "${MOCK_FORCE_ARCH}" ]
    then
        RESULT_DIR=$(mockchain -r "${MOCK_CONFIG}" ${SRPM_LIST} | grep "results dir" | cut -d ':' -f 2 | xargs)
    else
        RESULT_DIR=$(mockchain -r "${MOCK_CONFIG}" -m "--forcearch=${MOCK_FORCE_ARCH}" ${SRPM_LIST} | grep "results dir" | cut -d ':' -f 2 | xargs)
    fi
    cp ${RESULT_DIR}/*/*.src.rpm "${SRPM_DIR}/unsigned"
    cp ${RESULT_DIR}/*/*.noarch.rpm ${RESULT_DIR}/*/*.x86_64.rpm ${RESULT_DIR}/*/*.aarch64.rpm "${RPM_DIR}/unsigned"
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
        tar -cJf "${HOME}/rpmRepo-v2-${MOCK_CONFIG}-${DATETIME}.tar.xz" .
    )
)
