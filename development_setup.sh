#!/bin/sh

REPO_BRANCH=v3
BASE_DIR=${HOME}/Projects/eduVPN-${REPO_BRANCH}
GIT_HOST=https://git.sr.ht/
#GIT_HOST=git@git.sr.ht:

mkdir -p "${BASE_DIR}"
cd "${BASE_DIR}" || exit

# clone repositories (read-only)
git clone -b "${REPO_BRANCH}" ${GIT_HOST}~fkooman/vpn-user-portal
git clone -b "${REPO_BRANCH}" ${GIT_HOST}~fkooman/vpn-server-node
git clone -b "${REPO_BRANCH}" ${GIT_HOST}~fkooman/vpn-documentation
git clone -b "${REPO_BRANCH}" ${GIT_HOST}~fkooman/vpn-portal-artwork-eduVPN
git clone -b "${REPO_BRANCH}" ${GIT_HOST}~fkooman/vpn-portal-artwork-LC
git clone ${GIT_HOST}~fkooman/vpn-ca
git clone ${GIT_HOST}~fkooman/vpn-daemon
git clone ${GIT_HOST}~fkooman/vpn-maint-scripts
git clone ${GIT_HOST}~fkooman/builder.rpm
git clone ${GIT_HOST}~fkooman/nbuilder.deb

# clone all RPM/DEB packages
mkdir -p rpm deb
for PACKAGE_NAME in vpn-daemon php-oauth2-server php-secookie vpn-ca vpn-portal-artwork-LC vpn-portal-artwork-eduVPN vpn-server-node vpn-user-portal vpn-maint-scripts; do
	git clone ${GIT_HOST}~fkooman/"${PACKAGE_NAME}".rpm rpm/"${PACKAGE_NAME}".rpm
	git clone ${GIT_HOST}~fkooman/"${PACKAGE_NAME}".deb deb/"${PACKAGE_NAME}".deb
done

######################################
# vpn-ca                             #
######################################
cd "${BASE_DIR}/vpn-ca" || exit
go build -o vpn-ca tuxed.net/vpn-ca/cmd/vpn-ca/...

######################################
# vpn-user-portal                    #
######################################
cd "${BASE_DIR}/vpn-user-portal" || exit
mkdir -p data
composer update

cat << EOF > config/config.php
<?php
\$baseConfig = include __DIR__.'/config.php.example';
\$localConfig = [
    //'styleName' => 'eduVPN',
    //'styleName' => 'LC',
    'adminUserIdList' => ['admin'],
    'vpnCaPath' => '${BASE_DIR}/vpn-ca/vpn-ca',
];
return array_merge(\$baseConfig, \$localConfig);
EOF

php libexec/generate-secrets.php
php bin/account.php --add admin --password secret
php bin/account.php --add foo --password bar

# symlink to the official templates we have so we can easily modify and test
# them
mkdir -p web/css web/img web/fonts
for TPL in eduVPN LC
do
    ln -s "${BASE_DIR}/vpn-portal-artwork-${TPL}/views"  "views/${TPL}"
    ln -s "${BASE_DIR}/vpn-portal-artwork-${TPL}/locale" "locale/${TPL}"
    ln -s "${BASE_DIR}/vpn-portal-artwork-${TPL}/css"    "web/css/${TPL}"
    ln -s "${BASE_DIR}/vpn-portal-artwork-${TPL}/img"    "web/img/${TPL}"
    ln -s "${BASE_DIR}/vpn-portal-artwork-${TPL}/fonts"  "web/fonts/${TPL}"
done

######################################
# vpn-daemon                         #
######################################
cd "${BASE_DIR}/vpn-daemon" || exit
echo "[Go] building vpn-daemon... (may take a while...)"
go build -o vpn-daemon tuxed.net/vpn-daemon/cmd/vpn-daemon/...

######################################
# vpn-server-node                    #
######################################
cd "${BASE_DIR}/vpn-server-node" || exit
mkdir -p openvpn-config wg-config
composer update
cat << 'EOF' > config/config.php
<?php
$baseConfig = include __DIR__.'/config.php.example';
$localConfig = [
    'apiUrl' => 'http://localhost:8082/node-api.php',
];
return array_merge($baseConfig, $localConfig);
EOF

php libexec/generate-secrets.php
cp "${BASE_DIR}/vpn-user-portal/config/keys/node.0.key" "${BASE_DIR}/vpn-server-node/config/keys/node.key"

######################################
# launch script                      #
######################################
cat << 'EOF' | tee "${BASE_DIR}/launch.sh" > /dev/null
#!/bin/sh
vpn-daemon/vpn-daemon &
cd vpn-user-portal || exit
php -S localhost:8082 -t web dev/router.php
EOF
chmod +x "${BASE_DIR}/launch.sh"
