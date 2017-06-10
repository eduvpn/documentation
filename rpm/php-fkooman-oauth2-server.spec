%global composer_vendor         fkooman
%global composer_project        oauth2-server
%global composer_namespace      %{composer_vendor}/OAuth/Server

%global github_owner            fkooman
%global github_name             php-oauth2-server

%global commit0 5aeb812a48835701d19453d9735641871dbf8212
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:       php-%{composer_vendor}-%{composer_project}
Version:    1.0.0
Release:    0.37%{?dist}
Summary:    Very simple OAuth 2.0 server

Group:      System Environment/Libraries
License:    MIT

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildArch:  noarch

BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-libsodium
BuildRequires:  php-date
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-standard
BuildRequires:  php-composer(fedora/autoloader)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  %{_bindir}/phpunit

Requires:   php(language) >= 5.4.0
Requires:   php-libsodium
Requires:   php-date
Requires:   php-hash
Requires:   php-json
Requires:   php-pcre
Requires:   php-pdo
Requires:   php-standard
Requires:   php-composer(fedora/autoloader)
Requires:   php-composer(paragonie/constant_time_encoding)

Provides:   php-composer(%{composer_vendor}/%{composer_project}) = %{version}

%description
This is a very simple OAuth 2.0 server for integration in your own 
application. It has minimal dependencies, but still tries to be secure. 
The main purpose is to be compatible with PHP 5.4.

%prep
%setup -n %{github_name}-%{commit0}

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('fkooman\\OAuth\\Server\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php',
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
\Fedora\Autoloader\Autoload::addPsr4('fkooman\\OAuth\\Server\\Tests\\', dirname(__DIR__) . '/tests');
EOF

%{_bindir}/phpunit --verbose

%files
%dir %{_datadir}/php/fkooman
%dir %{_datadir}/php/fkooman/OAuth
%{_datadir}/php/%{composer_namespace}
%doc README.md CHANGES.md composer.json
%license LICENSE

%changelog
* Sat Jun 10 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.37
- rebuilt

* Sun May 21 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.36
- rebuilt

* Fri May 19 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.35
- rebuilt

* Sat May 06 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.34
- rebuilt

* Sat May 06 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.33
- rebuilt

* Fri May 05 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.32
- rebuilt

* Wed May 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.31
- rebuilt

* Wed May 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.30
- rebuilt

* Thu Apr 27 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.29
- rebuilt

* Wed Apr 26 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.28
- rebuilt

* Fri Apr 21 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.27
- rebuilt

* Thu Apr 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.26
- rebuilt

* Thu Mar 16 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.25
- rebuilt
