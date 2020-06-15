---
title: Deploying on Debian
description: Install and Maintain eduVPN/Let's Connect! on Debian
category: howto
---

For simple one server deployments and tests, we have a deploy script available 
you can run on a fresh Debian 9 installation. It will configure all components 
and will be ready for use after running!

Additional scripts are available after deployment:

* Use [Let's Encrypt](https://letsencrypt.org/) for automatic web server 
  certificate management;

## Requirements

* Clean Debian 9 installation with all updates installed;
* Have a **STATIC** IPv4 and IPv6 address configured on your external 
  interface;
* Network equipment/VM platform allows access to the very least `tcp/80`, 
  `tcp/443`, `udp/1194` and `tcp/1194` for basic functionality, the deploy 
  script will take care of the host firewall;
* Working DNS entry for your VPN server, e.g. `vpn.example.org`.

We test only with the official Debian 
[netinst](https://www.debian.org/distrib/netinst) and the official 
[Cloud](https://cdimage.debian.org/cdimage/openstack/) images.

If you have a more complicated setup, we recommend to manually walk through 
the deploy script and follow the steps.

**NOTE** if you expect to do a production deploy, please read the section below 
about modifying the PHP configuration.

## Base Deploy

Perform these steps on the host where you want to deploy:

    $ sudo apt-get -y install ca-certificates
    $ wget https://github.com/eduvpn/documentation/archive/v2.tar.gz
    $ tar -xzf v2.tar.gz
    $ cd documentation-2

We assume you have `sudo` installed and configured for your user first, after
this:

    $ sudo -s
    # ./deploy_debian.sh

Specify the hostname you want to use for your VPN server. The recommended 
hostname SHOULD already be the one you want to use... If not, set the hostname
correctly first.

**NOTE**: you can NOT use `localhost` as a hostname, nor an IP address!

**NOTE**: by default there is **NO** firewall for the traffic between VPN 
client and VPN server. So if you have SSH running on your server, the clients
will be able to connect to it when you don't take additional steps! Look 
[here](FIREWALL.md).

## Update

Periodically install updates! Run the following command periodically, e.g. 
every week during the maintenance window. Reboot your server as required for 
kernel / system library updates.

    $ sudo vpn-maint-update-system

If the command is not available, install the `vpn-maint-scripts` package first.

## Configuration

### VPN

See [PROFILE_CONFIG](PROFILE_CONFIG.md) on how to update the VPN server 
settings.

### Authentication 

#### Username & Password

By default there is a user `demo` and `admin` with a generated password for 
portal access. Those are printed at the end of the deploy script.

If you want to update/add users you can use the `vpn-user-portal-add-user`. 
Provide an existing account to _update_ the password:

    $ sudo vpn-user-portal-add-user
    User ID: foo
    Setting password for user "foo"
    Password: 
    Password (repeat): 

You can configure which user(s) is/are an administrator by setting the 
`adminUserIdList` option in `/etc/vpn-user-portal/config.php`, e.g.:

    'adminUserIdList' => ['admin'],

#### LDAP

It is easy to enable LDAP authentication. This is documented separately. See
[LDAP](LDAP.md).

#### RADIUS

It is easy to enable RADIUS authentication. This is documented separately. See
[RADIUS](RADIUS.md).

#### SAML

It is easy to enable SAML authentication for identity federations, this is 
documented separately. See [SAML](SAML.md).

### 2FA

It is possible to enable [2FA](2FA.md) with TOTP.

### ACLs

If you want to restrict the use of the VPN a bit more than on whether someone
has an account or not, e.g. to limit certain profiles to certain (groups of)
users, see [ACL](ACL.md).

## PHP 

Debian's `php7.0-fpm` package has some unfortunate defaults that only work for 
very light usage and in no way for deploys where you expect more than a few 
users to use the service.

Modify `/etc/php/7.0/fpm/pool.d/www.conf` and change the following settings. 
We'll use the CentOS/Fedora defaults here as well:

    pm = dynamic
    pm.max_children = 50
    pm.start_servers = 5
    pm.min_spare_servers = 5
    pm.max_spare_servers = 35
 
You can tweak those further if needed, but they'll do for some time! Restart 
the `php7.0-fpm` service to activate the changes:

    $ sudo systemctl restart php7.0-fpm

## Optional

### Web Server Certificates

By default a self-signed certificate is used for the web server. You can 
install your own certificates, and tweak 
`/etc/apache2/sites-available/vpn.example.org.conf` to point to them, or use 
Let's Encrypt using the script mentioned below.

#### Let's Encrypt

Run the script (as root) from the documentation folder:

    $ sudo -s
    # ./lets_encrypt_debian.sh

Make sure you use the exact same DNS name you used when running 
`deploy_debian.sh`! 

After completing the script, the certificate will be installed. After that, it
is advisable to set up automatic
[certificate renewal](https://certbot.eff.org/docs/using.html#renewing-certificates).


### Port Sharing

If you also want to allow clients to connect with the VPN over `tcp/443`, see 
[Port Sharing](PORT_SHARING.md).


