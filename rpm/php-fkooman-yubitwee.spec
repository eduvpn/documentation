%global commit0 bf8e5f1106b11a3f50b1113d3db6609294a488da
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:           php-fkooman-yubitwee
Version:        1.0.1
Release:        2%{?dist}
Summary:        YubiKey OTP Validator library

License:        MIT
URL:            https://github.com/fkooman/php-yubitwee
Source0:        https://github.com/fkooman/php-yubitwee/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildArch:      noarch

BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-hash
BuildRequires:  php-libsodium
BuildRequires:  php-pcre
BuildRequires:  php-spl
BuildRequires:  php-composer(fedora/autoloader)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  %{_bindir}/phpunit

Requires:       php(language) >= 5.4.0
Requires:       php-curl
Requires:       php-date
Requires:       php-hash
Requires:       php-libsodium
Requires:       php-pcre
Requires:       php-spl
Requires:       php-composer(fedora/autoloader)
Requires:       php-composer(paragonie/constant_time_encoding)

Provides:       php-composer(fkooman/yubitwee) = %{version}

%description
A very simple, secure YubiKey OTP Validator with pluggable HTTP client.

%prep
%autosetup -n php-yubitwee-%{commit0}

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('fkooman\\YubiTwee\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php',
));
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/YubiTwee
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/YubiTwee

%check
cat <<'AUTOLOAD' | tee tests/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('fkooman\\YubiTwee\\Tests\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{buildroot}/%{_datadir}/php/fkooman/YubiTwee/autoload.php',
));
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

%files
%license LICENSE
%doc composer.json CHANGES.md README.md
%dir %{_datadir}/php/fkooman
%{_datadir}/php/fkooman/YubiTwee

%changelog
* Wed Aug 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-2
- rework spec, to align it with practices document

* Thu Jun 01 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1
- license changed to MIT

* Tue Apr 11 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
