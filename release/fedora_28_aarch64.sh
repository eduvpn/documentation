#!/bin/sh

OS_VERSION=28
MOCK_CONFIG=fedora-${OS_VERSION}-aarch64
REPO_ROOT=${HOME}/repo/${MOCK_CONFIG}
RPM_DIR=${REPO_ROOT}/release/fedora/${OS_VERSION}/aarch64
SRPM_DIR=${REPO_ROOT}/release/fedora/${OS_VERSION}/Source
MOCK_FORCE_ARCH=aarch64

export REPO_ROOT RPM_DIR SRPM_DIR MOCK_CONFIG MOCK_FORCE_ARCH

(
    sh release/build_packages.sh
)
