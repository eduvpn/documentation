#!/bin/sh

LC_BRANCH=master
BASE_DIR=${HOME}/Projects/LC-${LC_BRANCH}
GITHUB_USER=eduvpn

mkdir -p "${BASE_DIR}"
cd "${BASE_DIR}" || exit

# clone repositories (read-only)
git clone -b ${LC_BRANCH} https://github.com/${GITHUB_USER}/vpn-user-portal.git
git clone -b ${LC_BRANCH} https://github.com/${GITHUB_USER}/vpn-server-node.git
git clone -b ${LC_BRANCH} https://github.com/${GITHUB_USER}/documentation.git

# clone all repositories (read/write, your own "fork")
#git clone -b ${LC_BRANCH} git@github.com:${GITHUB_USER}/vpn-user-portal.git
#git clone -b ${LC_BRANCH} git@github.com:${GITHUB_USER}/vpn-server-node.git
#git clone -b ${LC_BRANCH} git@github.com:${GITHUB_USER}/documentation.git

# vpn-user-portal
cd "${BASE_DIR}/vpn-user-portal" || exit
composer update
mkdir -p openvpn-config
mkdir -p data

cat << 'EOF' > config/config.php
<?php
$baseConfig = include __DIR__.'/config.php.example';
$localConfig = [
    'secureCookie' => false,
    'adminUserIdList' => ['admin'],
    'ProfileList' => [
        'default' => [
            'profileNumber' => 1,
            'displayName' => 'Default Profile',
            'rangeFour' => '10.42.42.0/25',
            'rangeSix' => 'fd42:4242:4242:4242::/64',
            'hostName' => 'localhost',
        ],
    ],
];
return array_merge($baseConfig, $localConfig);
EOF

php libexec/init.php
php bin/add-user.php foo   bar
php bin/add-user.php admin secret
NODE_API_SECRET=$(cat config/node-api.key)

# vpn-server-node
cd "${BASE_DIR}/vpn-server-node" || exit
mkdir -p openvpn-config
composer update
cp "${BASE_DIR}/vpn-user-portal/config/node-api.key" config/node-api.key
cat << 'EOF' > config/config.php
<?php
$baseConfig = include __DIR__.'/config.php.example';
$localConfig = [
    'apiUrl' => 'http://localhost:8082/node-api.php',
];
return array_merge($baseConfig, $localConfig);
EOF

# launch script
cat << 'EOF' | tee "${BASE_DIR}/launch.sh" > /dev/null
#!/bin/sh
(
    cd vpn-user-portal || exit
    php -S localhost:8082 -t web &
    #php libexec/generate-openvpn-config.php --dev
    #sudo openvpn --config openvpn-config/default-0.conf &
    #sudo openvpn --config openvpn-config/default-1.conf &
)
EOF
chmod +x "${BASE_DIR}/launch.sh"
