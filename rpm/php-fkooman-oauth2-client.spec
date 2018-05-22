%global commit0 901880724a1566c72caa8f5c13c064e949294bf7
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:           php-fkooman-oauth2-client
Version:        7.1.0
Release:        1%{?dist}
Summary:        Very simple OAuth 2.0 client

License:        MIT
URL:            https://github.com/fkooman/php-oauth2-client
Source0:        https://github.com/fkooman/php-oauth2-client/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildArch:      noarch

#        "php": ">=5.4",
BuildRequires:  php(language) >= 5.4.0
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-session": "*",
#        "ext-spl": "*",
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-session
BuildRequires:  php-spl
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": "^1|^2",
#        "psr/log": "^1.0",
#        "symfony/polyfill-php56": "^1"
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(psr/log)
BuildRequires:  php-composer(symfony/polyfill-php56)
BuildRequires:  %{_bindir}/phpab
BuildRequires:  %{_bindir}/phpunit

#        "php": ">=5.4",
Requires:       php(language) >= 5.4.0
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-session": "*",
#        "ext-spl": "*",
Requires:       php-curl
Requires:       php-date
Requires:       php-hash
Requires:       php-json
Requires:       php-pcre
Requires:       php-pdo
Requires:       php-session
Requires:       php-spl
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": "^1|^2",
#        "psr/log": "^1.0",
#        "symfony/polyfill-php56": "^1"
Requires:       php-composer(paragonie/constant_time_encoding)
Requires:       php-composer(paragonie/random_compat)
Requires:       php-composer(psr/log)
Requires:       php-composer(symfony/polyfill-php56)

Provides:       php-composer(fkooman/oauth2-client) = %{version}

%description
This is a very simple OAuth 2.0 client for integration in your own 
application. It has minimal dependencies, but still tries to be secure. 
The main purpose is to be compatible with PHP 5.4.

%prep
%autosetup -n php-oauth2-client-%{commit0}

%build
%{_bindir}/phpab -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
require_once '%{_datadir}/php/random_compat/autoload.php';
require_once '%{_datadir}/php/Symfony/Polyfill/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/OAuth/Client
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/OAuth/Client

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

%files
%license LICENSE
%doc composer.json CHANGES.md README.md
%dir %{_datadir}/php/fkooman
%dir %{_datadir}/php/fkooman/OAuth
%{_datadir}/php/fkooman/OAuth/Client

%changelog
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
