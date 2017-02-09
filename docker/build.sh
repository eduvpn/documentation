#!/bin/sh
echo '%_topdir /out' | tee $HOME/.rpmmacros >/dev/null
rpmdev-setuptree

# install dependencies for building
yum deplist /in/${1} | awk '/provider:/ {print $2}' | sort -u | xargs yum -y install

# rebuild package
rpmbuild --rebuild /in/${1}
