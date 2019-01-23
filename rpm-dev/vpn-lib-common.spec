%global git 7aad6d3d2d377ba54ec1a3c34ee5880099a3947d

Name:       vpn-lib-common
Version:    2.0.0
Release:    0.8%{?dist}
Summary:    Common VPN library
Group:      System Environment/Libraries
License:    AGPLv3+
URL:        https://github.com/eduvpn/vpn-lib-common
%if %{defined git}
Source0:    https://github.com/eduvpn/vpn-lib-common/archive/%{git}/vpn-lib-common-%{version}-%{git}.tar.gz
%else
Source0:    https://github.com/eduvpn/vpn-lib-common/releases/download/%{version}/vpn-lib-common-%{version}.tar.xz
Source1:    https://github.com/eduvpn/vpn-lib-common/releases/download/%{version}/vpn-lib-common-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif

BuildArch:  noarch

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
#        "ext-filter": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-ldap": "*",
#        "ext-mbstring": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-radius": "*",
#        "ext-spl": "*",
#        "fkooman/secookie": "^2",
#        "ircmaxell/password-compat": "^1",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": "^1|^2",
#        "php": ">= 5.4",
#        "psr/log": "^1.0",
#        "symfony/polyfill-php56": "^1",
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-filter
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-ldap
BuildRequires:  php-mbstring
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-radius
BuildRequires:  php-spl
BuildRequires:  php-composer(fkooman/secookie)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(psr/log)
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
#        "ext-ldap": "*",
#        "ext-mbstring": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-radius": "*",
#        "ext-spl": "*",
#        "fkooman/secookie": "^2",
#        "ircmaxell/password-compat": "^1",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": "^1|^2",
#        "php": ">= 5.4",
#        "psr/log": "^1.0",
#        "symfony/polyfill-php56": "^1",
#    },
Requires:       php(language) >= 5.4.0
Requires:       php-curl
Requires:       php-date
Requires:       php-filter
Requires:       php-hash
Requires:       php-json
Requires:       php-ldap
Requires:       php-mbstring
Requires:       php-pcre
Requires:       php-pdo
Requires:       php-radius
Requires:       php-spl
Requires:       php-composer(fkooman/secookie)
Requires:       php-composer(paragonie/constant_time_encoding)
Requires:       php-composer(psr/log)
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
Requires:       php-composer(ircmaxell/password-compat)
Requires:       php-composer(paragonie/random_compat)
Requires:       php-composer(symfony/polyfill-php56)
%endif

%description
Common VPN library.

%prep
%if %{defined git}
%setup -qn vpn-lib-common-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
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
mkdir -p %{buildroot}%{_datadir}/php/LetsConnect/Common
cp -pr src/* %{buildroot}%{_datadir}/php/LetsConnect/Common

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{phpunit} tests --verbose --bootstrap=tests/autoload.php

%files
%dir %{_datadir}/php/LetsConnect
%{_datadir}/php/LetsConnect/Common
%doc README.md composer.json CHANGES.md
%license LICENSE

%changelog
* Tue Jan 22 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.8
- rebuilt

* Thu Jan 17 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.7
- rebuilt

* Wed Jan 16 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.6
- rebuilt

* Tue Jan 15 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.5
- rebuilt

* Tue Jan 15 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.4
- rebuilt

* Tue Jan 15 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-0.3
- update to 2.0.0
