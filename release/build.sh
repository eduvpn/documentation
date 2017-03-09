#!/bin/sh

cat > /etc/yum.repos.d/eduVPN.repo << EOF
[eduVPN]
name=eduVPN
baseurl=file:///rpm
skip_if_unavailable=True
gpgcheck=0
repo_gpgcheck=0
enabled=1
EOF

cat > /root/.rpmmacros << EOF
%_topdir /rpm
EOF

# install dependencies for building
yum-builddep -y "/rpm/SRPMS/${1}"

# rebuild package
rpmbuild --rebuild "/rpm/SRPMS/${1}"

# update repository
createrepo_c /rpm
