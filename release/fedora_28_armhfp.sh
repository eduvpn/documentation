#!/bin/sh

REPO_ROOT=${HOME}/repo
RPM_DIR=${REPO_ROOT}/release/fedora/28/armhfp
SRPM_DIR=${REPO_ROOT}/release/fedora/28/Source
MOCK_CONFIG=fedora-28-armhfp
MOCK_FORCE_ARCH=armv7hl

export REPO_ROOT RPM_DIR SRPM_DIR MOCK_CONFIG MOCK_FORCE_ARCH

(
    sh release/build_packages.sh
)
