#!/bin/sh

# clean all old builds
rpmdev-wipetree

# build all projects
sh php-fkooman-ini.sh
sh php-fkooman-json.sh
sh php-fkooman-rest.sh
sh php-fkooman-rest-plugin-basic.sh
sh php-fkooman-rest-plugin-mellon.sh
sh vpn-cert-service.sh
sh vpn-user-portal.sh

# create a yum repo
createrepo ${HOME}/rpmbuild/RPMS/

# rsync to a web server
#rsync --delete --recursive ${HOME}/rpmbuild/RPMS fkooman@eduvpn.surfcloud.nl:/var/www/html/eduvpn
