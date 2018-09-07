%global commit0 03af3fbe32c0e9255c1d5bc6cee3ee79f4a57abd

Name:           php-LC-openvpn-connection-manager
Version:        1.0.2
Release:        4%{?dist}
Summary:        Manage client connections to OpenVPN processes

License:        MIT
URL:            https://git.tuxed.net/LC/php-openvpn-connection-manager
Source0:        https://git.tuxed.net/LC/php-openvpn-connection-manager/snapshot/php-openvpn-connection-manager-%{commit0}.tar.xz

BuildArch:      noarch

#        "php": ">=5.4",
BuildRequires:  php(language) >= 5.4.0
#        "psr/log": "^1.0",
BuildRequires:  php-composer(psr/log)
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpab
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
BuildRequires:  phpunit7
%global phpunit %{_bindir}/phpunit7
%else
BuildRequires:  phpunit
%global phpunit %{_bindir}/phpunit
%endif

#        "php": ">=5.4",
Requires:       php(language) >= 5.4.0
#        "psr/log": "^1.0",
Requires:       php-composer(psr/log)

Provides:       php-composer(LC/openvpn-connection-manager) = %{version}

%description
Simple library written in PHP to manage client connections to OpenVPN processes 
through the OpenVPN management socket.

%prep
%autosetup -n php-openvpn-connection-manager-%{commit0}

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/Psr/Log/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/LC/OpenVpn
cp -pr src/* %{buildroot}%{_datadir}/php/LC/OpenVpn

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{phpunit} tests --verbose --bootstrap=tests/autoload.php

%files
%license LICENSE
%doc composer.json CHANGES.md README.md
%dir %{_datadir}/php/LC
%{_datadir}/php/LC/OpenVpn

%changelog
* Fri Sep 07 2018 François Kooman <fkooman@tuxed.net> - 1.0.2-4
- rebuilt

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.0.2-3
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 1.0.2-2
- use fedora phpab template

* Wed Jun 13 2018 François Kooman <fkooman@tuxed.net> - 1.0.2-1
- update to 1.0.2

* Thu Jun 07 2018 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Wed Jun 06 2018 François Kooman <fkooman@tuxed.net> - 1.0.0-2
- update upstream source URL

* Tue Jun 05 2018 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
