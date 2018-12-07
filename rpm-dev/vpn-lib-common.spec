%global git 59b56e4b0a9247782c71b9d698eda8d15a022123

Name:       vpn-lib-common
Version:    1.3.3
Release:    0.6%{?dist}
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
#        "ext-gettext": "*",
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
#        "twig/extensions": "^1",
#        "twig/twig": "^1"
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-filter
BuildRequires:  php-gettext
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
BuildRequires:  php-composer(twig/extensions) < 2.0
BuildRequires:  php-composer(twig/twig) < 2.0
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
BuildRequires:  php-composer(ircmaxell/password-compat)
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(symfony/polyfill-php56)
%endif

#    "require": {
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-filter": "*",
#        "ext-gettext": "*",
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
#        "twig/extensions": "^1",
#        "twig/twig": "^1"
#    },
Requires:       php(language) >= 5.4.0
Requires:       php-curl
Requires:       php-date
Requires:       php-filter
Requires:       php-gettext
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
Requires:       php-composer(twig/extensions) < 2.0
Requires:       php-composer(twig/twig) < 2.0
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
require_once '%{_datadir}/php/Twig/Extensions/autoload.php';
require_once '%{_datadir}/php/Twig/autoload.php';
AUTOLOAD
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/password_compat/password.php';
require_once '%{_datadir}/php/random_compat/autoload.php';
require_once '%{_datadir}/php/Symfony/Polyfill/autoload.php';
AUTOLOAD
%endif

%install
mkdir -p %{buildroot}%{_datadir}/php/SURFnet/VPN/Common
cp -pr src/* %{buildroot}%{_datadir}/php/SURFnet/VPN/Common

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{phpunit} tests --verbose --bootstrap=tests/autoload.php

%files
%dir %{_datadir}/php/SURFnet
%dir %{_datadir}/php/SURFnet/VPN
%{_datadir}/php/SURFnet/VPN/Common
%doc README.md composer.json CHANGES.md
%license LICENSE

%changelog
* Fri Dec 07 2018 François Kooman <fkooman@tuxed.net> - 1.3.3-0.6
- rebuilt

* Fri Dec 07 2018 François Kooman <fkooman@tuxed.net> - 1.3.3-0.5
- rebuilt

* Thu Dec 06 2018 François Kooman <fkooman@tuxed.net> - 1.3.3-0.4
- rebuilt

* Thu Dec 06 2018 François Kooman <fkooman@tuxed.net> - 1.3.3-0.3
- rebuilt

* Thu Dec 06 2018 François Kooman <fkooman@tuxed.net> - 1.3.3-0.2
- rebuilt

* Thu Dec 06 2018 François Kooman <fkooman@tuxed.net> - 1.3.3-0.1
- update to 1.3.3

* Wed Dec 05 2018 François Kooman <fkooman@tuxed.net> - 1.3.2-1
- update to 1.3.2

* Wed Nov 28 2018 François Kooman <fkooman@tuxed.net> - 1.3.1-1
- update to 1.3.1

* Thu Nov 22 2018 François Kooman <fkooman@tuxed.net> - 1.3.0-1
- update to 1.3.0

* Fri Nov 09 2018 François Kooman <fkooman@tuxed.net> - 1.2.3-1
- update to 1.2.3

* Wed Oct 10 2018 François Kooman <fkooman@tuxed.net> - 1.2.2-1
- update to 1.2.2

* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 1.2.1-1
- update to 1.2.1

* Sun Sep 09 2018 François Kooman <fkooman@tuxed.net> - 1.2.0-3
- merge dev and prod spec files in one
- cleanup requirements

* Sat Sep 08 2018 François Kooman <fkooman@tuxed.net> - 1.2.0-2
- only autoload compat libraries on older versions of Fedora/EL

* Wed Aug 15 2018 François Kooman <fkooman@tuxed.net> - 1.2.0-1
- update to 1.2.0

* Sun Aug 05 2018 François Kooman <fkooman@tuxed.net> - 1.1.17-1
- update to 1.1.17
- use PHPUnit 7 on supported platforms

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.1.16-4
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.1.16-3
- use fedora phpab template for generating autoloader

* Fri Jun 29 2018 François Kooman <fkooman@tuxed.net> - 1.1.16-2
- use release tarball instead of Git tarball
- verify GPG signature

* Wed Jun 06 2018 François Kooman <fkooman@tuxed.net> - 1.1.16-1
- update to 1.1.16

* Wed May 16 2018 François Kooman <fkooman@tuxed.net> - 1.1.15-1
- update to 1.1.15

* Mon May 14 2018 François Kooman <fkooman@tuxed.net> - 1.1.14-1
- update to 1.1.14

* Tue Apr 17 2018 François Kooman <fkooman@tuxed.net> - 1.1.13-1
- update to 1.1.13

* Thu Apr 05 2018 François Kooman <fkooman@tuxed.net> - 1.1.12-1
- update to 1.1.12

* Thu Mar 29 2018 François Kooman <fkooman@tuxed.net> - 1.1.11-1
- update to 1.1.11

* Fri Mar 16 2018 François Kooman <fkooman@tuxed.net> - 1.1.10-1
- update to 1.1.10

* Thu Mar 15 2018 François Kooman <fkooman@tuxed.net> - 1.1.9-1
- update to 1.1.9

* Tue Feb 27 2018 François Kooman <fkooman@tuxed.net> - 1.1.8-1
- update to 1.1.8

* Mon Feb 26 2018 François Kooman <fkooman@tuxed.net> - 1.1.7-1
- update to 1.1.7

* Fri Feb 23 2018 François Kooman <fkooman@tuxed.net> - 1.1.6-1
- update to 1.1.6

* Mon Feb 19 2018 François Kooman <fkooman@tuxed.net> - 1.1.5-1
- update to 1.1.5

* Sat Feb 17 2018 François Kooman <fkooman@tuxed.net> - 1.1.4-2
- depend on php-pdo

* Sat Feb 17 2018 François Kooman <fkooman@tuxed.net> - 1.1.4-1
- update to 1.1.4

* Thu Dec 14 2017 François Kooman <fkooman@tuxed.net> - 1.1.3-1
- update to 1.1.3

* Tue Dec 12 2017 François Kooman <fkooman@tuxed.net> - 1.1.2-1
- update to 1.1.2

* Thu Dec 07 2017 François Kooman <fkooman@tuxed.net> - 1.1.1-2
- use phpab to generate the classloader

* Mon Nov 27 2017 François Kooman <fkooman@tuxed.net> - 1.1.1-1
- update to 1.1.1

* Thu Nov 23 2017 François Kooman <fkooman@tuxed.net> - 1.1.0-1
- update to 1.1.0

* Mon Nov 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.8-1
- update to 1.0.8

* Wed Nov 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.7-1
- update to 1.0.7

* Thu Oct 26 2017 François Kooman <fkooman@tuxed.net> - 1.0.6-1
- update to 1.0.6

* Fri Oct 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.5-1
- update to 1.0.5

* Mon Oct 02 2017 François Kooman <fkooman@tuxed.net> - 1.0.4-1
- update to 1.0.4

* Mon Sep 11 2017 François Kooman <fkooman@tuxed.net> - 1.0.3-1
- update to 1.0.3

* Sun Sep 10 2017 François Kooman <fkooman@tuxed.net> - 1.0.2-1
- update to 1.0.2

* Thu Aug 17 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Fri Jun 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial release
