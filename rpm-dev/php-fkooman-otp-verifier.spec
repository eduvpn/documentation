%global commit0 2f5c4770a76cf1f4c913a35977108314b3af9ade

Name:           php-fkooman-otp-verifier
Version:        0.2.0
Release:        3%{?dist}
Summary:        OTP Verification Library

License:        MIT
URL:            https://git.tuxed.net/fkooman/php-otp-verifier
Source0:        https://git.tuxed.net/fkooman/php-otp-verifier/snapshot/php-otp-verifier-%{commit0}.tar.xz

BuildArch:      noarch

#        "php": ">= 5.4",
BuildRequires:  php(language) >= 5.4.0
#        "ext-date": "*",
#        "ext-hash": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
BuildRequires:  php-date
BuildRequires:  php-hash
BuildRequires:  php-pdo
BuildRequires:  php-spl
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": ">=1",
#        "symfony/polyfill-php56": "^1"
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(symfony/polyfill-php56)
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpab
BuildRequires:  %{_bindir}/phpunit

#        "php": ">= 5.4",
Requires:  php(language) >= 5.4.0
#        "ext-date": "*",
#        "ext-hash": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
Requires:  php-date
Requires:  php-hash
Requires:  php-pdo
Requires:  php-spl
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": ">=1",
#        "symfony/polyfill-php56": "^1"
Requires:  php-composer(paragonie/constant_time_encoding)
Requires:  php-composer(paragonie/random_compat)
Requires:  php-composer(symfony/polyfill-php56)

Provides:       php-composer(fkooman/otp-verifier) = %{version}

%description
OTP Verification Library

%prep
%autosetup -n php-otp-verifier-%{commit0}

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
require_once '%{_datadir}/php/random_compat/autoload.php';
require_once '%{_datadir}/php/Symfony/Polyfill/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/Otp
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/Otp

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

%files
%license LICENSE
%doc composer.json CHANGES.md README.md
%dir %{_datadir}/php/fkooman
%{_datadir}/php/fkooman/Otp

%changelog
* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 0.2.0-3
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 0.2.0-2
- use fedora phpab template

* Fri Jul 20 2018 François Kooman <fkooman@tuxed.net> - 0.2.0-1
- update to 0.2.0

* Mon Jul 16 2018 François Kooman <fkooman@tuxed.net> - 0.1.1-1
- update to 0.1.1

* Tue Jul 10 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-0.1
- initial package
