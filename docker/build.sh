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

# setup RPM build directory
echo '%_topdir /rpm' | tee /root/.rpmmacros >/dev/null
rpmdev-setuptree

# install dependencies for building
yum deplist "/rpm/SRPMS/${1}" | awk '/provider:/ {print $2}' | sort -u | xargs yum -y install

# rebuild package
rpmbuild --rebuild "/rpm/SRPMS/${1}"

# create/update package index
createrepo_c /rpm
