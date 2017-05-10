%global composer_namespace      SURFnet/VPN/Common

%global github_owner            eduvpn
%global github_name             vpn-lib-common
%global github_commit           b22f148b2083191a43f1825e76f689d718b45ef9
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       vpn-lib-common
Version:    1.0.0
Release:    0.55%{?dist}
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
BuildRequires:  php-gettext
BuildRequires:  php-json
BuildRequires:  php-libsodium
BuildRequires:  php-mbstring
BuildRequires:  php-pcre
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
Requires:   php-gettext
Requires:   php-json
Requires:   php-libsodium
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
mkdir vendor
cat << 'EOF' | tee vendor/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Dependencies::required(array(
    '%{buildroot}/%{_datadir}/php/%{composer_namespace}/autoload.php',
));
\Fedora\Autoloader\Autoload::addPsr4('SURFnet\\VPN\\Common\\Tests\\', dirname(__DIR__) . '/tests');
EOF

%{_bindir}/phpunit --verbose

%files
%dir %{_datadir}/php/SURFnet
%dir %{_datadir}/php/SURFnet/VPN
%{_datadir}/php/%{composer_namespace}
%doc README.md composer.json CHANGES.md
%license LICENSE

%changelog
* Wed May 10 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.55
- rebuilt

* Mon May 01 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.54
- rebuilt

* Mon May 01 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.53
- rebuilt

* Sat Apr 29 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.52
- rebuilt
