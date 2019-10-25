#!/bin/sh

REPO_ROOT=${HOME}/repo-v2
PACKAGE_BRANCH=master

# targets to build for
TARGET_LIST=(\
    epel-7-x86_64 \
    fedora-30-x86_64 \
    fedora-30-aarch64 \
    fedora-31-x86_64 \
)

for TARGET_NAME in "${TARGET_LIST[@]}"
do
    # determine ARCH based on target name
    ARCH=$(echo ${TARGET_NAME} | cut -d '-' -f 3)

    # list of packages to build, *in this order*
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
        vpn-portal-artwork-eduVPN \
        vpn-portal-artwork-LC \
    )

    SRPM_LIST=""

    # generate source RPMs for all the packages and add them to the list of 
    # packages that need to be (re)build
    for PACKAGE_NAME in "${PACKAGE_LIST[@]}"
    do
        # XXX clone in a tmp location
        git clone -b ${PACKAGE_BRANCH} https://git.tuxed.net/rpm/${PACKAGE_NAME}
        cp ${PACKAGE_NAME}/SOURCES/* ${HOME}/rpmbuild/SOURCES
        cd ${PACKAGE_NAME}/SPECS
        spectool -g -R ${PACKAGE_NAME}.spec
        SRPM_FILE=$(rpmbuild -bs "${PACKAGE_NAME}".spec | grep Wrote | cut -d ':' -f 2 | xargs)
        PACKAGE_NAME=$(basename "${SRPM_FILE}" .src.rpm)
        if [ ! -f "${REPO_ROOT}/results/${TARGET_NAME}/${PACKAGE_NAME}/success" ]
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

    mock --chain -r "${TARGET_NAME}" --localrepo="${REPO_ROOT}" --arch "${ARCH}" ${SRPM_LIST}
done
