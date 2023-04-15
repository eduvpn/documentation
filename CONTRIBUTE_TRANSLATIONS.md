# Contribute Translations

If you'd like to contribute translations to the VPN software this document
explains how.

## Server

You can check which translations are already available, and possibly update 
them if they are out of date:

* [vpn-user-portal](https://git.sr.ht/~fkooman/vpn-user-portal/tree/v3/item/locale)

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

## Apps

TBD.

## Submitting

Once you are done, you can submit your translation file either by creating a 
"Pull Request" on GitHub, or simply mailing the file with your translations to
[eduvpn-support@lists.geant.org](mailto:eduvpn-support@lists.geant.org). Don't
forget to mention how/if you want to be 
[credited](https://git.sr.ht/~fkooman/vpn-user-portal/tree/v3/item/locale/CREDITS.md).

Thanks!
