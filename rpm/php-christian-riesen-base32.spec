%global composer_vendor         christian-riesen
%global composer_project        base32
%global composer_namespace      Base32

%global github_owner            ChristianRiesen
%global github_name             base32
%global github_commit           0a31e50c0fa9b1692d077c86ac188eecdcbaf7fa
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       php-%{composer_vendor}-%{composer_project}
Version:    1.3.1
Release:    4%{?dist}
Summary:    Base32 Encoder/Decoder according to RFC 4648

Group:      System Environment/Libraries
License:    MIT

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz

BuildArch:  noarch

BuildRequires:  php(language) >= 5.3.0
BuildRequires:  php-pcre
BuildRequires:  php-composer(fedora/autoloader)
BuildRequires:  %{_bindir}/phpunit

Requires:   php(language) >= 5.3.0
Requires:   php-pcre
Requires:   php-composer(fedora/autoloader)

Provides:   php-composer(%{composer_vendor}/%{composer_project}) = %{version}

%description
Base32 Encoder/Decoder for PHP according to RFC 4648.

%prep
%setup -qn %{github_name}-%{github_commit}

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('Base32\\', __DIR__);
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/%{composer_namespace}
cp -pr src/* %{buildroot}%{_datadir}/php/%{composer_namespace}

%check
phpunit --bootstrap=%{buildroot}/%{_datadir}/php/%{composer_namespace}/autoload.php

%files
%{_datadir}/php/%{composer_namespace}
%doc README.md composer.json
%license LICENSE

%changelog
* Fri Nov 25 2016 François Kooman <fkooman@tuxed.net> - 1.3.1-4
- remove defattr

* Fri Nov 25 2016 François Kooman <fkooman@tuxed.net> - 1.3.1-3
- cleanup spec file

* Tue Nov 15 2016 François Kooman <fkooman@tuxed.net> - 1.3.1-2
- update autoloader
- spec cleanup

* Fri May 06 2016 François Kooman <fkooman@tuxed.net> - 1.3.1-1
- update to 1.3.1

* Fri Apr 22 2016 François Kooman <fkooman@tuxed.net> - 1.3.0-2
- add pecl extension as a requirement

* Fri Apr 22 2016 François Kooman <fkooman@tuxed.net> - 1.3.0-1
- initial package
