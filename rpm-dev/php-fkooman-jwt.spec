%global commit0 60a393dbd7af4505cf3a90e2391aa9a2febebdbb

Name:           php-fkooman-jwt
Version:        0.1.0
Release:        0.8%{?dist}
Summary:        JWT Library

License:        MIT
URL:            https://git.tuxed.net/fkooman/php-jwt
Source0:        https://git.tuxed.net/fkooman/php-jwt/snapshot/php-jwt-%{commit0}.tar.xz

BuildArch:      noarch

#        "php": ">= 5.4",
BuildRequires:  php(language) >= 5.4.0
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-openssl": "*",
#        "ext-spl": "*",
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-openssl
BuildRequires:  php-spl
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": ">=1",
#        "symfony/polyfill-php56": "^1"
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(symfony/polyfill-php56)
%if 0%{?rhel} < 8
BuildRequires:  php-composer(paragonie/random_compat)
%endif

BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpab

%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
BuildRequires:  phpunit7
%global phpunit %{_bindir}/phpunit7
%else
BuildRequires:  phpunit
%global phpunit %{_bindir}/phpunit
%endif

#        "php": ">= 5.4",
Requires:  php(language) >= 5.4.0
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-openssl": "*",
#        "ext-spl": "*",
Requires:  php-hash
Requires:  php-json
Requires:  php-openssl
Requires:  php-spl
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": ">=1",
#        "symfony/polyfill-php56": "^1"
Requires:  php-composer(paragonie/constant_time_encoding)
Requires:  php-composer(symfony/polyfill-php56)
%if 0%{?rhel} < 8
Requires:  php-composer(paragonie/random_compat)
%endif

Provides:  php-composer(fkooman/jwt) = %{version}

%description
JWT Library.

%prep
%autosetup -n php-jwt-%{commit0}

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php',
    '%{_datadir}/php/Symfony/Polyfill/autoload.php',
));
\Fedora\Autoloader\Dependencies::optional(array(
    '%{_datadir}/php/random_compat/autoload.php'
));
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/Jwt
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/Jwt

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{phpunit} tests --verbose --bootstrap=tests/autoload.php

%files
%license LICENSE
%doc composer.json CHANGES.md README.md
%dir %{_datadir}/php/fkooman
%{_datadir}/php/fkooman/Jwt

%changelog
* Fri Aug 24 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-0.8
- rebuilt

* Thu Aug 23 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-0.7
- rebuilt

* Thu Aug 23 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-0.6
- rebuilt

* Thu Aug 23 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-0.5
- rebuilt

* Wed Aug 22 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-0.4
- rebuilt

* Tue Aug 21 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-0.3
- rebuilt

* Mon Aug 20 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-0.2
- remove paragonie/random_compat

* Mon Aug 20 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-0.1
- initial package
