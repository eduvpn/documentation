%global composer_vendor         fkooman
%global composer_project        oauth2-client
%global composer_namespace      %{composer_vendor}/OAuth/Client

%global github_owner            fkooman
%global github_name             php-oauth2-client

%global commit0 a62ea870dfdf52efea413a6859cb06cd52c1b89a
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:       php-%{composer_vendor}-%{composer_project}
Version:    5.0.0
Release:    0.25%{?dist}
Summary:    Very simple OAuth 2.0 client

Group:      System Environment/Libraries
License:    MIT

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildArch:  noarch

BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-curl
BuildRequires:  php-session
BuildRequires:  php-date
BuildRequires:  php-json
BuildRequires:  php-spl
BuildRequires:  php-standard
BuildRequires:  php-composer(fedora/autoloader)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(psr/log)
BuildRequires:  %{_bindir}/phpunit

Requires:   php(language) >= 5.4.0
Requires:   php-curl
Requires:   php-session
Requires:   php-date
Requires:   php-json
Requires:   php-spl
Requires:   php-standard
Requires:   php-composer(fedora/autoloader)
Requires:   php-composer(paragonie/constant_time_encoding)
Requires:   php-composer(paragonie/random_compat)
Requires:   php-composer(psr/log)

Provides:   php-composer(%{composer_vendor}/%{composer_project}) = %{version}

%description
This is a very simple OAuth 2.0 client for integration in your own 
application. It has minimal dependencies, but still tries to be secure. 
The main purpose is to be compatible with PHP 5.4.

%prep
%setup -n %{github_name}-%{commit0}

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('fkooman\\OAuth\\Client\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php',
    '%{_datadir}/php/random_compat/autoload.php',
    '%{_datadir}/php/Psr/Log/autoload.php',
));

AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/%{composer_namespace}
cp -pr src/* %{buildroot}%{_datadir}/php/%{composer_namespace}

%check
mkdir vendor
cat << 'EOF' | tee vendor/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Dependencies::required(array(
    '%{buildroot}/%{_datadir}/php/%{composer_namespace}/autoload.php',
));
\Fedora\Autoloader\Autoload::addPsr4('fkooman\\OAuth\\Client\\Tests\\', dirname(__DIR__) . '/tests');
EOF

%{_bindir}/phpunit --verbose
%files
%dir %{_datadir}/php/fkooman
%dir %{_datadir}/php/fkooman/OAuth
%{_datadir}/php/%{composer_namespace}
%doc README.md CHANGES.md composer.json
%license LICENSE

%changelog
* Sat May 06 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.25
- rebuilt

* Fri May 05 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.24
- rebuilt

* Fri May 05 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.23
- rebuilt

* Fri May 05 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.22
- rebuilt

* Fri Apr 28 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.21
- rebuilt

* Sun Apr 23 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.20
- rebuilt

* Sun Apr 23 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.19
- rebuilt

* Sun Apr 23 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.18
- rebuilt

* Sat Apr 22 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.17
- rebuilt

* Sat Apr 22 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.16
- rebuilt

* Fri Apr 21 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.15
- rebuilt

* Fri Apr 21 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.14
- rebuilt

* Fri Apr 21 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.13
- rebuilt

* Fri Apr 21 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.12
- rebuilt

* Wed Mar 29 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.11
- rebuilt

* Mon Mar 20 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.10
- rebuilt

* Thu Mar 16 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.9
- rebuilt

* Mon Mar 13 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.8
- rebuilt
