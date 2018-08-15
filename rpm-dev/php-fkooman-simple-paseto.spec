%global commit0 62d3d77218a26d043267b34a4bfc92c8a66898b2

Name:           php-fkooman-simple-paseto
Version:        0.1.7
Release:        1%{?dist}
Summary:        Simple PASETO v2.public for PHP >= 5.4

License:        ISC
URL:            https://git.tuxed.net/fkooman/php-simple-paseto
Source0:        https://git.tuxed.net/fkooman/php-simple-paseto/snapshot/php-simple-paseto-%{commit0}.tar.xz

BuildArch:      noarch

#        "php": ">=5.4",
BuildRequires:  php(language) >= 5.4.0
#    "suggest": {
#        "ext-libsodium": "PHP < 7.2 sodium implementation",
#        "ext-sodium": "PHP >= 7.2 sodium implementation"
#    },
BuildRequires:  php-pecl(libsodium)
#        "ext-hash": "*",
BuildRequires:  php-hash
#        "paragonie/constant_time_encoding": "^1|^2",
#        "symfony/polyfill-php56": "^1"
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(symfony/polyfill-php56)
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpunit
BuildRequires:  %{_bindir}/phpab

#        "php": ">=5.4",
Requires:       php(language) >= 5.4.0
#    "suggest": {
#        "ext-libsodium": "PHP < 7.2 sodium implementation",
#        "ext-sodium": "PHP >= 7.2 sodium implementation"
#    },
Requires:       php-pecl(libsodium)
#        "ext-hash": "*",
Requires:       php-hash
#        "paragonie/constant_time_encoding": "^1|^2",
#        "symfony/polyfill-php56": "^1"
Requires:       php-composer(paragonie/constant_time_encoding)
Requires:       php-composer(symfony/polyfill-php56)

Provides:       php-composer(fkooman/simple-paseto) = %{version}

%description
This is a very simple PASETO implementation written for PHP >= 5.4. It **ONLY** 
supports `v2.public` and nothing else.

%prep
%autosetup -n php-simple-paseto-%{commit0}

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once sprintf('%s/sodium_compat.php', __DIR__);
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
require_once '%{_datadir}/php/Symfony/Polyfill/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/Paseto
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/Paseto

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

%files
%license LICENSE
%doc composer.json CHANGES.md README.md
%dir %{_datadir}/php/fkooman
%{_datadir}/php/fkooman/Paseto

%changelog
* Thu Aug 09 2018 François Kooman <fkooman@tuxed.net> - 0.1.7-1
- update to 0.1.7

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 0.1.6-4
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 0.1.6-3
- use fedora phpab template

* Thu May 24 2018 François Kooman <fkooman@tuxed.net> - 0.1.6-2
- point to new repository

* Tue May 01 2018 François Kooman <fkooman@tuxed.net> - 0.1.6-1
- update to 0.1.6

* Tue Apr 24 2018 François Kooman <fkooman@tuxed.net> - 0.1.5-1
- update to 0.1.5

* Mon Apr 23 2018 François Kooman <fkooman@tuxed.net> - 0.1.4-1
- update to 0.1.4

* Fri Apr 20 2018 François Kooman <fkooman@tuxed.net> - 0.1.3-1
- update to 0.1.3

* Thu Apr 19 2018 François Kooman <fkooman@tuxed.net> - 0.1.2-2
- depend on php-pecl(libsodium)

* Thu Apr 19 2018 François Kooman <fkooman@tuxed.net> - 0.1.2-1
- update to 0.1.2

* Thu Apr 19 2018 François Kooman <fkooman@tuxed.net> - 0.1.1-1
- initial package
