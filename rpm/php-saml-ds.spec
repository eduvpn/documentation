Name:       php-saml-ds
Version:    1.0.11
Release:    3%{?dist}
Summary:    SAML Discovery Service

Group:      Applications/Internet
License:    ASL2.0

URL:        https://software.tuxed.net/php-saml-ds
Source0:    https://software.tuxed.net/php-saml-ds/files/php-saml-ds-%{version}.tar.xz
Source1:    https://software.tuxed.net/php-saml-ds/files/php-saml-ds-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
Source3:    %{name}-httpd.conf
Patch0:     %{name}-autoload.patch

BuildArch:  noarch

BuildRequires:  gnupg2
BuildRequires:  %{_bindir}/phpunit
BuildRequires:  %{_bindir}/phpab
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-curl
BuildRequires:  php-filter
BuildRequires:  php-pecl-imagick
BuildRequires:  php-json
BuildRequires:  php-pcre
BuildRequires:  php-spl
BuildRequires:  php-xml
BuildRequires:  php-composer(twig/twig) < 2
BuildRequires:  php-composer(fkooman/secookie)

Requires:   php(language) >= 5.4.0
Requires:   php-curl
Requires:   php-filter
Requires:   php-pecl-imagick
Requires:   php-json
Requires:   php-pcre
Requires:   php-spl
Requires:   php-xml
Requires:   php-composer(twig/twig) < 2
Requires:   php-composer(fkooman/secookie)
%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif

%description
SAML Discovery Service written in PHP.

%prep
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn php-saml-ds-%{version}
%patch0 -p1

%build
%{_bindir}/phpab -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/Twig/autoload.php';
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

%post
# remove template cache if it is there
rm -rf %{_localstatedir}/lib/%{name}/tpl/* >/dev/null 2>/dev/null || :

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

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
