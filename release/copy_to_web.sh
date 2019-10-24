#!/bin/sh

REPO_ROOT=${HOME}/repo-v2
WEB_ROOT=/var/www/html

mkdir -p ${WEB_ROOT}/repo
cp ${HOME}/RPM-GPG-KEY-LC ${WEB_ROOT}/repo/
cp -r ${REPO_ROOT}/results/* ${WEB_ROOT}/repo/
restorecon -R ${WEB_ROOT}/repo
