#global git d25a76d5faa03166daf87a40bc65965f6f3512eb

Name:           php-fkooman-jwt
Version:        1.0.1
Release:        1%{?dist}
Summary:        JWT Library

License:        MIT
URL:            https://software.tuxed.net/php-jwt
%if %{defined git}
Source0:        https://git.tuxed.net/fkooman/php-jwt/snapshot/php-jwt-%{git}.tar.xz
%else
Source0:        https://software.tuxed.net/php-jwt/files/php-jwt-%{version}.tar.xz
Source1:        https://software.tuxed.net/php-jwt/files/php-jwt-%{version}.tar.xz.minisig
Source2:        minisign-8466FFE127BCDC82.pub
%endif

# we do not wish to depend on paragonie/sodium_compat as we'll always require
# php-pecl(libsodium) on CentOS 7, instead we have a small mapping wrapper that
# converts calls to the Sodium namespaced php-pecl(libsodium) 1.x 
# constants/functions
Patch0:         php-fkooman-jwt-sodium.patch

BuildArch:      noarch

BuildRequires:  minisign
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
#        "paragonie/sodium_compat": "^1",
#        "php": ">= 5.4.8",
#        "symfony/polyfill-php56": "^1"
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
%endif

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
#        "paragonie/sodium_compat": "^1",
#        "php": ">= 5.4.8",
#        "symfony/polyfill-php56": "^1"
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
%endif

%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
Requires:   php-sodium
%else
Requires:   php-pecl(libsodium)
%endif

Provides:  php-composer(fkooman/jwt) = %{version}

%description
This is small JSON Web Token implementation. It only supports signatures 
with the following signature algorithms:

* HS256 (HMAC using SHA-256)
* RS256 (RSASSA-PKCS1-v1_5 using SHA-256)
* EdDSA (Ed25519, RFC 8037)

The first two seem to be the most widely deployed JWT signature algorithms. 
The library does NOT support encryption/decryption due to the can of worms 
that would open. It MAY support encryption/decryption in the future, but not 
with RSA.

%prep
%if %{defined git}
%autosetup -n php-jwt-%{git}
%else
/usr/bin/minisign -V -m %{SOURCE0} -x %{SOURCE1} -p %{SOURCE2}
%autosetup -n php-jwt-%{version}
%endif

%if 0%{?fedora} < 28 && 0%{?rhel} < 8
%patch0 -p1
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
* Tue Aug 20 2019 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Fri Aug 09 2019 François Kooman <fkooman@tuxed.net> - 1.0.0-3
- switch to minisign signature verification for release builds

* Mon Mar 18 2019 François Kooman <fkooman@tuxed.net> - 1.0.0-2
- rebuilt

* Wed Mar 06 2019 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- update to 1.0.0

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
