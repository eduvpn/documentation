#!/bin/sh

cat > /etc/yum.repos.d/eduvpn.repo << EOF
[eduvpn]
name=eduVPN packages
baseurl=file:///out
skip_if_unavailable=True
gpgcheck=0
repo_gpgcheck=0
enabled=1
EOF

# setup RPM build directory
echo '%_topdir /out' | tee /root/.rpmmacros >/dev/null
rpmdev-setuptree

# install dependencies for building
yum deplist "/in/${1}" | awk '/provider:/ {print $2}' | sort -u | xargs yum -y install

# rebuild package
rpmbuild --rebuild "/in/${1}"

# create package index
createrepo_c /out
