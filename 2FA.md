# Two-factor Authentication

The VPN service supports 2FA for which the user can self-enroll. This can be
either voluntary, or enforced by the administrator.

## Threat Model

The way 2FA is implements, together with the native apps, protects explicitly 
against these threats:

1. The user's credentials become available to an attacker;
2. An attacker obtains the user's client certificate from the user's device.

When 2FA is enabled, the user's credentials are useless to an attacker, 
assuming the user already enrolled for 2FA (on first login).

When using the Let's Connect!/eduVPN applications, the user's certificates is
protected from exporting by the user (and thus the attacker) making it 
impossible to "steal" the certificate. This is implemented by importing the 
user's certificate in the "key store" on Windows and macOS.

At the moment, 
[TOTP](https://en.wikipedia.org/wiki/Time-based_One-time_Password_Algorithm) is 
supported.

## Configuration

By default, the user has the option to self-enroll for 2FA at their discretion. 
However, the software can be configured to _enforce_ 2FA, thus forcing all 
users to enroll for 2FA when they (first) authenticate to the service.

### Optional 2FA

The default configuration, in `/etc/vpn-user-portal/default/config.php`:

    'requireTwoFactor' => false,
    'twoFactorMethods' => ['totp'],

This allows users to enroll for TOTP themselves, but does not force them to do 
so.

### Disable 2FA

This will fully disable 2FA. The user won't be asked for 2FA, nor are they 
able to enroll themselves.

    'requireTwoFactor' => false,
    'twoFactorMethods' => [],

### Enforce 2FA

This will force the user to use 2FA, if they are not enrolled they will be 
forced to enroll when they login to the service, either directly to the portal,
or through an application obtaining authorization.

    'requireTwoFactor' => true,
    'twoFactorMethods' => ['totp'],

## Enrollment

Users can enroll themselves in the portal on the "Account" page if 2FA is 
optional.

## Recovery

If a user lost their second factor credentials, 2FA can be removed through 
the admin portal for that particular user.

If access to the admin portal is not available (anymore), the 2FA enrollment
can also be removed manually. 

    $ sudo sqlite3 /var/lib/vpn-server-api/default/db.sqlite

Perform the following query to remove the OTP secret for the user `foo`:

    DELETE FROM otp WHERE user_id='foo';
