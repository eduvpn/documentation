%global git 7b60cc2be26841189987c5c08247ed37b863939b

Name:       php-saml-ds
Version:    1.1.0
Release:    0.2%{?dist}
Summary:    SAML Discovery Service

Group:      Applications/Internet
License:    ASL2.0

URL:        https://software.tuxed.net/php-saml-ds
%if %{defined git}
Source0:    https://git.tuxed.net/fkooman/php-saml-ds/snapshot/php-saml-ds-%{git}.tar.xz
%else
Source0:    https://software.tuxed.net/php-saml-ds/files/php-saml-ds-%{version}.tar.xz
Source1:    https://software.tuxed.net/php-saml-ds/files/php-saml-ds-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif
Source3:    %{name}-httpd.conf
Patch0:     %{name}-autoload.patch

BuildArch:  noarch

BuildRequires:  gnupg2
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpab
#    "require-dev": {
#        "phpunit/phpunit": "^4|^5|^6|^7"
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
#        "ext-filter": "*",
#        "ext-imagick": "*",
#        "ext-json": "*",
#        "ext-pcre": "*",
#        "ext-spl": "*",
#        "ext-xml": "*",
#        "fkooman/secookie": "^2",
#        "php": ">=5.4.0"
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-curl
BuildRequires:  php-filter
BuildRequires:  php-pecl-imagick
BuildRequires:  php-json
BuildRequires:  php-pcre
BuildRequires:  php-spl
BuildRequires:  php-xml
BuildRequires:  php-composer(fkooman/secookie)

%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif
#    "require": {
#        "ext-curl": "*",
#        "ext-filter": "*",
#        "ext-imagick": "*",
#        "ext-json": "*",
#        "ext-pcre": "*",
#        "ext-spl": "*",
#        "ext-xml": "*",
#        "fkooman/secookie": "^2",
#        "php": ">=5.4.0"
#    },
Requires:   php(language) >= 5.4.0
Requires:   php-cli
Requires:   php-curl
Requires:   php-filter
Requires:   php-pecl-imagick
Requires:   php-json
Requires:   php-pcre
Requires:   php-spl
Requires:   php-xml
Requires:   php-composer(fkooman/secookie)

%description
SAML Discovery Service written in PHP.

%prep
%if %{defined git}
%setup -qn php-saml-ds-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn php-saml-ds-%{version}
%endif
%patch0 -p1

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/fkooman/SeCookie/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/php/fkooman/SAML/DS
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/SAML/DS
cp -pr web views %{buildroot}%{_datadir}/%{name}
install -m 0755 -D -p bin/generate.php %{buildroot}%{_bindir}/%{name}-generate

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/config.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config

mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
ln -s ../../../var/lib/%{name} %{buildroot}%{_datadir}/%{name}/data

install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{phpunit} tests --verbose --bootstrap=tests/autoload.php

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/config.php
%{_bindir}/*
%dir %{_datadir}/php/fkooman
%dir %{_datadir}/php/fkooman/SAML
%{_datadir}/php/fkooman/SAML/DS
%{_datadir}/%{name}/web
%{_datadir}/%{name}/data
%{_datadir}/%{name}/views
%{_datadir}/%{name}/config
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/%{name}
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE

%changelog
* Sun Dec 16 2018 François Kooman <fkooman@tuxed.net> - 1.1.0-0.2
- rebuilt

* Thu Dec 13 2018 François Kooman <fkooman@tuxed.net> - 1.1.0-0.1
- update to 1.1.0
- remove Twig dependency

* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 1.0.12-4
- merge dev and prod spec files in one
- cleanup requirements

* Sat Sep 08 2018 François Kooman <fkooman@tuxed.net> - 1.0.12-3
- move some stuff around to make it consistent with other spec files
- add composer.json comments to (Build)Requires

* Sun Aug 05 2018 François Kooman <fkooman@tuxed.net> - 1.0.12-2
- use phpunit7 on supported platforms

* Fri Aug 03 2018 François Kooman <fkooman@tuxed.net> - 1.0.12-1
- update to 1.0.12

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.0.11-5
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.0.11-4
- use fedora phpab template for generating autoloader

* Thu Jun 28 2018 François Kooman <fkooman@tuxed.net> - 1.0.11-3
- use release tarball instead of Git tarball
- verify GPG signature

* Fri Jun 01 2018 François Kooman <fkooman@tuxed.net> - 1.0.11-2
- update upstream URL to git.tuxed.net

* Sun Apr 29 2018 François Kooman <fkooman@tuxed.net> - 1.0.11-1
- update to 1.0.11

* Mon Jan 22 2018 François Kooman <fkooman@tuxed.net> - 1.0.10-1
- update to 1.0.10

* Wed Dec 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.9-1
- update to 1.0.9
- cleanup autoloader

* Thu Dec 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.8-2
- use phpab to generate the classloader

* Sun Oct 01 2017 François Kooman <fkooman@tuxed.net> - 1.0.8-1
- update to 1.0.8

* Fri Sep 29 2017 François Kooman <fkooman@tuxed.net> - 1.0.7-1
- update to 1.0.7

* Sun Sep 10 2017 François Kooman <fkooman@tuxed.net> - 1.0.6-1
- update to 1.0.6

* Thu Aug 17 2017 François Kooman <fkooman@tuxed.net> - 1.0.5-1
- update to 1.0.5

* Mon Aug 14 2017 François Kooman <fkooman@tuxed.net> - 1.0.4-1
- update to 1.0.4

* Tue Aug 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.3-3
- update httpd snippet

* Mon Aug 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.3-2
- remove the tpl directory when upgrading

* Mon Aug 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.3-1
- update to 1.0.3

* Fri Jul 28 2017 François Kooman <fkooman@tuxed.net> - 1.0.2-1
- update to 1.0.2

* Wed Jul 19 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1
- rework autoloader

* Fri Jun 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
