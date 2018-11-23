#!/bin/sh

OS_VERSION=28
MOCK_CONFIG=fedora-${OS_VERSION}-x86_64
REPO_ROOT=${HOME}/repo/${MOCK_CONFIG}
RPM_DIR=${REPO_ROOT}/release/fedora/${OS_VERSION}/x86_64
SRPM_DIR=${REPO_ROOT}/release/fedora/${OS_VERSION}/Source

export REPO_ROOT RPM_DIR SRPM_DIR MOCK_CONFIG

(
    sh release/build_packages.sh
)
