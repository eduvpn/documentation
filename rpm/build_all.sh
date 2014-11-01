#!/bin/sh

# clean all old builds
rpmdev-wipetree

# build all projects
sh build.sh vpn-cert-service fkooman vpn-cert-service 0.1.12
sh build.sh vpn-user-portal  fkooman vpn-user-portal  0.1.11

#rpm --resign ${HOME}/rpmbuild/RPMS/noarch/*.rpm

# create a yum repo
createrepo ${HOME}/rpmbuild/RPMS/

# rsync to a web server
#rsync --recursive ${HOME}/rpmbuild/RPMS fkooman@ursa.uberspace.de:/var/www/virtual/fkooman/www.php-oauth.net/repo/eduVPN
