#global git 4cabcd6e49633b4ffcffb6f5978b90b7996de866

Name:           php-fkooman-secookie
Version:        2.0.1
Release:        7%{?dist}
Summary:        Secure Cookie and Session library for PHP

License:        MIT
URL:            https://software.tuxed.net/php-secookie
%if %{defined git}
Source0:        https://git.tuxed.net/fkooman/php-secookie/snapshot/php-secookie-%{git}.tar.xz
%else
Source0:        https://software.tuxed.net/php-secookie/files/php-secookie-%{version}.tar.xz
Source1:        https://software.tuxed.net/php-secookie/files/php-secookie-%{version}.tar.xz.asc
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
#        "ext-session": "*",
#        "php": ">=5.4"
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-date
BuildRequires:  php-session

#    "require": {
#        "ext-date": "*",
#        "ext-session": "*",
#        "php": ">=5.4"
#    },
Requires:       php(language) >= 5.4.0
Requires:       php-date
Requires:       php-session

Provides:       php-composer(fkooman/secookie) = %{version}

%description
Secure Cookie and Session library for PHP.

%prep
%if %{defined git}
%autosetup -n php-secookie-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%autosetup -n php-secookie-%{version}
%endif

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

%{phpunit} tests --verbose --bootstrap=tests/autoload.php

%files
%license LICENSE
%doc README.md composer.json CHANGES.md
%dir %{_datadir}/php/fkooman
%{_datadir}/php/fkooman/SeCookie

%changelog
* Sun Sep 09 2018 François Kooman <fkooman@tuxed.net> - 2.0.1-7
- merge dev and prod spec files in one
- cleanup requirements

* Sat Sep 08 2018 François Kooman <fkooman@tuxed.net> - 2.0.1-6
- add composer.json comments to (Build)Requires
- move some stuff around to make it consistent with other spec files

* Sun Aug 05 2018 François Kooman <fkooman@tuxed.net> - 2.0.1-5
- use phpunit7 on supported platforms

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 2.0.1-4
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 2.0.1-3
- use fedora phpab template for generating autoloader

* Thu Jun 28 2018 François Kooman <fkooman@tuxed.net> - 2.0.1-2
- use release tarball instead of Git tarball
- verify GPG signature

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
