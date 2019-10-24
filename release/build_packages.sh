#!/bin/sh

REPO_ROOT=${HOME}/repo-v2

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
cp ./*.pub ./*.sysconfig ./*.service ./*.conf ./*.cron ./*.patch ./gpgkey-* "${HOME}/rpmbuild/SOURCES"
for f in "${PACKAGE_LIST[@]}"
do
    spectool -g -R "${f}".spec || exit 1
    SRPM_FILE=$(rpmbuild -bs "${f}".spec | grep Wrote | cut -d ':' -f 2 | xargs)
	PACKAGE_NAME=$(basename "${SRPM_FILE}" .src.rpm)
	if [ ! -f "${REPO_ROOT}/results/${MOCK_CONFIG}/${PACKAGE_NAME}/success" ]
	then
		# only list the package for building if this exact version did not 
		# build successfully before...
		SRPM_LIST="${SRPM_LIST} ${SRPM_FILE}"
	fi
done

# only call mock when we have something to do...
if [ "" = "${SRPM_LIST}" ]
then
        echo "*** No (new) packages to build!"
        exit 0
fi

echo "Build in progress, this may take a long time..."
(
    mock --chain -r "${MOCK_CONFIG}" --localrepo="${REPO_ROOT}" --arch "${ARCH}" ${SRPM_LIST}
)
