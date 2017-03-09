#!/bin/sh

# setup the build dir
rpmdev-setuptree

# install dependencies for building
yum deplist "/rpm/SRPMS/${1}" | awk '/provider:/ {print $2}' | sort -u | xargs yum -y install

# rebuild package
rpmbuild --rebuild "/rpm/SRPMS/${1}"

# update repository
createrepo_c /rpm
