#global git 242e5ef7cfed32950fdbce394425deff547ed3d5

Name:       php-json-signer
Version:    3.0.2
Release:    11%{?dist}
Summary:    PHP JSON Signer

Group:      Applications/System
License:    MIT

URL:        https://software.tuxed.net/php-json-signer
%if %{defined git}
Source0:    https://git.tuxed.net/fkooman/php-json-signer/snapshot/php-json-signer-%{git}.tar.xz
%else
Source0:    https://software.tuxed.net/php-json-signer/files/php-json-signer-%{version}.tar.xz
Source1:    https://software.tuxed.net/php-json-signer/files/php-json-signer-%{version}.tar.xz.minisig
Source2:    minisign-8466FFE127BCDC82.pub
%endif
Patch0:     %{name}-autoload.patch

BuildArch:  noarch

BuildRequires:  minisign
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpab
#    "require-dev": {
#        "phpunit/phpunit": "^4.8.35|^5|^6|^7"
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
#        "ext-json": "*",
#        "ext-spl": "*",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "php": ">=5.4.0"
#    },
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-date
BuildRequires:  php-json
BuildRequires:  php-spl
BuildRequires:  php-composer(paragonie/constant_time_encoding)
#    "suggest": {
#        "ext-libsodium": "PHP < 7.2 sodium implementation",
#        "ext-sodium": "PHP >= 7.2 sodium implementation"
#    },
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
BuildRequires:  php-sodium
%else
BuildRequires:  php-pecl(libsodium)
%endif

#    "require": {
#        "ext-date": "*",
#        "ext-json": "*",
#        "ext-spl": "*",
#        "paragonie/constant_time_encoding": "^1|^2",
#        "php": ">=5.4.0"
#    },
Requires:   php(language) >= 5.4.0
Requires:   php-date
Requires:   php-json
Requires:   php-spl
Requires:   php-composer(paragonie/constant_time_encoding)
#    "suggest": {
#        "ext-libsodium": "PHP < 7.2 sodium implementation",
#        "ext-sodium": "PHP >= 7.2 sodium implementation"
#    },
%if 0%{?fedora} >= 28 || 0%{?rhel} >= 8
Requires:       php-sodium
%else
Requires:       php-pecl(libsodium)
%endif

%description
This application can be used to sign JSON files, by adding some fields that 
can be used to determine their time of signing and the sequence number. The 
signature is "detached" so no complicated file syntax is needed to store the 
signature in the file itself.

%prep
%if %{defined git}
%setup -qn php-json-signer-%{git}
%else
/usr/bin/minisign -V -m %{SOURCE0} -x %{SOURCE1} -p %{SOURCE2}
%setup -qn php-json-signer-%{version}
%endif
%patch0 -p1
 
%build
%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
AUTOLOAD
%if 0%{?fedora} < 28 && 0%{?rhel} < 8
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once sprintf('%s/sodium_compat.php', __DIR__);
AUTOLOAD
%endif

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/JsonSigner
install -m 0644 src/* --target-directory %{buildroot}%{_datadir}/php/fkooman/JsonSigner
install -D -m 0755 bin/app.php %{buildroot}%{_bindir}/php-json-signer

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{phpunit} tests --verbose --bootstrap=tests/autoload.php

%files
%defattr(-,root,root,-)
%{_bindir}/*
%dir %{_datadir}/php/fkooman
%{_datadir}/php/fkooman/JsonSigner
%doc README.md CHANGES.md UPGRADING.md composer.json
%license LICENSE

%changelog
* Fri Aug 09 2019 François Kooman <fkooman@tuxed.net> - 3.0.2-11
- switch to minisign signature verification for release builds

* Mon Sep 10 2018 François Kooman <fkooman@tuxed.net> - 3.0.2-10
- merge dev and prod spec files in one
- cleanup requirements

* Sat Sep 08 2018 François Kooman <fkooman@tuxed.net> - 3.0.2-9
- requires php-sodium on modern OSes to make sure we do not need sodium compat
- add composer.json comments to (Build)Requires

* Sun Aug 05 2018 François Kooman <fkooman@tuxed.net> - 3.0.2-8
- use phpunit7 on supported platforms

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 3.0.2-7
- add missing BR

* Mon Jul 23 2018 François Kooman <fkooman@tuxed.net> - 3.0.2-6
- use fedora phpab template for generating autoloader

* Thu Jun 28 2018 François Kooman <fkooman@tuxed.net> - 3.0.2-5
- use release tarball instead of Git tarball
- verify GPG signature

* Fri Jun 01 2018 François Kooman <fkooman@tuxed.net> - 3.0.2-4
- update upstream URL to git.tuxed.net

* Thu Apr 19 2018 François Kooman <fkooman@tuxed.net> - 3.0.2-3
- depend on php-pecl(libsodium)

* Tue Dec 12 2017 François Kooman <fkooman@tuxed.net> - 3.0.2-2
- cleanup install

* Mon Dec 11 2017 François Kooman <fkooman@tuxed.net> - 3.0.2-1
- update to 3.0.2

* Mon Dec 11 2017 François Kooman <fkooman@tuxed.net> - 3.0.1-1
- update to 3.0.1

* Thu Dec 07 2017 François Kooman <fkooman@tuxed.net> - 3.0.0-2
- use phpab to generate the classloader

* Mon Nov 20 2017 François Kooman <fkooman@tuxed.net> - 3.0.0-1
- update to 3.0.0

* Tue Oct 31 2017 François Kooman <fkooman@tuxed.net> - 2.1.0-1
- update to 2.1.0

* Mon Oct 30 2017 François Kooman <fkooman@tuxed.net> - 2.0.0-1
- update to 2.0.0

* Tue Aug 22 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Mon Aug 14 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
