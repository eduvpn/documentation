#!/bin/sh

LC_BRANCH=v2
BASE_DIR=${HOME}/Projects/LC-${LC_BRANCH}

mkdir -p "${BASE_DIR}"
cd "${BASE_DIR}" || exit

# clone repositories (read-only)
git clone -b "${LC_BRANCH}" https://github.com/eduvpn/vpn-lib-common.git
git clone -b "${LC_BRANCH}" https://github.com/eduvpn/vpn-user-portal.git
git clone -b "${LC_BRANCH}" https://github.com/eduvpn/vpn-server-api.git
git clone -b "${LC_BRANCH}" https://github.com/eduvpn/vpn-server-node.git
git clone -b "${LC_BRANCH}" https://github.com/eduvpn/documentation.git
git clone -b master       https://github.com/eduvpn/vpn-portal-artwork.git vpn-portal-artwork-eduVPN
git clone -b master       https://github.com/letsconnectvpn/vpn-portal-artwork.git vpn-portal-artwork-LC
git clone -b master       https://github.com/letsconnectvpn/vpn-ca.git
git clone -b master       https://github.com/letsconnectvpn/vpn-daemon.git

## clone all repositories (read/write, my own "forks")
#git clone -b ${LC_BRANCH} git@git.tuxed.net:LC/vpn-lib-common.git
#(cd vpn-lib-common && git remote add github git@github.com:eduvpn/vpn-lib-common.git)
#git clone -b ${LC_BRANCH} git@git.tuxed.net:LC/vpn-user-portal.git
#(cd vpn-user-portal && git remote add github git@github.com:eduvpn/vpn-user-portal.git)
#git clone -b ${LC_BRANCH} git@git.tuxed.net:LC/vpn-server-api.git
#(cd vpn-server-api && git remote add github git@github.com:eduvpn/vpn-server-api.git)
#git clone -b ${LC_BRANCH} git@git.tuxed.net:LC/vpn-server-node.git
#(cd vpn-server-node && git remote add github git@github.com:eduvpn/vpn-server-node.git)
#git clone -b ${LC_BRANCH} git@git.tuxed.net:LC/documentation.git
#(cd documentation && git remote add github git@github.com:eduvpn/documentation.git)
#git clone -b master git@git.tuxed.net:LC/vpn-portal-artwork-eduVPN.git
#(cd vpn-portal-artwork-eduVPN && git remote add github git@github.com:eduvpn/vpn-portal-artwork.git)
#git clone -b master git@git.tuxed.net:LC/vpn-portal-artwork-LC.git
#(cd vpn-portal-artwork-LC && git remote add github git@github.com:letsconnectvpn/vpn-portal-artwork.git)
#git clone -b master       git@git.tuxed.net:LC/vpn-ca.git
#(cd vpn-ca && git remote add github git@github.com:letsconnectvpn/vpn-ca.git)
#git clone -b master       git@git.tuxed.net:LC/vpn-daemon.git
#(cd vpn-daemon && git remote add github git@github.com:letsconnectvpn/vpn-daemon.git)

# clone all RPM packages
mkdir -p rpm
for PACKAGE_NAME in vpn-daemon php-LC-common php-LC-openvpn-connection-manager php-fkooman-jwt php-fkooman-oauth2-server php-fkooman-otp-verifier php-fkooman-saml-sp php-fkooman-secookie php-fkooman-sqlite-migrate php-json-signer vpn-ca vpn-portal-artwork-LC vpn-portal-artwork-eduVPN vpn-server-api vpn-server-node vpn-user-portal
do
	git clone -b master https://git.tuxed.net/rpm/"${PACKAGE_NAME}" rpm/"${PACKAGE_NAME}"
	#git clone -b master git@git.tuxed.net:rpm/${PACKAGE_NAME}.git rpm/${PACKAGE_NAME}
done

######################################
# vpn-user-portal                    #
######################################
cd "${BASE_DIR}/vpn-user-portal" || exit
mkdir -p data
composer update

cat << 'EOF' > config/config.php
<?php
$baseConfig = include __DIR__.'/config.php.example';
$localConfig = [
    //'styleName' => 'eduVPN',
    //'styleName' => 'LC',
    'secureCookie' => false,
    'apiUri' => 'http://localhost:8008/api.php',
];
return array_merge($baseConfig, $localConfig);
EOF

php bin/init.php
php bin/generate-oauth-key.php
php bin/add-user.php --user foo   --pass bar
php bin/add-user.php --user admin --pass secret

# symlink to the official templates we have so we can easily modify and test
# them
mkdir -p web/css web/img
for TPL in eduVPN LC
do
    ln -s "${BASE_DIR}/vpn-portal-artwork-${TPL}/views"  "views/${TPL}"
    ln -s "${BASE_DIR}/vpn-portal-artwork-${TPL}/locale" "locale/${TPL}"
    ln -s "${BASE_DIR}/vpn-portal-artwork-${TPL}/css"    "web/css/${TPL}"
    ln -s "${BASE_DIR}/vpn-portal-artwork-${TPL}/img"    "web/img/${TPL}"
    ln -s "${BASE_DIR}/vpn-portal-artwork-${TPL}/fonts"  "web/fonts/${TPL}"
done

######################################
# vpn-ca                             #
######################################
cd "${BASE_DIR}/vpn-ca" || exit
go build -o _bin/vpn-ca vpn-ca/*.go

######################################
# vpn-daemon                         #
######################################
cd "${BASE_DIR}/vpn-daemon" || exit
go build -o _bin/vpn-daemon vpn-daemon/*.go

######################################
# vpn-server-api                     #
######################################
cd "${BASE_DIR}/vpn-server-api" || exit
mkdir -p data
composer update

cat << EOF > config/config.php
<?php
\$baseConfig = include __DIR__.'/config.php.example';
\$localConfig = [
    'vpnCaPath' => '${BASE_DIR}/vpn-ca/_bin/vpn-ca',
];
return array_merge(\$baseConfig, \$localConfig);
EOF

php bin/init.php

######################################
# vpn-server-node                    #
######################################
cd "${BASE_DIR}/vpn-server-node" || exit
mkdir -p data openvpn-config
composer update
cat << 'EOF' > config/config.php
<?php
$baseConfig = include __DIR__.'/config.php.example';
$localConfig = [
    'apiUri' => 'http://localhost:8008/api.php',
];
return array_merge($baseConfig, $localConfig);
EOF

######################################
# launch script                      #
######################################
cat << 'EOF' | tee "${BASE_DIR}/launch.sh" > /dev/null
#!/bin/sh
(
    cd vpn-server-api || exit
    php -S localhost:8008 -t web &
)
(
    cd vpn-user-portal || exit
    php -S localhost:8082 -t web &
)
EOF
chmod +x "${BASE_DIR}/launch.sh"
