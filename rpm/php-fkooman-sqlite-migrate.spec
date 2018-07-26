Name:           php-fkooman-sqlite-migrate
Version:        0.1.1
Release:        1%{?dist}
Summary:        Simple SQLite Migrations

License:        MIT
URL:            https://software.tuxed.net/php-sqlite-migrate
Source0:        https://software.tuxed.net/php-sqlite-migrate/files/php-sqlite-migrate-%{version}.tar.xz
Source1:        https://software.tuxed.net/php-sqlite-migrate/files/php-sqlite-migrate-%{version}.tar.xz.asc
Source2:        gpgkey-6237BAF1418A907DAA98EAA79C5EDD645A571EB2

BuildArch:      noarch

BuildRequires:  gnupg2
#        "php": ">= 5.4",
BuildRequires:  php(language) >= 5.4.0
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-spl
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
Requires:       php(language) >= 5.4.0
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
Requires:       php-pcre
Requires:       php-pdo
Requires:       php-spl

Provides:       php-composer(fkooman/sqlite-migrate) = %{version}

%description
Library written in PHP that can assist with SQLite database migrations.

%prep
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%autosetup -n php-sqlite-migrate-%{version}

%build
%{_bindir}/phpab -t fedora -o src/autoload.php src

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/SqliteMigrate
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/SqliteMigrate

%check
%{_bindir}/phpab -t fedora -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{phpunit} tests --verbose --bootstrap=tests/autoload.php

%files
%license LICENSE
%doc composer.json CHANGELOG.md README.md
%dir %{_datadir}/php/fkooman
%{_datadir}/php/fkooman/SqliteMigrate

%changelog
* Thu Jul 26 2018 François Kooman <fkooman@tuxed.net> - 0.1.1-1
- initial package
