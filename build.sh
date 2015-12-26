#!/bin/sh

OWNER=${1}
REPO=${2}
VERSION=${3}
COMMIT=${4}

git clone https://github.com/${OWNER}/${REPO}.git ${REPO}-${VERSION}
(
    cd ${REPO}-${VERSION}
    git checkout ${COMMIT}
    rm -rf .git
    composer install --no-dev
)
tar -cJf ${REPO}-${VERSION}.tar.xz ${REPO}-${VERSION}
