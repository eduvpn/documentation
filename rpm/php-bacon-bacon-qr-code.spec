%global composer_vendor         bacon
%global composer_project        bacon-qr-code
%global composer_namespace      BaconQrCode

%global github_owner            Bacon
%global github_name             BaconQrCode
%global github_commit           5a91b62b9d37cee635bbf8d553f4546057250bee
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       php-%{composer_vendor}-%{composer_project}
Version:    1.0.3
Release:    1%{?dist}
Summary:    QR Code Generator for PHP 

Group:      System Environment/Libraries
License:    BSD-2-Clause

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz

BuildArch:  noarch

BuildRequires:  php(language) >= 5.3.3
BuildRequires:  php-gd
BuildRequires:  php-iconv
BuildRequires:  %{_bindir}/phpunit
BuildRequires:  php-composer(fedora/autoloader)

Requires:   php(language) >= 5.3.3
Requires:   php-gd
Requires:   php-iconv
Requires:   php-composer(fedora/autoloader)

Provides:   php-composer(%{composer_vendor}/%{composer_project}) = %{version}

%description
BaconQrCode is a QR code generator for PHP.

%prep
%setup -qn %{github_name}-%{github_commit} 

%build
cat <<'AUTOLOAD' | tee src/%{composer_namespace}/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr0('BaconQrCode\\', dirname(__DIR__));
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php
cp -pr src/* %{buildroot}%{_datadir}/php

%check
phpunit --bootstrap=%{buildroot}/%{_datadir}/php/%{composer_namespace}/autoload.php tests

%files
%{_datadir}/php/%{composer_namespace}
%doc README.md composer.json
%license LICENSE

%changelog
* Tue Oct 24 2017 François Kooman <fkooman@tuxed.net> - 1.0.3-1
- update to 1.0.3
- remove upstreamed patch

* Fri Mar 17 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-6
- rebuilt

* Sat Nov 26 2016 François Kooman <fkooman@tuxed.net> - 1.0.1-5
- fix building with PHP 7.1

* Fri Nov 25 2016 François Kooman <fkooman@tuxed.net> - 1.0.1-4
- remove defattr

* Fri Nov 25 2016 François Kooman <fkooman@tuxed.net> - 1.0.1-3
- cleanup spec file

* Tue Nov 15 2016 François Kooman <fkooman@tuxed.net> - 1.0.1-2
- update spec

* Mon Feb 15 2016 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- initial package
