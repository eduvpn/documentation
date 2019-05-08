#!/bin/sh

LC_BRANCH=master
BASE_DIR=${HOME}/Projects/LC-${LC_BRANCH}

mkdir -p "${BASE_DIR}"
cd "${BASE_DIR}" || exit

# clone repositories (read-only)
git clone -b ${LC_BRANCH} https://github.com/eduvpn/vpn-user-portal.git
git clone -b ${LC_BRANCH} https://github.com/eduvpn/vpn-server-node.git
git clone -b ${LC_BRANCH} https://github.com/eduvpn/documentation.git

# clone all repositories (read/write, your own "fork")
#GITHUB_USER=fkooman
#git clone -b ${LC_BRANCH} git@github.com:${GITHUB_USER}/vpn-user-portal.git
#git clone -b ${LC_BRANCH} git@github.com:${GITHUB_USER}/vpn-server-node.git

# vpn-user-portal
cd "${BASE_DIR}/vpn-user-portal" || exit
mkdir -p data
composer update

cat << 'EOF' > config/config.php
<?php
$baseConfig = include __DIR__.'/config.php.example';
$localConfig = [
    'secureCookie' => false,
];
return array_merge($baseConfig, $localConfig);
EOF

php libexec/init.php
php bin/add-user.php foo   bar
php bin/add-user.php admin secret
NODE_API_SECRET=$(cat config/node-api.key)

# vpn-server-node
cd "${BASE_DIR}/vpn-server-node" || exit
mkdir -p data openvpn-config
composer update
cp config/firewall.php.example config/firewall.php
cat << EOF > config/config.php
<?php
\$baseConfig = include __DIR__.'/config.php.example';
\$localConfig = [
    'apiUri' => 'http://localhost:8082/node-api.php',
    'apiPass' => '${NODE_API_SECRET}',
];
return array_merge(\$baseConfig, \$localConfig);
EOF

# launch script
cat << 'EOF' | tee "${BASE_DIR}/launch.sh" > /dev/null
#!/bin/sh
(
    cd vpn-user-portal || exit
    php -S localhost:8082 -t web &
)
EOF
chmod +x "${BASE_DIR}/launch.sh"
