#!/bin/sh

ARCH=aarch64
OS_VERSION=30
MOCK_CONFIG=fedora-${OS_VERSION}-${ARCH}

export MOCK_CONFIG ARCH
(
    sh release/build_packages.sh
)
