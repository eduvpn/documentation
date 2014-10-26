source ./versions.sh

# config
PACKAGE_NAME=php-fkooman-rest-plugin-mellon
GITHUB_USER=fkooman
GITHUB_NAME=php-lib-rest-plugin-mellon
VERSION=${PHP_FKOOMAN_REST_PLUGIN_MELLON_VERSION}

# download tarball
curl -s -L -o $HOME/rpmbuild/SOURCES/${VERSION}.tar.gz https://github.com/${GITHUB_USER}/${GITHUB_NAME}/archive/${VERSION}.tar.gz

# copy spec and sources to right location
(
    cd ${HOME}/rpmbuild/SOURCES/
    tar -xzf ${VERSION}.tar.gz
    cp ${GITHUB_NAME}-${VERSION}/rpm/* .
    mv ${PACKAGE_NAME}.spec ${HOME}/rpmbuild/SPECS/
    rm -rf ${GITHUB_NAME}-${VERSION}
)

# build package
(
    cd $HOME/rpmbuild/SPECS/
    rpmbuild -ba ${PACKAGE_NAME}.spec
)
