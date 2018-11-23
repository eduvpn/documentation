#!/bin/sh

OS_VERSION=28
MOCK_CONFIG=fedora-${OS_VERSION}-armhfp
REPO_ROOT=${HOME}/repo/${MOCK_CONFIG}
RPM_DIR=${REPO_ROOT}/release/fedora/${OS_VERSION}/armhfp
SRPM_DIR=${REPO_ROOT}/release/fedora/${OS_VERSION}/Source
MOCK_FORCE_ARCH=armv7hl

export REPO_ROOT RPM_DIR SRPM_DIR MOCK_CONFIG MOCK_FORCE_ARCH

(
    sh release/build_packages.sh
)
