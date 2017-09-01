%global commit0 9f63939f14ed1206a0b011d4735d4ed75163f660
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:           php-fkooman-secookie
Version:        1.0.2
Release:        2%{?dist}
Summary:        Secure Cookie and Session library for PHP

License:        MIT
URL:            https://github.com/fkooman/php-secookie
Source0:        https://github.com/fkooman/php-secookie/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildArch:      noarch

BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-date
BuildRequires:  php-session
BuildRequires:  php-composer(fedora/autoloader)
BuildRequires:  %{_bindir}/phpunit

Requires:       php(language) >= 5.4.0
Requires:       php-date
Requires:       php-session
Requires:       php-composer(fedora/autoloader)

Provides:       php-composer(fkooman/secookie) = %{version}

%description
Secure Cookie and Session library for PHP.

%prep
%autosetup -n php-secookie-%{commit0}

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('fkooman\\SeCookie\\', __DIR__);
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/SeCookie
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/SeCookie

%check
cat <<'AUTOLOAD' | tee tests/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('fkooman\\SeCookie\\Tests\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{buildroot}/%{_datadir}/php/fkooman/SeCookie/autoload.php',
));
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

%files
%license LICENSE
%doc README.md composer.json CHANGES.md
%dir %{_datadir}/php/fkooman
%{_datadir}/php/fkooman/SeCookie

%changelog
* Fri Sep 01 2017 François Kooman <fkooman@tuxed.net> - 1.0.2-2
- rework spec, to align it with practices document

* Tue Aug 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.2-1
- update to 1.0.2

* Mon Aug 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Fri Jun 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-2
- remove old changelog entries

* Fri Jun 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
