#!/bin/sh

REPO_ROOT=${HOME}/repo-v2

# Create Archive
DATETIME=$(date +%Y%m%d%H%M%S)
(
    cd "${REPO_ROOT}" || exit 1
    tar -cJf "${HOME}/rpmRepo-v2-${DATETIME}.tar.xz" .
)
