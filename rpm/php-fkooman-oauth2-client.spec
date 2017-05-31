%global composer_vendor         fkooman
%global composer_project        oauth2-client
%global composer_namespace      %{composer_vendor}/OAuth/Client

%global github_owner            fkooman
%global github_name             php-oauth2-client

%global commit0 8b0d2cd02189551ec71c09a38f349876ebd5b069
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:       php-%{composer_vendor}-%{composer_project}
Version:    5.0.0
Release:    0.40%{?dist}
Summary:    Very simple OAuth 2.0 client

Group:      System Environment/Libraries
License:    MIT

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildArch:  noarch

#        "php": ">=5.4.0",
BuildRequires:  php(language) >= 5.4.0
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-session": "*",
#        "ext-spl": "*",
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-session
BuildRequires:  php-spl
BuildRequires:  php-standard
#        "paragonie/constant_time_encoding": "^1|^2",
#        "paragonie/random_compat": "^1|^2",
#        "symfony/polyfill-php56": "^1.3"
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(symfony/polyfill-php56)
BuildRequires:  php-composer(fedora/autoloader)
BuildRequires:  %{_bindir}/phpunit

Requires:   php(language) >= 5.4.0
Requires:   php-curl
Requires:   php-date
Requires:   php-hash
Requires:   php-json
Requires:   php-pcre
Requires:   php-pdo
Requires:   php-session
Requires:   php-spl
Requires:   php-standard
Requires:   php-composer(paragonie/constant_time_encoding)
Requires:   php-composer(paragonie/random_compat)
Requires:   php-composer(symfony/polyfill-php56)
Requires:   php-composer(fedora/autoloader)

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
    '%{_datadir}/php/Symfony/Polyfill/autoload.php',
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
* Wed May 31 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.40
- rebuilt

* Wed May 24 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.39
- rebuilt

* Sat May 13 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.38
- rebuilt

* Fri May 12 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.37
- rebuilt

* Fri May 12 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.36
- rebuilt

* Wed May 10 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.35
- rebuilt

* Tue May 09 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.34
- rebuilt

* Tue May 09 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.33
- rebuilt

* Tue May 09 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.32
- rebuilt

* Tue May 09 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.31
- rebuilt

* Tue May 09 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.30
- rebuilt
