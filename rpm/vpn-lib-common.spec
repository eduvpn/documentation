%global composer_namespace      SURFnet/VPN/Common

%global github_owner            eduvpn
%global github_name             vpn-lib-common
%global github_commit           07510f6562bb4a063a8349fcd4ee0e4acb2652a9
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       vpn-lib-common
Version:    1.0.0
Release:    0.51%{?dist}
Summary:    Common VPN library
Group:      System Environment/Libraries
License:    AGPLv3+
URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz
BuildArch:  noarch

BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-filter
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-mbstring
BuildRequires:  php-pcre
BuildRequires:  php-libsodium
BuildRequires:  php-session
BuildRequires:  php-spl
BuildRequires:  php-composer(fedora/autoloader)
BuildRequires:  php-composer(psr/log)
BuildRequires:  php-composer(ircmaxell/password-compat)
BuildRequires:  php-composer(twig/twig) < 2
BuildRequires:  php-composer(twig/extensions)
BuildRequires:  %{_bindir}/phpunit

Requires:   php(language) >= 5.4.0
Requires:   php-curl
Requires:   php-date
Requires:   php-filter
Requires:   php-hash
Requires:   php-libsodium
Requires:   php-json
Requires:   php-mbstring
Requires:   php-pcre
Requires:   php-session
Requires:   php-spl
Requires:   php-composer(fedora/autoloader)
Requires:   php-composer(psr/log)
Requires:   php-composer(ircmaxell/password-compat)
Requires:   php-composer(twig/twig) < 2
Requires:   php-composer(twig/extensions)

%description
Common VPN library.

%prep
%setup -qn %{github_name}-%{github_commit}

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('SURFnet\\VPN\\Common\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/Psr/Log/autoload.php',
    '%{_datadir}/php/password_compat/password.php',
    '%{_datadir}/php/Twig/autoload.php',
    '%{_datadir}/php/Twig/Extensions/autoload.php',
));
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/php/%{composer_namespace}
cp -pr src/* %{buildroot}%{_datadir}/php/%{composer_namespace}

%check
phpunit --bootstrap=%{buildroot}/%{_datadir}/php/%{composer_namespace}/autoload.php

%files
%dir %{_datadir}/php/SURFnet
%dir %{_datadir}/php/SURFnet/VPN
%{_datadir}/php/%{composer_namespace}
%doc README.md composer.json CHANGES.md
%license LICENSE

%changelog
* Tue Apr 25 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.51
- rebuilt

* Tue Apr 25 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.50
- rebuilt

* Mon Apr 24 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.49
- rebuilt

* Mon Apr 24 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.48
- rebuilt

* Tue Apr 18 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.47
- rebuilt

* Tue Apr 18 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.46
- rebuilt

* Tue Apr 18 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.45
- rebuilt

* Tue Apr 11 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.44
- rebuilt

* Fri Mar 31 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.43
- rebuilt

* Wed Mar 29 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.42
- rebuilt

* Wed Mar 29 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.41
- rebuilt

* Thu Mar 23 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.40
- rebuilt

* Thu Mar 16 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.39
- rebuilt

* Thu Mar 16 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.38
- rebuilt

* Wed Feb 15 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.37
- rebuilt

* Tue Feb 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.36
- rebuilt

* Tue Feb 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.35
- rebuilt

* Wed Jan 25 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.34
- rebuilt

* Sun Jan 22 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.33
- rebuilt

* Fri Jan 20 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.32
- rebuilt

* Thu Jan 19 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.31
- rebuilt

* Thu Jan 19 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.30
- rebuilt

* Thu Jan 19 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.29
- rebuilt

* Wed Jan 18 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.28
- rebuilt

* Wed Jan 18 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.27
- rebuilt

* Thu Jan 05 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.26
- rebuilt

* Wed Jan 04 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.25
- rebuilt

* Wed Jan 04 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.24
- rebuilt

* Wed Jan 04 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.23
- rebuilt

* Tue Jan 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.22
- rebuilt

* Tue Jan 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.21
- rebuilt

* Tue Jan 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.20
- rebuilt

* Tue Jan 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.19
- rebuilt

* Thu Dec 15 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.18
- rebuilt

* Thu Dec 15 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.17
- rebuilt

* Tue Dec 13 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.16
- rebuilt

* Tue Dec 13 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.15
- rebuilt

* Mon Dec 12 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.14
- rebuilt

* Mon Dec 12 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.13
- rebuilt

* Wed Dec 07 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.12
- rebuilt

* Tue Dec 06 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.11
- rebuilt

* Tue Dec 06 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.10
- rebuilt

* Mon Dec 05 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.9
- rebuilt

* Sun Dec 04 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.8
- rebuilt

* Sat Dec 03 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.7
- rebuilt

* Fri Dec 02 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.6
- rebuilt

* Fri Dec 02 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.5
- rebuilt

* Fri Dec 02 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.4
- rebuilt

* Thu Dec 01 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.3
- rebuilt

* Thu Dec 01 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.2
- rebuilt

* Thu Dec 01 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.1
- rebuilt
