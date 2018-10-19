#!/bin/sh

REPO_ROOT=${HOME}/repo
RPM_DIR=${REPO_ROOT}/release/enterprise/7/x86_64
SRPM_DIR=${REPO_ROOT}/release/enterprise/7/Source
MOCK_CONFIG=epel-7-x86_64

(
    # create a symlink from 7Server -> 7 for some? RHEL installations
    mkdir -p ${REPO_ROOT}/release/enterprise/7
    cd ${REPO_ROOT}/release/enterprise
    ln -s 7 7Server
)

export REPO_ROOT RPM_DIR SRPM_DIR MOCK_CONFIG

(
    sh release/build_packages.sh
)
