%global composer_namespace      SURFnet/VPN/Common

%global github_owner            eduvpn
%global github_name             vpn-lib-common
%global github_commit           0aa297d77d147ed7cd20197f8be69394317135a3
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       vpn-lib-common
Version:    1.1.1
Release:    2%{?dist}
Summary:    Common VPN library
Group:      System Environment/Libraries
License:    AGPLv3+
URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz
BuildArch:  noarch

#        "php": ">=5.4",
BuildRequires:  php(language) >= 5.4.0
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-filter": "*",
#        "ext-gettext": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-ldap": "*",
#        "ext-mbstring": "*",
#        "ext-pcre": "*",
#        "ext-spl": "*",
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-filter
BuildRequires:  php-gettext
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-ldap
BuildRequires:  php-mbstring
BuildRequires:  php-pcre
BuildRequires:  php-spl
#        "fkooman/secookie": "^2",
#        "ircmaxell/password-compat": "^1",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": "^1|^2",
#        "psr/log": "^1.0",
#        "symfony/polyfill-php56": "^1",
#        "twig/extensions": "^1",
#        "twig/twig": "^1"
BuildRequires:  php-composer(fkooman/secookie)
BuildRequires:  php-composer(ircmaxell/password-compat)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(psr/log)
BuildRequires:  php-composer(symfony/polyfill-php56)
BuildRequires:  php-composer(twig/extensions) < 2.0
BuildRequires:  php-composer(twig/twig) < 2.0
BuildRequires:  %{_bindir}/phpunit
BuildRequires:  %{_bindir}/phpab

#        "php": ">=5.4",
Requires:       php(language) >= 5.4.0
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-filter": "*",
#        "ext-gettext": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-ldap": "*",
#        "ext-mbstring": "*",
#        "ext-pcre": "*",
#        "ext-spl": "*",
Requires:       php-curl
Requires:       php-date
Requires:       php-filter
Requires:       php-gettext
Requires:       php-hash
Requires:       php-json
Requires:       php-ldap
Requires:       php-mbstring
Requires:       php-pcre
Requires:       php-spl
#        "fkooman/secookie": "^2",
#        "ircmaxell/password-compat": "^1",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": "^1|^2",
#        "psr/log": "^1.0",
#        "symfony/polyfill-php56": "^1",
#        "twig/extensions": "^1",
#        "twig/twig": "^1"
Requires:       php-composer(fkooman/secookie)
Requires:       php-composer(ircmaxell/password-compat)
Requires:       php-composer(paragonie/constant_time_encoding)
Requires:       php-composer(paragonie/random_compat)
Requires:       php-composer(psr/log)
Requires:       php-composer(symfony/polyfill-php56)
Requires:       php-composer(twig/extensions) < 2.0
Requires:       php-composer(twig/twig) < 2.0

%description
Common VPN library.

%prep
%setup -qn %{github_name}-%{github_commit}

%build
%{_bindir}/phpab -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/fkooman/SeCookie/autoload.php';
require_once '%{_datadir}/php/password_compat/password.php';
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
require_once '%{_datadir}/php/random_compat/autoload.php';
require_once '%{_datadir}/php/Psr/Log/autoload.php';
require_once '%{_datadir}/php/Symfony/Polyfill/autoload.php';
require_once '%{_datadir}/php/Twig/Extensions/autoload.php';
require_once '%{_datadir}/php/Twig/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/%{composer_namespace}
cp -pr src/* %{buildroot}%{_datadir}/php/%{composer_namespace}

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

%files
%dir %{_datadir}/php/SURFnet
%dir %{_datadir}/php/SURFnet/VPN
%{_datadir}/php/%{composer_namespace}
%doc README.md composer.json CHANGES.md
%license LICENSE

%changelog
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
