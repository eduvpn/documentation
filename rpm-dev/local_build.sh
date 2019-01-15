#!/bin/sh

# setup the build directory
rpmdev-setuptree

# download the archive from the web
spectool -g -R $1.spec

# copy required sources
cp $1*.conf $1*.cron $1*.patch gpgkey-* $HOME/rpmbuild/SOURCES

# build the RPM
rpmbuild -bb $1.spec
