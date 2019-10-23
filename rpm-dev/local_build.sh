#!/bin/sh

# setup the build directory
rpmdev-setuptree

# download the source(s)
spectool -g -R ${1}.spec

# copy additional sources
cp *.pub ${1}.sysconfig ${1}.service ${1}*.conf ${1}*.cron ${1}*.patch ${HOME}/rpmbuild/SOURCES

# build the RPM
rpmbuild -bb ${1}.spec
