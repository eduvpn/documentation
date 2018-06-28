Name:       php-json-signer
Version:    3.0.2
Release:    5%{?dist}
Summary:    PHP JSON Signer

Group:      Applications/System
License:    MIT

URL:        https://software.tuxed.net/php-json-signer
Source0:    https://software.tuxed.net/php-json-signer/files/php-json-signer-%{version}.tar.xz
Source1:    https://software.tuxed.net/php-json-signer/files/php-json-signer-%{version}.tar.xz.asc
Source2:    gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2
Patch0:     %{name}-autoload.patch

BuildArch:  noarch

BuildRequires:  gnupg2
BuildRequires:  %{_bindir}/phpunit
BuildRequires:  %{_bindir}/phpab
BuildRequires:  php(language) >= 5.4.0
#    "suggest": {
#        "ext-libsodium": "PHP < 7.2 sodium implementation",
#        "ext-sodium": "PHP >= 7.2 sodium implementation"
#    },
BuildRequires:  php-pecl(libsodium)
BuildRequires:  php-date
BuildRequires:  php-json
BuildRequires:  php-spl
BuildRequires:  php-composer(paragonie/constant_time_encoding)

Requires:   php(language) >= 5.4.0
#    "suggest": {
#        "ext-libsodium": "PHP < 7.2 sodium implementation",
#        "ext-sodium": "PHP >= 7.2 sodium implementation"
#    },
Requires:   php-pecl(libsodium)
Requires:   php-date
Requires:   php-json
Requires:   php-spl
Requires:   php-composer(paragonie/constant_time_encoding)

%description
This application can be used to sign JSON files, by adding some fields that 
can be used to determine their time of signing and the sequence number. The 
signature is "detached" so no complicated file syntax is needed to store the 
signature in the file itself.

%prep
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%setup -qn php-json-signer-%{version}
%patch0 -p1
 
%build
%{_bindir}/phpab -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once sprintf('%s/sodium_compat.php', __DIR__);
require_once '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php';
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/JsonSigner
install -m 0644 src/* --target-directory %{buildroot}%{_datadir}/php/fkooman/JsonSigner
install -D -m 0755 bin/app.php %{buildroot}%{_bindir}/php-json-signer

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

%files
%defattr(-,root,root,-)
%{_bindir}/*
%dir %{_datadir}/php/fkooman
%{_datadir}/php/fkooman/JsonSigner
%doc README.md CHANGES.md UPGRADING.md composer.json
%license LICENSE

%changelog
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
