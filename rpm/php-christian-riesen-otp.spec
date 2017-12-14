%global composer_vendor         christian-riesen
%global composer_project        otp
%global composer_namespace      Otp

%global github_owner            ChristianRiesen
%global github_name             otp

%global commit0 a6c095fb36f6404aa1078d2dfd717aa95c1b5267
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:       php-%{composer_vendor}-%{composer_project}
Version:    2.5.0
Release:    2%{?dist}
Summary:    One Time Passwords

Group:      System Environment/Libraries
License:    MIT

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildArch:  noarch

BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-date
BuildRequires:  php-hash
BuildRequires:  php-spl
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(symfony/polyfill-php56)

BuildRequires:  %{_bindir}/phpunit
BuildRequires:  %{_bindir}/phpab

Requires:   php(language) >= 5.4.0
Requires:   php-date
Requires:   php-hash
Requires:   php-spl
Requires:   php-composer(paragonie/random_compat)
Requires:   php-composer(paragonie/constant_time_encoding)
Requires:   php-composer(symfony/polyfill-php56)

Provides:   php-composer(%{composer_vendor}/%{composer_project}) = %{version}

%description
Implements hotp according to RFC4226 and totp according to RFC6238 (only sha1 
algorithm).

%prep
%setup -n %{github_name}-%{commit0}

%build
%{_bindir}/phpab -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/Symfony/Polyfill/autoload.php';
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
require_once '%{_datadir}/php/random_compat/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/%{composer_namespace}
cp -pr src/* %{buildroot}%{_datadir}/php/%{composer_namespace}/

%check
phpunit --no-coverage --verbose --bootstrap=src/autoload.php

%files
%{_datadir}/php/%{composer_namespace}
%doc README.md composer.json
%license LICENSE

%changelog
* Thu Dec 14 2017 François Kooman <fkooman@tuxed.net> - 2.5.0-2
- add missing polyfill autoloader

* Thu Dec 14 2017 François Kooman <fkooman@tuxed.net> - 2.5.0-1
- update to 2.5.0

* Thu Dec 07 2017 François Kooman <fkooman@tuxed.net> - 2.4.0-2
- use phpab to generate the classloader

* Thu Mar 16 2017 François Kooman <fkooman@tuxed.net> - 2.4.0-1
- update to 2.4.0

* Tue Jan 17 2017 François Kooman <fkooman@tuxed.net> - 2.3.0-1
- update to 2.3.0

* Fri Nov 25 2016 François Kooman <fkooman@tuxed.net> - 2.2.0-4
- more spec cleanup

* Tue Nov 15 2016 François Kooman <fkooman@tuxed.net> - 2.2.0-3
- cleanup spec

* Thu Oct 13 2016 François Kooman <fkooman@tuxed.net> - 2.2.0-2
- do not depend on libsodium any longer

* Wed Sep 14 2016 François Kooman <fkooman@tuxed.net> - 2.2.0-1
- update to 2.2.0

* Fri Apr 22 2016 François Kooman <fkooman@tuxed.net> - 1.4.3-1
- initial package
