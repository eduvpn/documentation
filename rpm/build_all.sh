#!/bin/sh

# build all projects
rpmdev-wipetree
sh build.sh vpn-cert-service fkooman vpn-cert-service 0.3.0
scp $HOME/rpmbuild/SPECS/*.spec $HOME/rpmbuild/SRPMS/*.rpm fedorapeople.org:~/public_html/vpn-cert-service/

rpmdev-wipetree
sh build.sh vpn-user-portal  fkooman vpn-user-portal  0.4.2
scp $HOME/rpmbuild/SPECS/*.spec $HOME/rpmbuild/SRPMS/*.rpm fedorapeople.org:~/public_html/vpn-user-portal/

rpmdev-wipetree
sh build.sh vpn-crl-fetcher  fkooman vpn-crl-fetcher  0.1.3
scp $HOME/rpmbuild/SPECS/*.spec $HOME/rpmbuild/SRPMS/*.rpm fedorapeople.org:~/public_html/vpn-crl-fetcher/
