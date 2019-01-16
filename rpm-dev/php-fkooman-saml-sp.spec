%global git 9cab92045cbd449a795cf5fe5dd6e715bf43c6c0

Name:           php-fkooman-saml-sp
Version:        0.0.0
Release:        0.17%{?dist}
Summary:        SAML Service Provider library

License:        MIT
URL:            https://software.tuxed.net/php-saml-sp
%if %{defined git}
Source0:        https://git.tuxed.net/fkooman/php-saml-sp/snapshot/php-saml-sp-%{git}.tar.xz
%else
Source0:        https://software.tuxed.net/php-saml-sp/files/php-saml-sp-%{version}.tar.xz
Source1:        https://software.tuxed.net/php-saml-sp/files/php-saml-sp-%{version}.tar.xz.asc
Source2:        gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
%endif

BuildArch:      noarch

BuildRequires:  gnupg2
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpab
#    "require-dev": {
#        "phpunit/phpunit": "^4|^5|^6|^7",
#    },
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
BuildRequires:  phpunit7
%global phpunit %{_bindir}/phpunit7
%else
BuildRequires:  phpunit
%global phpunit %{_bindir}/phpunit
%endif
#    "require": {
#        "ext-date": "*",
#        "ext-dom": "*",
#        "ext-hash": "*",
#        "ext-libxml": "*",
#        "ext-openssl": "*",
#        "ext-session": "*",
#        "ext-zlib": "*",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": ">=1",
#        "php": ">=5.4",
#        "symfony/polyfill-php56": "^1"
#    }
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-date
BuildRequires:  php-dom
BuildRequires:  php-hash
BuildRequires:  php-libxml
BuildRequires:  php-openssl
BuildRequires:  php-session
BuildRequires:  php-zlib
BuildRequires:  php-composer(paragonie/constant_time_encoding)
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(symfony/polyfill-php56)
%endif

#    "require": {
#        "ext-date": "*",
#        "ext-dom": "*",
#        "ext-hash": "*",
#        "ext-libxml": "*",
#        "ext-openssl": "*",
#        "ext-session": "*",
#        "ext-zlib": "*",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": ">=1",
#        "php": ">=5.4",
#        "symfony/polyfill-php56": "^1"
#    }
Requires:       php(language) >= 5.4.0
Requires:       php-date
Requires:       php-dom
Requires:       php-hash
Requires:       php-libxml
Requires:       php-openssl
Requires:       php-session
Requires:       php-zlib
Requires:       php-composer(paragonie/constant_time_encoding)
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
Requires:       php-composer(paragonie/random_compat)
Requires:       php-composer(symfony/polyfill-php56)
%endif

Provides:       php-composer(fkooman/saml-sp) = %{version}

%description
This library allows adding SAML Service Provider (SP) support to your PHP web
application.

%prep
%if %{defined git}
%setup -qn php-saml-sp-%{git}
%else
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn php-saml-sp-%{version}
%endif

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
AUTOLOAD
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/random_compat/autoload.php';
require_once '%{_datadir}/php/Symfony/Polyfill/autoload.php';
AUTOLOAD
%endif

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/SAML/SP

cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/SAML/SP

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
%dir %{_datadir}/php/fkooman/SAML
%{_datadir}/php/fkooman/SAML/SP

%changelog
* Wed Jan 16 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.17
- rebuilt

* Tue Jan 15 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.16
- rebuilt

* Tue Jan 15 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.15
- rebuilt

* Tue Jan 15 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.14
- rebuilt

* Fri Jan 11 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.13
- rebuilt

* Thu Jan 10 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.12
- rebuilt

* Thu Jan 10 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.11
- rebuilt

* Tue Jan 08 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.10
- rebuilt

* Tue Jan 08 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.9
- rebuilt

* Mon Jan 07 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.8
- rebuilt

* Sun Jan 06 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.7
- rebuilt

* Sun Jan 06 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.6
- rebuilt

* Sun Jan 06 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.5
- rebuilt

* Sun Jan 06 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.4
- rebuilt

* Sun Jan 06 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.3
- rebuilt

* Sun Jan 06 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.2
- rebuilt

* Fri Oct 19 2018 François Kooman <fkooman@tuxed.net> - 0.0.0-0.1
- initial package
