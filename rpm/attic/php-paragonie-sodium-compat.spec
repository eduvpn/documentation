%global commit0 6b3a59ef127445564a00e261eb1e960b6292f494
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:           php-paragonie-sodium-compat
Version:        1.3.1
Release:        1%{?dist}
Summary:        Pure PHP polyfill for ext/sodium

License:        ISC
URL:            https://github.com/paragonie/sodium_compat
Source0:        %{name}-%{version}-%{commit0}.tar.gz

BuildArch:      noarch

BuildRequires:  php(language) >= 5.2.4
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  %{_bindir}/phpunit

Requires:       php(language) >= 5.2.4  
Requires:       php-composer(paragonie/random_compat)

Provides:       php-composer(paragonie/sodium_compat) = %{version}

%description
Sodium Compat is a pure PHP polyfill for the Sodium cryptography library 
(libsodium), a core extension in PHP 7.2.0+ and otherwise available in PECL.

%prep
%autosetup -n sodium_compat-%{commit0}

%build

%install
mkdir -p %{buildroot}%{_datadir}/php/sodium_compat
cp -pr autoload.php lib src namespaced %{buildroot}%{_datadir}/php/sodium_compat

%check
pwd
cat <<'AUTOLOAD' | tee tests/autoload.php
<?php
require_once '%{_datadir}/php/random_compat/autoload.php';
require_once '%{buildroot}%{_datadir}/php/sodium_compat/autoload.php';
AUTOLOAD

%{_bindir}/phpunit tests --bootstrap=tests/autoload.php

%files
%license LICENSE
%doc composer.json README.md
%{_datadir}/php/sodium_compat

%changelog
* Sat Sep 30 2017 François Kooman <fkooman@tuxed.net> - 1.3.1-1
- update to 1.3.1

* Wed Aug 30 2017 François Kooman <fkooman@tuxed.net> - 1.2.0-1
- initial package
