---
title: Custom Branding
description: Apply your own Branding/Themes
category: howto
---

This document describes how to apply your own branding (style and e.g. logo) to
the portal.

# Custom Portal Footer

If all you want is to add a simple text at the bottom of (all) pages, you can
use the "custom footer" functionality.

Create a file in `/etc/vpn-user-portal/views/customFooter.php` with e.g. the 
following content:

    <p class="plain">
        If you need help, contact us on 
        <a href="tel:+1234567890">+(1) (234) 567890</a>, or mail 
        <a href="mailto:support@example.org">us</a>!
    </p>

**NOTE**: this footer is *always* visible, also when VPN apps are being 
authorized.

# Template Overriding

The portals use templates, located in the following folders:

    /usr/share/vpn-user-portal/views

You can copy the `base.php` from this folder to 
`/etc/vpn-user-portal/views/base.php` and modify it to override the defaults. 
For instance by adding an extra line pointing to an additional CSS file.

**NOTE**: It is NOT recommended to update other templates than `base.php` as 
they MAY break future software updates. We do NOT guarantee template 
compatibility!

For example, for eduVPN we use this addition to the `base.php` file under the
default CSS line:

    <link href="/css/eduvpn.css" media="screen" rel="stylesheet">

# CSS

Place, the CSS file, in this case `eduvpn.css`, in 
`/var/www/html/css/eduvpn.css`.

For eduVPN we show a logo that is placed in 
`/var/www/html/img/eduvpn.png` that is linked to from the CSS file, 
for example:

    /** 
     * eduvpn custom style
     */
    h1, h2, h3, h4 {
        font-weight: 500;
    }

    a {
        color: #ed6b06;
    }

    ul.menu li.active a, ul.menu li.active span {
        background-color: #ed6b06;
    }

    /* only show the logo when width is >= 800px */
    @media (min-width: 800px) {
        h1 {
            display: block;
            float: right;
            color: transparent; /* hide header text */
            width: 300px;
            height: 120px;
            background-image: url("/img/eduVPN/eduVPN.png");
            background-repeat: no-repeat;
            background-position: 100% 0%;
        }

        ul.menu {
            /* leave enough room for the background logo */
            margin-right: 325px;
            min-height: 120px;
        }
    }
