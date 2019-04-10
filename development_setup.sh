#!/bin/sh

BASE_DIR=${HOME}/Projects/LC

mkdir -p "${BASE_DIR}"
cd "${BASE_DIR}" || exit

# clone all repositories
git clone https://github.com/eduvpn/vpn-server-api.git
git clone https://github.com/eduvpn/vpn-user-portal.git
git clone https://github.com/eduvpn/vpn-server-node.git
git clone https://github.com/eduvpn/vpn-lib-common.git

# vpn-server-api
cd "${BASE_DIR}/vpn-server-api" || exit
mkdir -p data
composer update
cat << 'EOF' > config/config.php
<?php
$baseConfig = include __DIR__.'/config.php.example';
$localConfig = [
];
return array_merge($baseConfig, $localConfig);
EOF
php bin/init.php

# vpn-user-portal
cd "${BASE_DIR}/vpn-user-portal" || exit
mkdir -p data
composer update

cat << 'EOF' > config/config.php
<?php
$baseConfig = include __DIR__.'/config.php.example';
$localConfig = [
    'secureCookie' => false,
    'apiUri' => 'http://localhost:8008/api.php',
];
return array_merge($baseConfig, $localConfig);
EOF

php bin/init.php
php bin/generate-oauth-key.php
php bin/add-user.php --user foo   --pass bar
php bin/add-user.php --user admin --pass secret

# vpn-server-node
cd "${BASE_DIR}/vpn-server-node" || exit
mkdir -p data openvpn-config
composer update
cp config/firewall.php.example config/firewall.php
cat << 'EOF' > config/config.php
<?php
$baseConfig = include __DIR__.'/config.php.example';
$localConfig = [
    'apiUri' => 'http://localhost:8008/api.php',
];
return array_merge($baseConfig, $localConfig);
EOF

# launch script
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
