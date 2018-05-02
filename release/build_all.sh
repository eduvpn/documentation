#!/bin/sh

#
# Mock https://fedoraproject.org/wiki/Using_Mock_to_test_package_builds
#
# user MUST be part of mock group:
#   $ sudo usermod -a -G mock myusername 
#

REPO_ROOT=${HOME}/repo
mkdir -p "${REPO_ROOT}"

rpmdev-wipetree || exit
rpmdev-setuptree || exit

# CentOS / Red Hat Enterprise Linux
(
    export RPM_DIR=${REPO_ROOT}/release/enterprise/7/x86_64
    export SRPM_DIR=${REPO_ROOT}/release/enterprise/7/Source
    export MOCK_CONFIG=epel-7-x86_64
    export MOCK_FLAGS="-m --yum"
    sh release/build_packages.sh
)

# Fedora 28
(
    export RPM_DIR=${REPO_ROOT}/release/fedora/28/x86_64
    export SRPM_DIR=${REPO_ROOT}/release/fedora/28/Source
    export MOCK_CONFIG=fedora-28-x86_64
    export MOCK_FLAGS=
    sh release/build_packages.sh
)

# Fedora 29
#(
#    export RPM_DIR=${REPO_ROOT}/release/fedora/29/x86_64
#    export SRPM_DIR=${REPO_ROOT}/release/fedora/29/Source
#    export MOCK_CONFIG=fedora-29-x86_64
#    export MOCK_FLAGS=
#    sh release/build_packages.sh
#)

# Create Archive
DATETIME=$(date +%Y%m%d%H%M%S)
(
    cd "${REPO_ROOT}" || exit
    tar -cJf "../rpmRepo-${DATETIME}.tar.xz" .
)
# Done
