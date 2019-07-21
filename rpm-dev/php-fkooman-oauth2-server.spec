%global git d5fca179de2e09212db20df2bf8187c3320124d0

Name:           php-fkooman-oauth2-server
Version:        5.0.1
Release:        1%{?dist}
Summary:        Very simple OAuth 2.0 server

License:        MIT
URL:            https://software.tuxed.net/php-oauth2-server
%if %{defined git}
Source0:        https://git.tuxed.net/fkooman/php-oauth2-server/snapshot/php-oauth2-server-%{git}.tar.xz
%else
Source0:        https://software.tuxed.net/php-oauth2-server/files/php-oauth2-server-%{version}.tar.xz
Source1:        https://software.tuxed.net/php-oauth2-server/files/php-oauth2-server-%{version}.tar.xz.asc
Source2:        gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif

BuildArch:      noarch

BuildRequires:  gnupg2
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpab
#    "require-dev": {
#        "phpunit/phpunit": "^4.8.35|^5|^6|^7"
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
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
#        "paragonie/constant_time_encoding": "^1.0.3|^2.2.0",
#        "paragonie/random_compat": ">=1",
#        "php": ">=5.4",
#        "symfony/polyfill-php56": "^1"
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-date
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-spl
BuildRequires:  php-composer(paragonie/constant_time_encoding)
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(symfony/polyfill-php56)
%endif

#    "require": {
#        "ext-date": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
#        "paragonie/constant_time_encoding": "^1.0.3|^2.2.0",
#        "paragonie/random_compat": ">=1",
#        "php": ">=5.4",
#        "symfony/polyfill-php56": "^1"
#    },
Requires:       php(language) >= 5.4.0
Requires:       php-date
Requires:       php-hash
Requires:       php-json
Requires:       php-pcre
Requires:       php-pdo
Requires:       php-spl
Requires:       php-composer(paragonie/constant_time_encoding)
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
Requires:       php-composer(paragonie/random_compat)
Requires:       php-composer(symfony/polyfill-php56)
%endif

Provides:       php-composer(fkooman/oauth2-server) = %{version}

%description
This is a very simple OAuth 2.0 server for integration in your own 
application. It has minimal dependencies, but still tries to be secure. 
The main purpose is to be compatible with PHP 5.4.

%prep
%if %{defined git}
%autosetup -n php-oauth2-server-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%autosetup -n php-oauth2-server-%{version}
%endif

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
AUTOLOAD
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/random_compat/autoload.php';
require_once '%{_datadir}/php/Symfony/Polyfill/autoload.php';
AUTOLOAD
%endif

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/OAuth/Server
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/OAuth/Server

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
%dir %{_datadir}/php/fkooman/OAuth
%{_datadir}/php/fkooman/OAuth/Server

%changelog
* Sun Jul 21 2019 François Kooman <fkooman@tuxed.net> - 5.0.1-1
- update to 5.0.1

* Wed Mar 27 2019 François Kooman <fkooman@tuxed.net> - 5.0.0-1
- update to 5.0.0

* Wed Mar 06 2019 François Kooman <fkooman@tuxed.net> - 4.0.0-1
- update to 4.0.0

* Mon Nov 26 2018 François Kooman <fkooman@tuxed.net> - 3.0.5-1
- update to 3.0.5

* Mon Nov 26 2018 François Kooman <fkooman@tuxed.net> - 3.0.4-1
- update to 3.0.4

* Mon Nov 26 2018 François Kooman <fkooman@tuxed.net> - 3.0.3-1
- update to 3.0.3

* Fri Sep 21 2018 François Kooman <fkooman@tuxed.net> - 3.0.2-1
- update to 3.0.2

* Sun Sep 09 2018 François Kooman <fkooman@tuxed.net> - 3.0.1-7
- merge dev and prod spec files in one
- cleanup requirements

* Sat Sep 08 2018 François Kooman <fkooman@tuxed.net> - 3.0.1-6
- only autoload compat libraries on older versions of Fedora/EL
- requires php-sodium on modern OSes to make sure we do not need sodium compat

* Sun Aug 05 2018 François Kooman <fkooman@tuxed.net> - 3.0.1-5
- use phpunit7 on supported platforms

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 3.0.1-4
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 3.0.1-3
- use fedora phpab template for generating autoloader

* Thu Jun 28 2018 François Kooman <fkooman@tuxed.net> - 3.0.1-2
- use release tarball instead of Git tarball
- verify GPG signature

* Fri Jun 08 2018 François Kooman <fkooman@tuxed.net> - 3.0.1-1
- update to 3.0.1

* Fri Jun 01 2018 François Kooman <fkooman@tuxed.net> - 3.0.0-3
- update upstream URL to git.tuxed.net

* Thu Apr 19 2018 François Kooman <fkooman@tuxed.net> - 3.0.0-2
- depend on php-pecl(libsodium)

* Mon Mar 19 2018 François Kooman <fkooman@tuxed.net> - 3.0.0-1
- update to 3.0.0

* Wed Jan 10 2018 François Kooman <fkooman@tuxed.net> - 2.2.0-1
- update to 2.2.0

* Thu Dec 07 2017 François Kooman <fkooman@tuxed.net> - 2.1.0-2
- use phpab to generate the classloader

* Thu Nov 30 2017 François Kooman <fkooman@tuxed.net> - 2.1.0-1
- update to 2.1.0

* Wed Nov 29 2017 François Kooman <fkooman@tuxed.net> - 2.0.1-1
- update to 2.0.1

* Tue Nov 14 2017 François Kooman <fkooman@tuxed.net> - 2.0.0-1
- update to 2.0.0

* Mon Sep 18 2017 François Kooman <fkooman@tuxed.net> - 1.1.0-1
- update to 1.1.0 

* Thu Jul 06 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
