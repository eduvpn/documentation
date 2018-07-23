%global commit0 762fedc0783ff58b6cef5557ed420ff1e8a73422

Name:       php-voot2-provider
Version:    0.2.1
Release:    3%{?dist}
Summary:    VOOT 2.0 Provider

Group:      Applications/Internet
License:    MIT

URL:        https://git.tuxed.net/fkooman/php-voot2-provider
Source0:    https://git.tuxed.net/fkooman/php-voot2-provider/snapshot/php-voot2-provider-%{commit0}.tar.xz
Source1:    %{name}-httpd.conf
Patch0:     %{name}-autoload.patch

BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpunit
BuildRequires:  %{_bindir}/phpab
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-ldap": "*",
#        "php": ">= 5.4",
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-ldap
#        "psr/log": "^1",
#        "symfony/polyfill-php56": "^1"
BuildRequires:  php-composer(psr/log)
BuildRequires:  php-composer(symfony/polyfill-php56)
BuildRequires:  php-fedora-autoloader-devel

#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-ldap": "*",
#        "php": ">= 5.4",
Requires:   php(language) >= 5.4.0
Requires:   php-hash
Requires:   php-json
Requires:   php-ldap
#        "psr/log": "^1",
#        "symfony/polyfill-php56": "^1"
Requires:  php-composer(psr/log)
Requires:  php-composer(symfony/polyfill-php56)
Requires:  php-fedora-autoloader

%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif

%description
Simple implementation of the VOOT 2.0 protocol written in PHP.

%prep
%setup -qn php-voot2-provider-%{commit0}
%patch0 -p1

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/Psr/Log/autoload.php';
require_once '%{_datadir}/php/Symfony/Polyfill/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/php/fkooman/Voot
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/Voot
cp -pr web %{buildroot}%{_datadir}/%{name}

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/config.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config

install -m 0644 -D -p %{SOURCE1} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

%check
%{_bindir}/phpab -t fedora -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/config.php
%dir %{_datadir}/php/fkooman
%{_datadir}/php/fkooman/Voot
%{_datadir}/%{name}/web
%{_datadir}/%{name}/config
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE

%changelog
* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 0.2.1-3
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 0.2.1-2
- use fedora phpab template

* Fri Jun 01 2018 François Kooman <fkooman@tuxed.net> - 0.2.1-1
- update to 0.2.1

* Fri Jun 01 2018 François Kooman <fkooman@tuxed.net> - 0.2.0-1
- update to 0.2.0

* Fri Jun 01 2018 François Kooman <fkooman@tuxed.net> - 0.1.2-1
- update to 0.1.2

* Thu May 31 2018 François Kooman <fkooman@tuxed.net> - 0.1.1-1
- update to 0.1.1

* Thu May 31 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-1
- initial packag
