---
title: Two-factor Authentication
description: Configure 2FA (Two Factor Authentication)
category: advanced
---

The VPN service supports 2FA for which the user can self-enroll. This can be
either voluntary, or enforced by the administrator.

**NOTE**: make sure the clock of your server is synchronized using NTP, 
otherwise TOTP will not work properly or stop working when then server time 
deviates too much!

## Threat Model

The way 2FA is implemented, together with the native apps, protects explicitly 
against this threat: the user's credentials become available to an attacker.

When 2FA is enabled, the user's credentials are useless to an attacker, 
assuming the user already enrolled for 2FA, possibly by being forced to enroll
for 2FA on first login.

When using the Let's Connect!/eduVPN applications, the user's certificates is
protected from exporting by the user, and thus the attacker, making it 
impossible to "steal" the certificate. This is implemented by importing the 
user's certificate in the "key store" on Windows and macOS.

At the moment, 
[TOTP](https://en.wikipedia.org/wiki/Time-based_One-time_Password_Algorithm) is 
supported.

## Configuration

By default, 2FA is disabled on new installations. The software can be 
configured to make 2FA optional, or to enforce the use of 2FA, i.e. enroll 
"on first use".

### Disable 2FA

This will fully disable 2FA and is the _default_. The user won't be asked for 
2FA, nor are they able to enroll themselves. Users that enrolled themselves 
before are no longer asked for 2FA.

    'requireTwoFactor' => false,
    'twoFactorMethods' => [],

### Optional 2FA

The default configuration, in `/etc/vpn-user-portal/config.php`:

    'requireTwoFactor' => false,
    'twoFactorMethods' => ['totp'],

This allows users to enroll for TOTP themselves, but does not force them to do 
so.

### Enforce 2FA

This will force the user to use 2FA, if they are not enrolled they will be 
forced to enroll when they login to the service, either directly to the portal,
or through an application obtaining authorization.

    'requireTwoFactor' => true,
    'twoFactorMethods' => ['totp'],

## Enrollment

Users can enroll themselves in the portal on the "Account" page if 2FA is 
optional, or will be forced directly when 2FA is enforced.

## Recovery

If a user lost their second factor credentials, 2FA can be removed through 
the admin portal for that particular user.

If access to the admin portal is not available (anymore), the 2FA enrollment
can also be removed manually. The example below will remove the OTP for the 
user `foo`:

    $ sudo sqlite3 /var/lib/vpn-server-api/db.sqlite
    SQLite version 3.7.17 2013-05-20 00:56:22
    Enter ".help" for instructions
    Enter SQL statements terminated with a ";"
    sqlite> DELETE FROM otp WHERE user_id='foo';
    sqlite> .q
