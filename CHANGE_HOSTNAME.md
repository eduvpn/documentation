# Change Hostname

In case you want to change the hostname of your VPN server, you need to follow
these steps:

1. Set the correct hostname;
2. Make sure DNS is correct;
3. Obtain new TLS certificates and install them;
4. Change the Apache `VirtualHost` configuration;
5. Update `/etc/vpn-user-portal/config.php` to make sure `hostName` (in all 
   profiles) points to the correct name.

We assume you want to rename from `vpn.example.org` to `vpn.example.com`. 
Please adapt the hostname as appropriate.

This instruction is for a _single_ server deployment.

## Hostname

```bash
$ sudo hostnamectl set-hostname vpn.example.com
```

## DNS

Make sure the new hostname has an A (and AAAA) record to your VPN server IPs.

## TLS

When your DNS is correct you can use Let's Encrypt to obtain new certificates,
or manually obtain them from your CA and install them.

## Apache

### Fedora / EL

Rename `/etc/httpd/conf.d/vpn.example.org.conf` to 
`/etc/httpd/conf.d/vpn.example.com.conf`. Replace all occurrences of 
`vpn.example.org` with `vpn.example.com` in this file.

### Debian / Ubuntu

Disable the old site:

```bash
$ sudo a2dissite vpn.example.org
$ sudo mv /etc/apache2/sites-available/vpn.example.org.conf /etc/apache2/sites-available/vpn.example.com.conf
$ sudo a2ensite vpn.example.com
```

Modify `/etc/apache2/sites-available/vpn.example.com.conf` and replace all 
occurrences of `vpn.example.org` with `vpn.example.com`.

## Server Configuration

Modify `/etc/vpn-user-portal/config.php` and look at all `hostName` entries and
change them to the new hostname.

## Apply

Run:

```bash
$ sudo vpn-maint-apply-changes
```

Reboot your system to make sure everything comes back correctly. All should be
done now!
