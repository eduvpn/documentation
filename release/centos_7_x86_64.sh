#!/bin/sh

OS_VERSION=7
MOCK_CONFIG=epel-${OS_VERSION}-x86_64
REPO_ROOT=${HOME}/repo-v2/${MOCK_CONFIG}
RPM_DIR=${REPO_ROOT}/release/enterprise/${OS_VERSION}/x86_64
SRPM_DIR=${REPO_ROOT}/release/enterprise/${OS_VERSION}/Source

(
    # create a symlink from 7Server -> 7 for some? RHEL installations
    mkdir -p ${REPO_ROOT}/release/enterprise/${OS_VERSION}
    cd ${REPO_ROOT}/release/enterprise
    ln -s ${OS_VERSION} ${OS_VERSION}Server
)

export REPO_ROOT RPM_DIR SRPM_DIR MOCK_CONFIG

(
    sh release/build_packages.sh
)
