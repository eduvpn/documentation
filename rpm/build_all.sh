#!/bin/sh

# clean all old builds
rpmdev-wipetree

# build all projects
sh build.sh vpn-cert-service fkooman vpn-cert-service 0.2.0
sh build.sh vpn-user-portal  fkooman vpn-user-portal  0.3.0
sh build.sh vpn-crl-fetcher  fkooman vpn-crl-fetcher  0.1.1
