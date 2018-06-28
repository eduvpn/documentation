%global commit0 e6bc5442b29a14575a1b9caa1a9eb798bd3e119d
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:           php-eduvpn-common
Version:        1.1.0
Release:        0.1%{?dist}
Summary:        Common VPN library

License:        AGPLv3+
URL:            https://github.com/eduvpn/vpn-lib-common
Source0:        https://github.com/eduvpn/vpn-lib-common/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildArch:      noarch

#        "php": ">=5.4",
BuildRequires:  php(language) >= 5.4.0
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-filter": "*",
#        "ext-gettext": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-mbstring": "*",
#        "ext-pcre": "*",
#        "ext-spl": "*",
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-filter
BuildRequires:  php-gettext
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-mbstring
BuildRequires:  php-pcre
BuildRequires:  php-spl
BuildRequires:  php-composer(fedora/autoloader)
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

#        "php": ">=5.4",
Requires:       php(language) >= 5.4.0
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-filter": "*",
#        "ext-gettext": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-mbstring": "*",
#        "ext-pcre": "*",
#        "ext-spl": "*",
Requires:       php-curl
Requires:       php-date
Requires:       php-filter
Requires:       php-gettext
Requires:       php-hash
Requires:       php-json
Requires:       php-mbstring
Requires:       php-pcre
Requires:       php-spl
Requires:       php-composer(fedora/autoloader)
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

Provides:       php-composer(eduvpn/common) = %{version}

%description
Common VPN library.

%prep
%autosetup -n vpn-lib-common-%{commit0}

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('SURFnet\\VPN\\Common\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/fkooman/SeCookie/autoload.php',
    '%{_datadir}/php/password_compat/password.php',
    '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php',
    '%{_datadir}/php/random_compat/autoload.php',
    '%{_datadir}/php/Psr/Log/autoload.php',
    '%{_datadir}/php/Symfony/Polyfill/autoload.php',
    '%{_datadir}/php/Twig/Extensions/autoload.php',
    '%{_datadir}/php/Twig/autoload.php',
));
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/SURFnet/VPN/Common
cp -pr src/* %{buildroot}%{_datadir}/php/SURFnet/VPN/Common

%check
cat <<'AUTOLOAD' | tee tests/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('SURFnet\\VPN\\Common\\Tests\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{buildroot}/%{_datadir}/php/SURFnet/VPN/Common/autoload.php',
));
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

%files
%license LICENSE LICENSE.spdx
%doc composer.json CHANGES.md README.md
%dir %{_datadir}/php/SURFnet
%dir %{_datadir}/php/SURFnet/VPN
%{_datadir}/php/SURFnet/VPN/Common

%changelog
* Mon Sep 18 2017 François Kooman <fkooman@tuxed.net> - 1.1.0-0.1
- update to 1.1.0

* Mon Sep 11 2017 François Kooman <fkooman@tuxed.net> - 1.0.3-1
- update to 1.0.3

* Sun Sep 10 2017 François Kooman <fkooman@tuxed.net> - 1.0.2-1
- update to 1.0.2

* Thu Aug 17 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Fri Jun 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial release
