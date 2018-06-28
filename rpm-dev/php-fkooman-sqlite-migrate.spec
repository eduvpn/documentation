%global commit0 605247a3e219f0ebf43beee3b37ec6af41d1eba4

Name:           php-fkooman-sqlite-migrate
Version:        0.1.1
Release:        1%{?dist}
Summary:        Simple SQLite migrations

License:        MIT
URL:            https://git.tuxed.net/fkooman/php-sqlite-migrate
Source0:        https://git.tuxed.net/fkooman/php-sqlite-migrate/snapshot/php-sqlite-migrate-%{commit0}.tar.xz

BuildArch:      noarch

#        "php": ">=5.4",
BuildRequires:  php(language) >= 5.4.0
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-spl
BuildRequires:  %{_bindir}/phpab
BuildRequires:  %{_bindir}/phpunit

#        "php": ">=5.4",
Requires:       php(language) >= 5.4.0
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-spl": "*",
Requires:       php-pcre
Requires:       php-pdo
Requires:       php-spl

Provides:       php-composer(fkooman/sqlite-migrate) = %{version}

%description
Very simple library that can assist with database migrations for SQLite when 
using PHP.

%prep
%autosetup -n php-sqlite-migrate-%{commit0}

%build
%{_bindir}/phpab -o src/autoload.php src

%install
mkdir -p %{buildroot}%{_datadir}/php/fkooman/SqliteMigrate
cp -pr src/* %{buildroot}%{_datadir}/php/fkooman/SqliteMigrate

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

%{_bindir}/phpunit tests --verbose --bootstrap=tests/autoload.php

%files
%license LICENSE
%doc composer.json CHANGELOG.md README.md
%dir %{_datadir}/php/fkooman
%{_datadir}/php/fkooman/SqliteMigrate

%changelog
* Tue Jun 26 2018 François Kooman <fkooman@tuxed.net> - 0.1.1-1
- update to 0.1.1

* Mon Jun 25 2018 François Kooman <fkooman@tuxed.net> - 0.1.0-1
- intiial package
