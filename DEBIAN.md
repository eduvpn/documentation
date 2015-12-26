# Introduction

Rough documentation on how to get eduVPN working on Debian 8. We assume your
server has the name `vpn.example` throughout the document.

# Dependencies

    $ sudo apt-get install apache2 php5 openvpn curl php5-sqlite

# Download

You can download a release:

- [0.9.0](https://storage.tuxed.net/fkooman/public/upload/eduvpn/eduvpn-0.9.0.tar.xz) ([SIG](https://storage.tuxed.net/fkooman/public/upload/eduvpn/eduvpn-0.9.0.tar.xz.asc))

This archive contains all components of eduVPN. Each component will have their
own version, you have to use the version of the component below when you 
read `VERSION`.

    $ mkdir $HOME/Downloads
    $ cd $HOME/Downloads
    $ curl -O https://storage.tuxed.net/fkooman/public/upload/eduvpn/eduvpn-VERSION.tar.xz
    $ tar -xJf eduvpn-0.9.0.tar.xz

# Installation

Now unpack them all in `/var/www` and create symlinks:

    $ cd /var/www
    $ sudo tar -xJf $HOME/Downloads/vpn-config-api-VERSION.tar.xz
    $ sudo tar -xJf $HOME/Downloads/vpn-user-portal-VERSION.tar.xz
    $ sudo tar -xJf $HOME/Downloads/vpn-server-api-VERSION.tar.xz
    $ sudo tar -xJf $HOME/Downloads/vpn-admin-portal-VERSION.tar.xz
    $ sudo ln -s vpn-config-api-VERSION vpn-config-api
    $ sudo ln -s vpn-user-portal-VERSION vpn-user-portal
    $ sudo ln -s vpn-server-api-VERSION vpn-server-api
    $ sudo ln -s vpn-admin-portal-VERSION vpn-admin-portal

# Configuration

**WARNING**: the 0.9.0 release still uses INI files and not YAML files, these 
instructions are for a release that is coming soon!

## VPN Config API

    $ cd /var/www/vpn-config-api
    $ sudo cp config/config.yaml.example config/config.yaml

Edit `config/config.yaml` and set at least the following:

    sourcePath: /usr/share/easy-rsa
    targetPath: /var/www/vpn-config-api/data/easy-rsa

Now you should be able to initialize the CA:

    $ sudo mkdir data
    $ sudo chown www-data.www-data data
    $ sudo -u www-data php bin/init

Generate a server configuration:

    $ sudo -u www-data php bin/server-config vpn.example | sudo tee /etc/openvpn/server.conf >/dev/null

Install the Apache configuration in `/etc/apache2/conf-available/vpn-config-api.conf`:

    Alias /vpn-config-api /var/www/vpn-config-api/web

    <Directory /var/www/vpn-config-api/web>
        AllowOverride None
        Require local
        SetEnvIfNoCase ^Authorization$ "(.+)" HTTP_AUTHORIZATION=$1
    </Directory>

Enable the configuration and reload Apache:

    $ sudo a2enconf vpn-config-api
    $ sudo service apache2 reload

## VPN User Portal

    $ cd /var/www/vpn-user-portal
    $ sudo cp config/config.yaml.example config/config.yaml

Edit `config/config.yaml` and set at least the following:

    dsn: 'sqlite:/var/www/vpn-user-portal/data/configurations.sqlite'

Initialize the database:
    
    $ sudo mkdir data
    $ sudo chown www-data.www-data data
    $ sudo -u www-data php bin/init

Install the Apache configuration in `/etc/apache2/conf-available/vpn-user-portal.conf`:

    Alias /vpn-user-portal /var/www/vpn-user-portal/web

    <Directory /var/www/vpn-user-portal/web>
        AllowOverride none
      
        #Require local 
        Require all granted

        RewriteEngine on
        RewriteBase /vpn-user-portal
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteRule ^(.*)$ index.php/$1 [L,QSA]

        # For MellonAuthentication
        # Use the following to test vpn-user-portal without needing to configure
        # mod_mellon.
        #RequestHeader set MELLON-NAME-ID foo

        # For BasicAuthentication
        SetEnvIfNoCase ^Authorization$ "(.+)" HTTP_AUTHORIZATION=$1
    </Directory>

Enable the configuration, enable `rewrite` module and restart Apache:

    $ sudo a2enconf vpn-user-portal
    $ sudo a2enmod rewrite
    $ sudo service apache2 restart
    
## VPN Server API

    $ cd /var/www/vpn-server-api
    $ sudo cp config/config.yaml.example config/config.yaml

Edit `config/config.yaml` and set at least the following:

    Crl:
        path: '/var/www/vpn-server-api/data'
    Ccd:
        path: '/var/www/vpn-server-api/data/ccd'

If you want to enable more OpenVPN servers also add additional ones, together
with their management port in the configuration file. By default only one 
server is enabled.

Create some directories and set permissions to allow writing the CA and files
in the Client Config Directory (CCD):

    $ sudo mkdir -p data/ccd
    $ sudo chown -R www-data.www-data data

Install the Apache configuration in `/etc/apache2/conf-available/vpn-server-api.conf`:

    Alias /vpn-server-api /var/www/vpn-server-api/web

    <Directory /var/www/vpn-server-api/web>
        AllowOverride None
        Require local
        SetEnvIfNoCase ^Authorization$ "(.+)" HTTP_AUTHORIZATION=$1
    </Directory>

Enable the configuration and reload Apache:

    $ sudo a2enconf vpn-server-api
    $ sudo service apache2 reload

## VPN Admin Portal

    $ cd /var/www/vpn-server-api
    $ sudo cp config/config.yaml.example config/config.yaml

You do not need to modify anything in the default configuration if you followed
the instructions above.

Install the Apache configuration in `/etc/apache2/conf-available/vpn-admin-portal.conf`:

    Alias /vpn-admin-portal /var/www/vpn-admin-portal/web

    <Directory /var/www/vpn-admin-portal/web>
        AllowOverride none
      
        #Require local 
        Require all granted

        RewriteEngine on
        RewriteBase /vpn-admin-portal
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteRule ^(.*)$ index.php/$1 [L,QSA]

        # For MellonAuthentication
        # Use the following to test vpn-admin-portal without needing to configure
        # mod_mellon.
        #RequestHeader set MELLON-NAME-ID foo

        # For BasicAuthentication
        SetEnvIfNoCase ^Authorization$ "(.+)" HTTP_AUTHORIZATION=$1
    </Directory>

Enable the configuration and reload Apache:

    $ sudo a2enconf vpn-admin-portal
    $ sudo service apache2 reload

# OpenVPN Configuration

With the instructions above you now have one OpenVPN instance configured, in
`/etc/openvpn/server.conf`. You need to make some modifications. After making
these modifications you can enable OpenVPN on boot and start it:

    $ systemctl enable openvpn@server
    $ systemctl start openvpn@server

## User

You need to change the user and group that OpenVPN will use when dropping 
privileges:

    user nobody
    group nogroup

## Client Configuration Directory

The VPN Server API has the ability to write custom client configurations, they
need to be picked up by OpenVPN:

    client-config-dir /var/www/vpn-server-api/data/ccd
    
## Enable the CRL

The CRL also needs to be enabled for when configurations are revoked by the 
users or adminstrators. 

    crl-verify /var/www/vpn-server-api/data/ca.crl

For this to work there actually needs to be a revoked certificate. You can 
create and revoke one in the VPN User Portal first and then enable the CRL in
the configuration file.

## A TCP server

Once you have the initial server running it is easy to create an additional 
TCP server. 

    $ sudo cp /etc/openvpn/server.conf /etc/openvpn/server-tcp.conf

You need to modify this configuration file to change (at least) the following
lines.

Disable these:

    proto udp
    port 1194

Enable these:

    #proto tcp-server
    #port 443

Change these:

    server 10.42.42.0 255.255.255.0
    server-ipv6 fd00:4242:4242::/64
    management localhost 7505

Choose a new IP range, and change the management port as well, typically to
`7506` for the next instance and so on.

Now you can also enable and start this server:

    $ sudo systemctl enable openvpn@server-tcp
    $ sudo systemctl start openvpn@server-tcp

# User Interfaces

You can visit the VPN User Portal here:

    http://vpn.example/vpn-user-portal/

And the VPN Admin Portal here:

    http://vpn.example/vpn-admin-portal/

The user for both environments is `foo` and the password is `bar`.

To add more users and or modify/delete the `foo` user, edit 
`/var/www/vpn-user-portal/config/config.yaml` and 
`/var/www/vpn-admin-portal/config/config.yaml` and follow the current format.

To generate password hashes use the command line, e.g.:

    $ php -r "echo password_hash('s3cr3t', PASSWORD_DEFAULT) . PHP_EOL;"
    $2y$10$G6YI9r1CtieyStqt75/fQudVF1xSytpip8imG1VUJdDTh6A6ZJEqu

Here a hash is generated for the password `s3cr3t`.
