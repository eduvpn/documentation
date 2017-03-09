#!/bin/sh

# setup the build directory
rpmdev-setuptree

# download the tar from GitHub
spectool -g -R $1.spec

# copy the additional sources
cp $1*.conf $1*.cron $1*.patch $HOME/rpmbuild/SOURCES

# create the RPM
rpmbuild -bb $1.spec
