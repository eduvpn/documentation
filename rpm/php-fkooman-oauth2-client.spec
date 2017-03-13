%global composer_vendor         fkooman
%global composer_project        oauth2-client
%global composer_namespace      %{composer_vendor}/OAuth/Client

%global github_owner            fkooman
%global github_name             php-oauth2-client

%global commit0 4207dd0cedd56a9a74633fed28b6acb4e09acf05
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:       php-%{composer_vendor}-%{composer_project}
Version:    5.0.0
Release:    0.8%{?dist}
Summary:    Very simple OAuth 2.0 client

Group:      System Environment/Libraries
License:    AGPLv3+

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildArch:  noarch

BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-curl
BuildRequires:  php-json
BuildRequires:  php-spl
BuildRequires:  php-standard
BuildRequires:  php-composer(fedora/autoloader)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  %{_bindir}/phpunit

Requires:   php(language) >= 5.4.0
Requires:   php-curl
Requires:   php-json
Requires:   php-spl
Requires:   php-standard
Requires:   php-composer(fedora/autoloader)
Requires:   php-composer(paragonie/constant_time_encoding)
Requires:   php-composer(paragonie/random_compat)

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
));

AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/%{composer_namespace}
cp -pr src/* %{buildroot}%{_datadir}/php/%{composer_namespace}

%check
phpunit --no-coverage --verbose --bootstrap=%{buildroot}/%{_datadir}/php/%{composer_namespace}/autoload.php

%files
%dir %{_datadir}/php/fkooman
%dir %{_datadir}/php/fkooman/OAuth
%{_datadir}/php/%{composer_namespace}
%doc README.md CHANGES.md composer.json
%license LICENSE

%changelog
* Mon Mar 13 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.8
- rebuilt

* Mon Mar 13 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.7
- rebuilt

* Mon Feb 13 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.6
- rebuilt

* Thu Feb 09 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.5
- rebuilt

* Tue Feb 07 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.4
- rebuilt

* Thu Feb 02 2017 François Kooman <fkooman@tuxed.net> - 5.0.0-0.3
- rebuilt

* Thu Feb 02 2017 François Kooman <fkooman@tuxed.net> - 4.1.0-0.2
- rebuilt

* Thu Feb 02 2017 François Kooman <fkooman@tuxed.net> - 4.0.1-2
- rebuilt

* Thu Jan 19 2017 François Kooman <fkooman@tuxed.net> - 4.0.1-1
- update to 4.0.1

* Wed Jan 04 2017 François Kooman <fkooman@tuxed.net> - 4.0.0-1
- update to 4.0.0

* Tue Jan 03 2017 François Kooman <fkooman@tuxed.net> - 3.0.2-1
- update to 3.0.2
- fix dependency version constraint

* Mon Dec 12 2016 François Kooman <fkooman@tuxed.net> - 3.0.1-2
- remove dependencies no longer used

* Mon Dec 12 2016 François Kooman <fkooman@tuxed.net> - 3.0.1-1
- update to 3.0.1
- license changed to AGPLv3+

* Fri Nov 25 2016 François Kooman <fkooman@tuxed.net> - 3.0.0-1
- update to 3.0.0

* Thu Nov 24 2016 François Kooman <fkooman@tuxed.net> - 2.0.2-2
- fix typo in description
- remove BuildRoot
- remove clean section
- fix directory ownership

* Tue Nov 15 2016 François Kooman <fkooman@tuxed.net> - 2.0.2-1
- update to 2.0.2

* Thu Sep 29 2016 François Kooman <fkooman@tuxed.net> - 2.0.1-1
- update to 2.0.1

* Wed Sep 21 2016 François Kooman <fkooman@tuxed.net> - 2.0.0-1
- update to 2.0.0

* Sat Jun 04 2016 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Mon May 30 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
