%global composer_vendor         christian-riesen
%global composer_project        otp
%global composer_namespace      Otp

%global github_owner            ChristianRiesen
%global github_name             otp
%global github_commit           83f941e1ad6f7a2ff318e30cbf5b3219e63a9a62
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       php-%{composer_vendor}-%{composer_project}
Version:    2.3.0
Release:    1%{?dist}
Summary:    One Time Passwords

Group:      System Environment/Libraries
License:    MIT

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz

BuildArch:  noarch

BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-date
BuildRequires:  php-hash
BuildRequires:  php-openssl
BuildRequires:  php-spl
BuildRequires:  php-composer(christian-riesen/base32)
BuildRequires:  php-composer(paragonie/random_compat)
BuildRequires:  php-composer(fedora/autoloader)
BuildRequires:  %{_bindir}/phpunit

Requires:   php(language) >= 5.4.0
Requires:   php-date
Requires:   php-hash
Requires:   php-openssl
Requires:   php-spl
Requires:   php-composer(christian-riesen/base32)
Requires:   php-composer(paragonie/random_compat)
Requires:   php-composer(fedora/autoloader)

Provides:   php-composer(%{composer_vendor}/%{composer_project}) = %{version}

%description
Implements hotp according to RFC4226 and totp according to RFC6238 (only sha1 
algorithm).

%prep
%setup -qn %{github_name}-%{github_commit}

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('Otp\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/Base32/autoload.php',
    '%{_datadir}/php/random_compat/autoload.php',
));
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/%{composer_namespace}
cp -pr src/* %{buildroot}%{_datadir}/php/%{composer_namespace}/

%check
phpunit --bootstrap=%{buildroot}/%{_datadir}/php/%{composer_namespace}/autoload.php

%files
%{_datadir}/php/%{composer_namespace}
%doc README.md composer.json
%license LICENSE

%changelog
* Tue Jan 17 2017 François Kooman <fkooman@tuxed.net> - 2.3.0-1
- update to 2.3.0

* Fri Nov 25 2016 François Kooman <fkooman@tuxed.net> - 2.2.0-4
- more spec cleanup

* Tue Nov 15 2016 François Kooman <fkooman@tuxed.net> - 2.2.0-3
- cleanup spec

* Thu Oct 13 2016 François Kooman <fkooman@tuxed.net> - 2.2.0-2
- do not depend on libsodium any longer

* Wed Sep 14 2016 François Kooman <fkooman@tuxed.net> - 2.2.0-1
- update to 2.2.0

* Fri Apr 22 2016 François Kooman <fkooman@tuxed.net> - 1.4.3-1
- initial package
