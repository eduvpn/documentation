# Contribute Translations

If you'd like to contribute translations to the VPN software this document
explains how.

## Server

You can check which translations are already available, and possibly update 
them if they are out of date:

* [vpn-user-portal](https://git.sr.ht/~fkooman/vpn-user-portal/tree/v3/item/locale)
* [vpn-portal-artwork-eduVPN](https://git.sr.ht/~fkooman/vpn-portal-artwork-eduVPN/tree/main/item/locale)

If you want to contribute a new translation you can take the 
[empty](https://git.sr.ht/~fkooman/vpn-user-portal/tree/v3/item/locale/empty.php) 
file and translate all strings in there and send it.

Also please update `src/Tpl.php` under the `supportedLanguages()` function, 
e.g.:

```
'nl-NL' => 'Nederlands',
```

The files use the PHP 
[Array](https://secure.php.net/manual/en/language.types.array.php) syntax.

The "key" is the English string, the value should be the translation.

Please feel free to also add yourself to the `CREDITS.md` file as well!

## Apps

Not all instructions are particularly helpful yet, but should give an idea of
where to go/what to do.

### Android

* See [eduvpn/android#395](https://github.com/eduvpn/android/issues/395), 
  [eduvpn/android#323](https://github.com/eduvpn/android/issues/323)

### Windows

Look [here](https://github.com/Amebis/eduVPN/blob/master/doc/Localization.md).

### iOS / macOS

* See [eduvpn/apple#391](https://github.com/eduvpn/apple/issues/391)

### Linux

TBD.

## Submitting

Once you are done, you can submit your translation file either by creating a 
"Pull Request" on GitHub, or simply mailing the file with your translations to
[eduvpn-support@lists.geant.org](mailto:eduvpn-support@lists.geant.org).

Thanks!
