#!/bin/sh
COPR_REPO=eduvpn-testing

# setup the build directory
rpmdev-setuptree

# download the tar from GitHub
spectool -g -R $1.spec

# copy the additional sources
cp $1*.conf $1*.cron $1*.patch $HOME/rpmbuild/SOURCES

# create the SRPM
SRPM_FILE_PATH=$(rpmbuild -bs $1.spec | cut -d ':' -f 2)
SRPM_FILE=$(basename $SRPM_FILE_PATH)

# upload the SPEC/SRPM to fedorapeople.org
scp $1.spec ${SRPM_FILE_PATH} fkooman@fedorapeople.org:~/public_html/$1/

# build @ COPR
copr-cli build ${COPR_REPO} https://fkooman.fedorapeople.org/$1/${SRPM_FILE}
