%global github_owner            fkooman
%global github_name             php-json-signer
%global github_commit           70c2716b41d50bff9f7fcc53d686856c87371a9d
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       php-json-signer
Version:    1.0.1
Release:    1%{?dist}
Summary:    PHP JSON Signer

Group:      Applications/System
License:    MIT

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz

BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

BuildRequires:  %{_bindir}/phpunit
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-date
BuildRequires:  php-json
BuildRequires:  php-libsodium
BuildRequires:  php-spl
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(dnoegel/php-xdg-base-dir)
BuildRequires:  php-composer(fedora/autoloader)

Requires:   php(language) >= 5.4.0
Requires:   php-date
Requires:   php-json
Requires:   php-libsodium
Requires:   php-spl
Requires:   php-composer(paragonie/constant_time_encoding)
Requires:   php-composer(dnoegel/php-xdg-base-dir)
Requires:   php-composer(fedora/autoloader)

%description
JSON signer written in PHP.

%prep
%setup -qn %{github_name}-%{github_commit} 

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('fkooman\\JsonSigner\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php',
    '%{_datadir}/php/XdgBaseDir/autoload.php',
));
AUTOLOAD

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/%{name}

cp -pr bin src %{buildroot}%{_datadir}/%{name}
chmod +x %{buildroot}%{_datadir}/%{name}/bin/*.php

ln -s %{_datadir}/%{name}/bin/init.php %{buildroot}%{_bindir}/%{name}-init
ln -s %{_datadir}/%{name}/bin/show-public-key.php %{buildroot}%{_bindir}/%{name}-show-public-key
ln -s %{_datadir}/%{name}/bin/sign.php %{buildroot}%{_bindir}/%{name}-sign
ln -s %{_datadir}/%{name}/bin/verify.php %{buildroot}%{_bindir}/%{name}-verify

%check
mkdir -p vendor
cat << 'EOF' | tee vendor/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Dependencies::required(array(
    '%{buildroot}%{_datadir}/%{name}/src/autoload.php',
));
\Fedora\Autoloader\Autoload::addPsr4('fkooman\\JsonSigner\\Tests\\', dirname(__DIR__) . '/tests');
EOF

%{_bindir}/phpunit --verbose

%files
%defattr(-,root,root,-)
%{_bindir}/*
%{_datadir}/%{name}/bin
%{_datadir}/%{name}/src
%doc README.md CHANGES.md composer.json
%license LICENSE

%changelog
* Tue Aug 22 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1

* Mon Aug 14 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
