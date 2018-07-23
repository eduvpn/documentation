%global commit0 4cabcd6e49633b4ffcffb6f5978b90b7996de866

Name:           php-fkooman-secookie
Version:        2.0.1
Release:        2%{?dist}
Summary:        Secure Cookie and Session library for PHP

License:        MIT
URL:            https://git.tuxed.net/fkooman/php-secookie
Source0:        https://git.tuxed.net/fkooman/php-secookie/snapshot/php-secookie-%{commit0}.tar.xz

BuildArch:      noarch

BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-date
BuildRequires:  php-session
BuildRequires:  %{_bindir}/phpunit
BuildRequires:  %{_bindir}/phpab

Requires:       php(language) >= 5.4.0
Requires:       php-date
Requires:       php-session

Provides:       php-composer(fkooman/secookie) = %{version}

%description
Secure Cookie and Session library for PHP.

%prep
%autosetup -n php-secookie-%{commit0}

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/SeCookie
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/SeCookie

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

%files
%license LICENSE
%doc README.md composer.json CHANGES.md
%dir %{_datadir}/php/fkooman
%{_datadir}/php/fkooman/SeCookie

%changelog
* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 2.0.1-2
- use fedora phpab template

* Sat Jun 02 2018 François Kooman <fkooman@tuxed.net> - 2.0.1-1
- update to 2.0.1

* Fri Jun 01 2018 François Kooman <fkooman@tuxed.net> - 2.0.0-3
- update upstream URL to git.tuxed.net

* Thu Dec 07 2017 François Kooman <fkooman@tuxed.net> - 2.0.0-2
- use phpab to generate the classloader

* Sun Sep 10 2017 François Kooman <fkooman@tuxed.net> - 2.0.0-1
- update to 2.0.0

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
