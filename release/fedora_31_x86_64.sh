#!/bin/sh

ARCH=x86_64
OS_VERSION=31
MOCK_CONFIG=fedora-${OS_VERSION}-${ARCH}
REPO_ROOT=${HOME}/repo-v2

export REPO_ROOT MOCK_CONFIG ARCH

(
    sh release/build_packages.sh
)
