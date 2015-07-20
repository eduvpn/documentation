#!/bin/sh

# build all projects
rpmdev-wipetree
sh build.sh vpn-cert-service fkooman vpn-cert-service 1.0.0
scp $HOME/rpmbuild/SPECS/*.spec $HOME/rpmbuild/SRPMS/*.rpm fedorapeople.org:~/public_html/vpn-cert-service/

rpmdev-wipetree
sh build.sh vpn-user-portal  fkooman vpn-user-portal 1.0.0
scp $HOME/rpmbuild/SPECS/*.spec $HOME/rpmbuild/SRPMS/*.rpm fedorapeople.org:~/public_html/vpn-user-portal/

rpmdev-wipetree
sh build.sh vpn-crl-fetcher  fkooman vpn-crl-fetcher 1.0.0
scp $HOME/rpmbuild/SPECS/*.spec $HOME/rpmbuild/SRPMS/*.rpm fedorapeople.org:~/public_html/vpn-crl-fetcher/
