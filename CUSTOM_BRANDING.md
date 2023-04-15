# Custom Branding

This document describes how to apply your own branding (style and e.g. logo) to
the portal.

## Custom Portal Footer

If all you want is to add a simple text at the bottom of (all) pages, you can
use the "custom footer" functionality.

Create a file in `/etc/vpn-user-portal/views/customFooter.php` with e.g. the 
following content:

    <p>
        If you need help, contact us on <a href="tel:+1234567890">+(1) (234) 567890</a>, or mail <a href="mailto:support@example.org">us</a>!
    </p>

**NOTE**: this footer is *always* visible, also when VPN apps are being 
authorized.

### Translations

You can also use multi language custom footers. You can use the 
`<?=$this->t('Text To Translate');?>` format to make text translatable and 
provide additional translation files. We modify the example above in 
`/etc/vpn-user-portal/views/customFooter.php`:

    <p>
        <?=$this->t('If you need help, contact us on <a href="tel:+1234567890">+(1) (234) 567890</a>, or mail <a href="mailto:support@example.org">us</a>!'); ?>
    </p>

Now for the translation file, you can create a file, e.g `nl_NL.php` for a 
Dutch translation in `/etc/vpn-user-portal/locale/nl_NL.php` with the following
content:

    <?php

    return [
        'If you need help, contact us on <a href="tel:+1234567890">+(1) (234) 567890</a>, or mail <a href="mailto:support@example.org">us</a>!' => 'Als je hulp nodig hebt, neem telefonisch contact met ons op via <a href="tel:+1234567890">+(1) (234) 567890</a>, of per <a href="mailto:support@example.org">mail</a>!',
    ];

Now when you switch languages in the portal, the translation should match when
they exist.
 
**NOTE**: if you want to use single quotes (`'`) in your texts, make sure to
escape them by adding a backslash (`\`) in front of them, e.g. 
`'Don\'t click here!'`.

## Template Overriding

The portal uses templates, located in the following folder:

    /usr/share/vpn-user-portal/views

You can copy the `base.php` from this folder to 
`/etc/vpn-user-portal/views/base.php` and modify it to override the default CSS
for example.

**NOTE**: It is NOT recommended to update other templates than `base.php` as 
they MAY break future software updates. We do NOT guarantee template 
compatibility!

After copying, add a new CSS line in `/etc/vpn-user-portal/views/base.php`
after the existing one:

    <link href="<?=$this->getAssetUrl($requestRoot, 'css/screen.css'); ?>" media="screen" rel="stylesheet">
    <link href="/css/my-screen.css" media="screen" rel="stylesheet">

This will then try to find the CSS file at 
`https://vpn.example.org/css/my-screen.css`. You can look in 
`/usr/share/vpn-user-portal/web/css/screen.css` for the default template CSS.

We have two officially supported themes, you can find the relevant files here 
and get inspiration:

* [eduVPN](https://git.sr.ht/~fkooman/vpn-portal-artwork-eduVPN)
* [Let's Connect!](https://git.sr.ht/~fkooman/vpn-portal-artwork-LC)

See [BRANDING](BRANDING.md) if you want to use those instead of creating your
own.
