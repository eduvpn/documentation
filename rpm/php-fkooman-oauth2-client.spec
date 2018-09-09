#global git 3d96587ed78b1ecd72085847cae779b6edeb4526

Name:           php-fkooman-oauth2-client
Version:        7.1.3
Release:        7%{?dist}
Summary:        Very simple OAuth 2.0 client

License:        MIT
URL:            https://software.tuxed.net/php-oauth2-client
%if %{defined git}
Source0:        https://git.tuxed.net/fkooman/php-oauth2-client/snapshot/php-oauth2-client-%{git}.tar.xz
%else
Source0:        https://software.tuxed.net/php-oauth2-client/files/php-oauth2-client-%{version}.tar.xz
Source1:        https://software.tuxed.net/php-oauth2-client/files/php-oauth2-client-%{version}.tar.xz.asc
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
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-session": "*",
#        "ext-spl": "*",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": ">=1",
#        "php": ">=5.4",
#        "psr/log": "^1.0",
#        "symfony/polyfill-php56": "^1"
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-session
BuildRequires:  php-spl
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(psr/log)
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(symfony/polyfill-php56)
%endif

#    "require": {
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-session": "*",
#        "ext-spl": "*",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": ">=1",
#        "php": ">=5.4",
#        "psr/log": "^1.0",
#        "symfony/polyfill-php56": "^1"
#    },
Requires:       php(language) >= 5.4.0
Requires:       php-curl
Requires:       php-date
Requires:       php-hash
Requires:       php-json
Requires:       php-pcre
Requires:       php-pdo
Requires:       php-session
Requires:       php-spl
Requires:       php-composer(paragonie/constant_time_encoding)
Requires:       php-composer(psr/log)
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
Requires:       php-composer(paragonie/random_compat)
Requires:       php-composer(symfony/polyfill-php56)
%endif

Provides:       php-composer(fkooman/oauth2-client) = %{version}

%description
This is a very simple OAuth 2.0 client for integration in your own 
application. It has minimal dependencies, but still tries to be secure. 
The main purpose is to be compatible with PHP 5.4.

%prep
%if %{defined git}
%autosetup -n php-oauth2-client-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%autosetup -n php-oauth2-client-%{version}
%endif

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
require_once '%{_datadir}/php/Psr/Log/autoload.php';
AUTOLOAD
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/random_compat/autoload.php';
require_once '%{_datadir}/php/Symfony/Polyfill/autoload.php';
AUTOLOAD
%endif

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/OAuth/Client
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/OAuth/Client

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
%{_datadir}/php/fkooman/OAuth/Client

%changelog
* Sun Sep 09 2018 François Kooman <fkooman@tuxed.net> - 7.1.3-7
- merge dev and prod spec files in one
- cleanup requirements

* Sat Sep 08 2018 François Kooman <fkooman@tuxed.net> - 7.1.3-6
- add psr/log to autoloader
- only autoload compat libraries on older versions of Fedora/EL

* Sun Aug 05 2018 François Kooman <fkooman@tuxed.net> - 7.1.3-5
- use phpunit7 on supported platforms

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 7.1.3-4
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 7.1.3-3
- use fedora phpab template for generating autoloader

* Thu Jun 28 2018 François Kooman <fkooman@tuxed.net> - 7.1.3-2
- use release tarball instead of Git tarball
- verify GPG signature

* Sat Jun 02 2018 François Kooman <fkooman@tuxed.net> - 7.1.3-1
- update to 7.1.3

* Fri Jun 01 2018 François Kooman <fkooman@tuxed.net> - 7.1.2-2
- update upstream URL to git.tuxed.net

* Tue May 22 2018 François Kooman <fkooman@tuxed.net> - 7.1.2-1
- update to 7.1.2

* Tue May 22 2018 François Kooman <fkooman@tuxed.net> - 7.1.1-1
- update to 7.1.1

* Fri May 18 2018 François Kooman <fkooman@tuxed.net> - 7.1.0-1
- update to 7.1.0

* Thu Apr 12 2018 François Kooman <fkooman@tuxed.net> - 7.0.0-1
- update to 7.0.0

* Wed Mar 21 2018 François Kooman <fkooman@tuxed.net> - 6.0.2-1
- update to 6.0.2

* Thu Dec 07 2017 François Kooman <fkooman@tuxed.net> - 6.0.1-2
- use phpab to generate the classloader

* Tue Nov 28 2017 François Kooman <fkooman@tuxed.net> - 6.0.1-1
- update to 6.0.1

* Mon Nov 27 2017 François Kooman <fkooman@tuxed.net> - 6.0.0-1
- update to 6.0.0

* Fri Nov 17 2017 François Kooman <fkooman@tuxed.net> - 5.0.3-1
- update to 5.0.3

* Wed Nov 08 2017 François Kooman <fkooman@tuxed.net> - 5.0.2-1
- update to 5.0.2

* Mon Sep 18 2017 François Kooman <fkooman@tuxed.net> - 5.0.1-1
- update to 5.0.1

* Thu Jul 06 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-1
- update to 5.0.0
