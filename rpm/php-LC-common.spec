#global git 67d330af8b04f6e26ecffa780a0c11420af37281

Name:       php-LC-common
Version:    2.0.6
Release:    1%{?dist}
Summary:    Common VPN library
Group:      System Environment/Libraries
License:    AGPLv3+
URL:        https://github.com/eduvpn/vpn-lib-common
%if %{defined git}
Source0:    https://github.com/eduvpn/vpn-lib-common/archive/%{git}/vpn-lib-common-%{version}-%{git}.tar.gz
%else
Source0:    https://github.com/eduvpn/vpn-lib-common/releases/download/%{version}/vpn-lib-common-%{version}.tar.xz
Source1:    https://github.com/eduvpn/vpn-lib-common/releases/download/%{version}/vpn-lib-common-%{version}.tar.xz.minisig
Source2:    minisign-8466FFE127BCDC82.pub
%endif

BuildArch:  noarch

BuildRequires:  minisign
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
#        "ext-filter": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-mbstring": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
#        "fkooman/secookie": "^2",
#        "ircmaxell/password-compat": "^1",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": ">=1",
#        "php": ">= 5.4",
#        "psr/log": "^1.0",
#        "symfony/polyfill-php56": "^1"
#    },
#    "suggest": {
#        "ext-ldap": "Support LDAP user authentication",
#        "ext-radius": "Support RADIUS user authentication"
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-filter
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-mbstring
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-spl
BuildRequires:  php-composer(fkooman/secookie)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(psr/log)
BuildRequires:  php-ldap
BuildRequires:  php-radius
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
BuildRequires:  php-composer(ircmaxell/password-compat)
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(symfony/polyfill-php56)
%endif

#    "require": {
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-filter": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-mbstring": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
#        "fkooman/secookie": "^2",
#        "ircmaxell/password-compat": "^1",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": ">=1",
#        "php": ">= 5.4",
#        "psr/log": "^1.0",
#        "symfony/polyfill-php56": "^1"
#    },
#    "suggest": {
#        "ext-ldap": "Support LDAP user authentication",
#        "ext-radius": "Support RADIUS user authentication"
#    },
Requires:       php(language) >= 5.4.0
Requires:       php-curl
Requires:       php-date
Requires:       php-filter
Requires:       php-hash
Requires:       php-json
Requires:       php-mbstring
Requires:       php-pcre
Requires:       php-pdo
Requires:       php-spl
Requires:       php-composer(fkooman/secookie)
Requires:       php-composer(paragonie/constant_time_encoding)
Requires:       php-composer(psr/log)
Requires:       php-ldap
Requires:       php-radius
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
Requires:       php-composer(ircmaxell/password-compat)
Requires:       php-composer(paragonie/random_compat)
Requires:       php-composer(symfony/polyfill-php56)
%endif

Provides:       php-composer(lc/common) = %{version}

%description
Common VPN library.

%prep
%if %{defined git}
%setup -qn vpn-lib-common-%{git}
%else
/usr/bin/minisign -V -m %{SOURCE0} -x %{SOURCE1} -p %{SOURCE2}
%setup -qn vpn-lib-common-%{version}
%endif

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/fkooman/SeCookie/autoload.php';
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
require_once '%{_datadir}/php/Psr/Log/autoload.php';
AUTOLOAD
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/password_compat/password.php';
require_once '%{_datadir}/php/random_compat/autoload.php';
require_once '%{_datadir}/php/Symfony/Polyfill/autoload.php';
AUTOLOAD
%endif

%install
mkdir -p %{buildroot}%{_datadir}/php/LC/Common
cp -pr src/* %{buildroot}%{_datadir}/php/LC/Common

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{phpunit} tests --verbose --bootstrap=tests/autoload.php

%files
%dir %{_datadir}/php/LC
%{_datadir}/php/LC/Common
%doc README.md composer.json CHANGES.md
%license LICENSE

%changelog
* Wed Sep 25 2019 François Kooman <fkooman@tuxed.net> - 2.0.6-1
- update to 2.0.6

* Thu Aug 29 2019 François Kooman <fkooman@tuxed.net> - 2.0.5-1
- update to 2.0.5

* Tue Aug 13 2019 François Kooman <fkooman@tuxed.net> - 2.0.4-1
- update to 2.0.4

* Fri Aug 09 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-2
- switch to minisign signature verification for release builds

* Sat Jul 20 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-1
- update to 2.0.3

* Fri Jun 07 2019 François Kooman <fkooman@tuxed.net> - 2.0.2-1
- update to 2.0.2

* Fri Apr 26 2019 François Kooman <fkooman@tuxed.net> - 2.0.1-1
- update to 2.0.1

* Mon Apr 01 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-1
- update to 2.0.0
