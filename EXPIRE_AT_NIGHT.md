**WORK IN PROGRESS** 

Please provide feedback if you have any!

**NOTE**: this is only implemented in vpn-user-portal >= 2.3.10 which has not
been released yet.

# Expire At Night

In vpn-user-portal >= 2.3.10 it is possible to expire VPN sessions at night 
instead of exactly after the duration specified in `sessionExpiry`. The goal
is to prevent that the user will be disconnected from the VPN during working 
hours.

By VPN session expiry we mean the moment at which the VPN session won't work 
anymore without the user authenticating/authorizing again. The default after 
which a session expires is 90 days, but this can be modified by the 
administrator.

The `sessionExpiry` becomes the upper bound of when the session will expire. 
The new expiry is moved back in time until the first 04:00 is reached. This 
could be the same day, or the previous day if the time is currently between 
00:00 and 04:00.

**NOTE**: currently the nightly expiry ONLY works when the `sessionExpiry` is
`P7D` (7 days) or longer. We may implement this also for sessions that expire
sooner.

## Server Configuration

To check the timezone your server is set to:

```
$ timedatectl 
               Local time: Mi 2021-04-14 21:27:24 CEST
           Universal time: Mi 2021-04-14 19:27:24 UTC
                 RTC time: Mi 2021-04-14 19:27:23
                Time zone: Europe/Berlin (CEST, +0200)
System clock synchronized: no
              NTP service: active
          RTC in local TZ: no
```

In the example above it set to the `Europe/Berlin` timezone. It could be your 
local time zone, or `UTC` which is also fine.

Verify what PHP thinks of this:

```
$ php -r 'echo ini_get("date.timezone");'
$ php -r 'echo date_default_timezone_get();'
Europe/Berlin
```

All good! 

### CentOS / Fedora

The system timezone is _not_ picked up by PHP on Fedora/CentOS, you need to 
manually set it. The default is UTC otherwise, independent of what your 
system's timezone is. On CentOS it is even slightly worse, if you don't set 
the `date.timezone` field PHP will complain (because PHP is so old on CentOS). 
That's why the `deploy_centos.sh` script configures `UTC` for you by default in 
the file `/etc/php.d/70-timezone.ini`. You can modify this and set it to your 
local timezone. Use [these](https://www.php.net/manual/en/timezones.php) values.

On Fedora you can directly edit `/etc/php.ini` and set the `date.timezone` 
field there.

Don't forget to restart php-fpm after making changes:

```
$ sudo systemctl restart php-fpm
```

Now you should be good to go.

## Portal Configuration

In the portal you can enable the expiry at night by setting the 
`sessionExpireAtNight` option in `/etc/vpn-user-portal/config.php`, e.g.:

```
'sessionExpireAtNight' => true,
```

The default is `false`.
