#!/bin/sh

# install dependencies for building
yum-builddep -y "/rpm/SRPMS/${1}"

# rebuild package
rpmbuild --rebuild "/rpm/SRPMS/${1}"

# update repository
createrepo_c /rpm
