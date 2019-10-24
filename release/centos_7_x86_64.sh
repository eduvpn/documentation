#!/bin/sh

ARCH=x86_64
OS_VERSION=7
MOCK_CONFIG=epel-${OS_VERSION}-${ARCH}

export MOCK_CONFIG ARCH
(
    sh release/build_packages.sh
)
