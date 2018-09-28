#global git 05dad054537906ec9cb1916c782c50f0a58a5b9b

Name:           php-fkooman-simple-paseto
Version:        0.2.1
Release:        1%{?dist}
Summary:        Simple PASETO v2.public for PHP >= 5.4

License:        ISC
URL:            https://software.tuxed.net/php-simple-paseto
%if %{defined git}
Source0:        https://git.tuxed.net/fkooman/php-simple-paseto/snapshot/php-simple-paseto-%{git}.tar.xz
%else
Source0:        https://software.tuxed.net/php-simple-paseto/files/php-simple-paseto-%{version}.tar.xz
Source1:        https://software.tuxed.net/php-simple-paseto/files/php-simple-paseto-%{version}.tar.xz.asc
Source2:        gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif

BuildArch:      noarch

BuildRequires:  gnupg2
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpab
#    "require-dev": {
#        "phpunit/phpunit": "^4|^5|^6|^7"
#    },
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
BuildRequires:  phpunit7
%global phpunit %{_bindir}/phpunit7
%else
BuildRequires:  phpunit
%global phpunit %{_bindir}/phpunit
%endif
#    "require": {
#        "ext-hash": "*",
#        "paragonie/constant_time_encoding": "^1.0.3|^2.2.0",
#        "php": ">=5.4",
#        "symfony/polyfill-php56": "^1",
#        "symfony/polyfill-php70": "^1"
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-hash
BuildRequires:  php-composer(paragonie/constant_time_encoding)
#    "suggest": {
#        "ext-libsodium": "PHP < 7.2 sodium implementation",
#        "ext-sodium": "PHP >= 7.2 sodium implementation"
#    },
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
BuildRequires:  php-sodium
%else
BuildRequires:  php-pecl(libsodium)
%endif
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
BuildRequires:  php-composer(symfony/polyfill-php56)
BuildRequires:  php-composer(symfony/polyfill-php70)
%endif

#    "require": {
#        "ext-hash": "*",
#        "paragonie/constant_time_encoding": "^1.0.3|^2.2.0",
#        "php": ">=5.4",
#        "symfony/polyfill-php56": "^1",
#        "symfony/polyfill-php70": "^1"
#    },
Requires:       php(language) >= 5.4.0
Requires:       php-hash
Requires:       php-composer(paragonie/constant_time_encoding)
#    "suggest": {
#        "ext-libsodium": "PHP < 7.2 sodium implementation",
#        "ext-sodium": "PHP >= 7.2 sodium implementation"
#    },
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
Requires:       php-sodium
%else
Requires:       php-pecl(libsodium)
%endif
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
Requires:       php-composer(symfony/polyfill-php56)
Requires:       php-composer(symfony/polyfill-php70)
%endif

Provides:       php-composer(fkooman/simple-paseto) = %{version}

%description
This is a very simple PASETO implementation written for PHP >= 5.4. It **ONLY** 
supports `v2.public` and nothing else.

%prep
%if %{defined git}
%autosetup -n php-simple-paseto-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%autosetup -n php-simple-paseto-%{version}
%endif

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
AUTOLOAD
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once sprintf('%s/sodium_compat.php', __DIR__);
require_once '%{_datadir}/php/Symfony/Polyfill/autoload.php';
AUTOLOAD
%endif

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/Paseto
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/Paseto

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{phpunit} tests --verbose --bootstrap=tests/autoload.php

%files
%license LICENSE
%doc composer.json CHANGES.md README.md
%dir %{_datadir}/php/fkooman
%{_datadir}/php/fkooman/Paseto

%changelog
* Fri Sep 28 2018 François Kooman <fkooman@tuxed.net> - 0.2.1-1
- update to 0.2.1

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
