#!/bin/sh

# Mock https://fedoraproject.org/wiki/Using_Mock_to_test_package_builds
#
# user MUST be part of mock group:
# sudo usermod -a -G mock myusername 

# Configuration
#REPO_DIR=/tmp/repo
MOCK_CONFIG=epel-7-x86_64
PACKAGE_LIST=(\
    php-bacon-bacon-qr-code\
    php-christian-riesen-otp\
    php-fkooman-oauth2-client\
    php-fkooman-oauth2-server\
    php-fkooman-yubitwee\
    php-fkooman-secookie\
    vpn-lib-common\
    vpn-admin-portal\
    vpn-server-api\
    vpn-server-node\
    vpn-user-portal\
    php-saml-ds\
)
# End of Configuration

rm -rf "${HOME}/rpmbuild/SRPMS"
rm -rf "${HOME}/rpmbuild/RPMS"

rpmdev-setuptree

# create the SRPM files

SRPM_LIST=""
cd rpm || exit
cp ./*.conf ./*.cron ./*.patch "${HOME}/rpmbuild/SOURCES"
for f in "${PACKAGE_LIST[@]}"
do
    spectool -g -R "${f}".spec
    SRPM_FILE=$(rpmbuild -bs "${f}".spec | cut -d ':' -f 2)
    SRPM_LIST+=${SRPM_FILE}
done

mockchain -r "${MOCK_CONFIG}" "${SRPM_LIST}"
