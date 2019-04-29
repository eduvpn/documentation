# Upgrade from 1.0 to 2.0

This document describes how to "upgrade" your 1.0 server to 2.0. I wrote 
"upgrade" as there is no way to automatically upgrade your server to 2.0. The 
reason for this is the extensive changes during the lifetime of 1.0. Therefore, 
there are many different "deployments" out there in various stages. As we 
needed to break compatibility for client configurations anyway as we removed 
some legacy OpenVPN configuration options and changed the OAuth token format we 
didn't bother handling the upgrade scenario. This also means that all current 
users will need to download a new configuration and configure their device. If 
they are using the Let's Connect! or eduVPN apps this will be handled 
automatically: only a new authentication/authorization will be triggered.

The way we approach an "upgrade" consists of these steps:

1. Create a backup of relevant configuration files;
2. Reset your VPN server _or_ remove the 1.0 software, configuration and data;
3. Run the `deploy_${DIST}.sh` 2.0 script;
4. (Optionally) manually merge the old configuration with the new 
   configuration.

## Backup

A few files are interesting to keep as they may help you configure your 2.0 
server if you don't remember all the details of the changes you made during the 
1.0 installation.

- `/etc/vpn-user-portal/default/config.php`
- `/etc/vpn-admin-portal/default/config.php`
- `/etc/vpn-server-api/default/config.php`
- `/etc/vpn-server-node/firewall.php`
- `/var/lib/vpn-user-portal/default/OAuth.key` (only for servers that have 
  "Guest Access" enabled)
- `/etc/httpd/conf.d/${HOSTNAME}.conf` (where `${HOSTNAME}` is the name of your 
  VPN server)

You SHOULD also make sure you have a copy of your TLS certificate/key if you 
used something else than Let's Encrypt as the new deploy script MAY overwrite 
your TLS certificate! However, this depends on how/where you installed the 
certificate.

## Remove

After backing up the files mentioned above, the best approach is to "reset" 
your machine, i.e. perform a new installation of the operating system, 
typically this is very easy when using a VM platform.

If this is not possible or inconvenient, you can use the 
`remove_1.0_${DIST}.sh` script to remove all software, configuration and data 
belonging to your 1.0 installation.

### SELinux

If you are using CentOS / Fedora, you need to deal with SELinux and remove 
some of its configuration. Because the `deploy_centos.sh` and 
`deploy_fedora.sh` scripts changed during the lifetime of the 1.0 release we 
can't be sure which SELinux configuration is active on your server.

In order to continue, run the following command and verify the output:

    $ sudo semanage port -l | grep openvpn_port_t
    openvpn_port_t                 tcp      1195-1263, 11940-12195, 1194
    openvpn_port_t                 udp      1195-1263, 1194

Now you can remove the UDP and TCP ports, except `1194`, for the example 
output above it would look like this, but on your system it MAY be different:

    $ sudo semanage port -d -t openvpn_port_t -p tcp 1195-1263
    $ sudo semanage port -d -t openvpn_port_t -p tcp 11940-12195
    $ sudo semanage port -d -t openvpn_port_t -p udp 1195-1263

When you are done it should look like this:

    $ sudo semanage port -l | grep openvpn_port_t
    openvpn_port_t                 tcp      1194
    openvpn_port_t                 udp      1194

## Deploy

Follow the new server deployment 
[instructions](https://github.com/eduvpn/documentation/blob/master/README.md#deployment).

## Restore

Now that you have a new deployment, you can start by (re)configuring your 
server again. 

Follow the (new) documentation as found here, and use that as a basis for 
(re)configuring your server. Do NOT copy your old configuration files over the
new configuration files, but only use them to look at the details of what you
configured before. Most configuration options will be similar to what they 
were before. The biggest changes were made to the way users are authenticated. 
It is best to follow the documentation on how to (re)configure the user 
authentication and what options are available now / need to be configured.

As there is no longer a `vpn-admin-portal` in 2.0, there is no need to restore
anything there. The "Admin" functionality is now part of the `vpn-user-portal` 
component.

Also, the configuration and data is no longer stored in a `default` folder, but 
directly under the component directory. 

For example, in 1.0 the configuration for `vpn-user-portal` was located in the
file `/etc/vpn-user-portal/default/config.php`, but in 2.0 this is now 
`/etc/vpn-user-portal/config.php`.

The OAuth key, if you need to keep using the old one needs to be modified:

    $ cat OAuth.key | tr '+/' '-_' | tr -d '=' > OAuth.new.key

The location also changed. Copy the `OAuth.new.key` to 
`/etc/vpn-user-portal/oauth.key`.

If you update your configuration files, you can also take a look at the 
"templates" that contain the default configuration. Some of the scripts that 
run during the deployment stage modify those files and remove all the comments
in the process, which is unfortunate. The templates can be found here:

- https://github.com/eduvpn/vpn-user-portal/blob/v2/config/config.php.example
- https://github.com/eduvpn/vpn-server-api/blob/v2/config/config.php.example
- https://github.com/eduvpn/vpn-server-node/blob/v2/config/config.php.example
- https://github.com/eduvpn/vpn-server-node/blob/v2/config/firewall.php.example
