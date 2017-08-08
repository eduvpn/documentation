%global composer_vendor         fkooman
%global composer_project        secookie
%global composer_namespace      %{composer_vendor}/SeCookie

%global github_owner            fkooman
%global github_name             php-secookie

%global commit0 9f63939f14ed1206a0b011d4735d4ed75163f660
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:       php-%{composer_vendor}-%{composer_project}
Version:    1.0.2
Release:    1%{?dist}
Summary:    Very simple Cookie and PHP Session library

Group:      System Environment/Libraries
License:    MIT

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildArch:  noarch

#        "php": ">=5.4.0",
BuildRequires:  php(language) >= 5.4.0
#        "ext-date": "*",
#        "ext-session": "*",
BuildRequires:  php-date
BuildRequires:  php-session
BuildRequires:  php-standard
BuildRequires:  php-composer(fedora/autoloader)
BuildRequires:  %{_bindir}/phpunit

Requires:   php(language) >= 5.4.0
Requires:   php-date
Requires:   php-session
Requires:   php-standard
Requires:   php-composer(fedora/autoloader)

Provides:   php-composer(%{composer_vendor}/%{composer_project}) = %{version}

%description
Very simple Cookie and PHP Session library.

%prep
%setup -n %{github_name}-%{commit0}

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('fkooman\\SeCookie\\', __DIR__);
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
\Fedora\Autoloader\Autoload::addPsr4('fkooman\\SeCookie\\Tests\\', dirname(__DIR__) . '/tests');
EOF

%{_bindir}/phpunit --verbose
%files
%dir %{_datadir}/php/fkooman
%dir %{_datadir}/php/fkooman/SeCookie
%{_datadir}/php/%{composer_namespace}
%doc README.md CHANGES.md composer.json
%license LICENSE

%changelog
* Tue Aug 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.2-1
- update to 1.0.2

* Mon Aug 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Fri Jun 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-2
- remove old changelog entries

* Fri Jun 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
