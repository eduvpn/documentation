%global github_owner            fkooman
%global github_name             php-saml-ds
%global github_commit           37d4d692553e91ea9143629c2ba84fc269b40379
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       php-saml-ds
Version:    1.0.3
Release:    3%{?dist}
Summary:    SAML Discovery Service

Group:      Applications/Internet
License:    ASL2.0

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz
Source1:    %{name}-httpd.conf

BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

BuildRequires:  %{_bindir}/phpunit
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-curl
BuildRequires:  php-filter
BuildRequires:  php-pecl-imagick
BuildRequires:  php-json
BuildRequires:  php-pcre
BuildRequires:  php-spl
BuildRequires:  php-xml
BuildRequires:  php-composer(twig/twig) < 2
BuildRequires:  php-composer(fkooman/secookie)
BuildRequires:  php-composer(fedora/autoloader)

Requires:   php(language) >= 5.4.0
Requires:   php-curl
Requires:   php-filter
Requires:   php-pecl-imagick
Requires:   php-json
Requires:   php-pcre
Requires:   php-spl
Requires:   php-xml
Requires:   php-composer(twig/twig) < 2
Requires:   php-composer(fkooman/secookie)
Requires:   php-composer(fedora/autoloader)
%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif

%description
SAML Discovery Service written in PHP.

%prep
%setup -qn %{github_name}-%{github_commit} 

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('fkooman\\SAML\\DS\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/Twig/autoload.php',
    '%{_datadir}/php/fkooman/SeCookie/autoload.php',
));
AUTOLOAD

%install
install -m 0644 -D -p %{SOURCE1} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}

cp -pr bin src web views %{buildroot}%{_datadir}/%{name}
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/config.php

chmod +x %{buildroot}%{_datadir}/%{name}/bin/generate.php

ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config
ln -s ../../../var/lib/%{name} %{buildroot}%{_datadir}/%{name}/data
ln -s %{_datadir}/%{name}/bin/generate.php %{buildroot}%{_bindir}/%{name}-generate

%post
# remove template cache if it is there
rm -rf %{_localstatedir}/lib/%{name}/tpl/* >/dev/null 2>/dev/null || :

%check
mkdir -p vendor
cat << 'EOF' | tee vendor/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Dependencies::required(array(
    '%{buildroot}%{_datadir}/%{name}/src/autoload.php',
));
\Fedora\Autoloader\Autoload::addPsr4('fkooman\\SAML\\DS\\Tests\\', dirname(__DIR__) . '/tests');
EOF

%{_bindir}/phpunit --verbose

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/config.php
%{_bindir}/*
%{_datadir}/%{name}/bin
%{_datadir}/%{name}/src
%{_datadir}/%{name}/web
%{_datadir}/%{name}/data
%{_datadir}/%{name}/views
%{_datadir}/%{name}/config
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/%{name}
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE

%changelog
* Tue Aug 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.3-3
- update httpd snippet

* Mon Aug 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.3-2
- remove the tpl directory when upgrading

* Mon Aug 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.3-1
- update to 1.0.3

* Fri Jul 28 2017 François Kooman <fkooman@tuxed.net> - 1.0.2-1
- update to 1.0.2

* Wed Jul 19 2017 François Kooman <fkooman@tuxed.net> - 1.0.1-1
- update to 1.0.1
- rework autoloader

* Fri Jun 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-1
- initial package
