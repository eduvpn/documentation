%global git 5d3d80c0e1c873570c41587eb5e072b668e965f0

Name:           php-fkooman-jwt
Version:        0.3.0
Release:        1%{?dist}
Summary:        JWT Library

License:        MIT
URL:            https://software.tuxed.net/php-jwt
%if %{defined git}
Source0:        https://git.tuxed.net/fkooman/php-jwt/snapshot/php-jwt-%{git}.tar.xz
%else
Source0:        https://software.tuxed.net/php-jwt/files/php-jwt-%{version}.tar.xz
Source1:        https://software.tuxed.net/php-jwt/files/php-jwt-%{version}.tar.xz.asc
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
#        "ext-date": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-openssl": "*",
#        "ext-spl": "*",
#        "paragonie/constant_time_encoding": "^1.0.3|^2.2.0",
#        "paragonie/random_compat": ">=1",
#        "php": ">= 5.4.8",
#        "symfony/polyfill-php56": "^1",
#        "symfony/polyfill-php70": "^1"
#    },
BuildRequires:  php(language) >= 5.4.8
BuildRequires:  php-date
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-openssl
BuildRequires:  php-spl
BuildRequires:  php-composer(paragonie/constant_time_encoding)
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(symfony/polyfill-php56)
BuildRequires:  php-composer(symfony/polyfill-php70)
%endif
#    "suggest": {
#        "ext-libsodium": "PHP < 7.2 sodium implementation",
#        "ext-sodium": "PHP >= 7.2 sodium implementation"
#    },
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
BuildRequires:  php-sodium
%else
BuildRequires:  php-pecl(libsodium)
%endif

#    "require": {
#        "ext-date": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-openssl": "*",
#        "ext-spl": "*",
#        "paragonie/constant_time_encoding": "^1.0.3|^2.2.0",
#        "paragonie/random_compat": ">=1",
#        "php": ">= 5.4.8",
#        "symfony/polyfill-php56": "^1",
#        "symfony/polyfill-php70": "^1"
#    },
Requires:  php(language) >= 5.4.8
Requires:  php-date
Requires:  php-hash
Requires:  php-json
Requires:  php-openssl
Requires:  php-spl
Requires:  php-composer(paragonie/constant_time_encoding)
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
Requires:  php-composer(paragonie/random_compat)
Requires:  php-composer(symfony/polyfill-php56)
Requires:  php-composer(symfony/polyfill-php70)
%endif
#    "suggest": {
#        "ext-libsodium": "PHP < 7.2 sodium implementation",
#        "ext-sodium": "PHP >= 7.2 sodium implementation"
#    },
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
Requires:   php-sodium
%else
Requires:   php-pecl(libsodium)
%endif

Provides:  php-composer(fkooman/jwt) = %{version}

%description
JWT Library.

%prep
%if %{defined git}
%autosetup -n php-jwt-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%autosetup -n php-jwt-%{version}
%endif

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php',
));
AUTOLOAD
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
cat <<'AUTOLOAD' | tee -a src/autoload.php
\Fedora\Autoloader\Dependencies::required(array(
    __DIR__.'/sodium_compat.php',
    '%{_datadir}/php/random_compat/autoload.php',
    '%{_datadir}/php/Symfony/Polyfill/autoload.php',
));
AUTOLOAD
%endif

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/Jwt
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/Jwt

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
%{_datadir}/php/fkooman/Jwt

%changelog
* Fri Feb 08 2019 François Kooman <fkooman@tuxed.net> - 0.3.0-1
- update to 0.3.0

* Tue Oct 23 2018 François Kooman <fkooman@tuxed.net> - 0.2.2-1
- update to 0.2.2

* Tue Oct 23 2018 François Kooman <fkooman@tuxed.net> - 0.2.1-1
- update to 0.2.1

* Fri Sep 28 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-2
- fix EL7 builds (autoloader syntax, missing R/BR)

* Fri Sep 28 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-1
- initial package
