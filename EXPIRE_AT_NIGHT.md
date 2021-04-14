# Expire At Night

**NOTE**: this document is work in progress and not everything has been 
extensively tested. There may be mistakes in it, please let us know!

In vpn-user-portal >= 2.3.10 it is possible to expire VPN sessions at night 
instead of exactly after the duration specified in `sessionExpiry`. The goal
is to prevent that the user will be disconnected from the VPN during working 
hours.

By VPN session expiry we mean the moment at which the VPN session won't work 
anymore without the user authenticating/authorizing again. The default after 
which a session expires is 90 days, but can be modified by the administrator.

The idea is to expire sessions always at 04:00 in the morning on the day before
the actual expiry as determined by `sessionExpiry`. The expiry will consider 
the timezone set in the PHP configuration of the VPN server.

## Preparation

We recommend to set/leave your server's timezone set to UTC in all 
circumstances.

```
$ timedatectl
      Local time: Mi 2021-04-14 13:02:35 UTC
  Universal time: Mi 2021-04-14 13:02:35 UTC
        RTC time: Mi 2021-04-14 13:02:35
       Time zone: UTC (UTC, +0000)
     NTP enabled: yes
NTP synchronized: yes
 RTC in local TZ: no
      DST active: n/a
```

If it is not currently set to UTC, you can use the following:

```
$ sudo timedatectl set-timezone UTC
```

It can't hurt to restart your system at this point.

## PHP Configuration

Now you can modify PHP and set the `date.timezone` parameter to your local 
timezone.

Valid timezone definitions can be found 
[here](https://www.php.net/manual/en/timezones.php).

### CentOS / Fedora

You can modify `/etc/php.ini`, search for the line with `date.timezone` and 
set it to your local timezone, e.g.:

```
date.timezone = Europe/Berlin
```

Now, restart `php-fpm`:

```
$ sudo systemctl restart php-fpm
```

### Debian

On Debian you can modify `/etc/php/7.3/fpm/php.ini` and 
`/etc/php/7.3/cli/php.ini`, where 7.3 is the version of PHP. On Debian 10 it is 
7.3, on Debian 9 it is 7.0. Search for the line with `date.timezone` and 
set it to your local timezone, e.g.:

```
date.timezone = Europe/Berlin
```

Now, restart `php-fpm`:

```
$ sudo systemctl restart php$(/usr/sbin/phpquery -V)-fpm
```

## Portal Configuration

In the portal you can enable the expiry at night by setting the 
`sessionExpireAtNight` option in `/etc/vpn-user-portal/config.php`, e.g.:

```
'sessionExpireAtNight' => true,
```

The default is `false`.
