%global composer_vendor         fkooman
%global composer_project        php-saml-ds
%global composer_namespace      fkooman/SAML/DS

%global github_owner            fkooman
%global github_name             php-saml-ds
%global github_commit           46be31b216f1d8fd406779a26875a37414e13302
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       php-saml-ds
Version:    1.0.0
Release:    0.46%{?dist}
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
BuildRequires:  php-date
BuildRequires:  php-filter
BuildRequires:  php-pecl-imagick
BuildRequires:  php-json
BuildRequires:  php-pcre
BuildRequires:  php-spl
BuildRequires:  php-xml
BuildRequires:  php-composer(twig/twig) < 2
BuildRequires:  php-composer(fedora/autoloader)

Requires:   php(language) >= 5.4.0
Requires:   php-curl
Requires:   php-date
Requires:   php-filter
Requires:   php-pecl-imagick
Requires:   php-json
Requires:   php-pcre
Requires:   php-spl
Requires:   php-xml
Requires:   php-composer(twig/twig) < 2
Requires:   php-composer(fedora/autoloader)
%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif

Requires(post): /usr/sbin/semanage
Requires(postun): /usr/sbin/semanage

%description
SAML Discovery Service written in PHP.

%prep
%setup -qn %{github_name}-%{github_commit} 

sed -i "s|require_once sprintf('%s/vendor/autoload.php', dirname(__DIR__));|require_once '%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php';|" bin/*
sed -i "s|require_once sprintf('%s/vendor/autoload.php', dirname(__DIR__));|require_once '%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php';|" web/*.php
sed -i "s|dirname(__DIR__)|'%{_datadir}/%{name}'|" bin/*

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('fkooman\\SAML\\DS\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/Twig/autoload.php',
));
AUTOLOAD

%install
install -m 0644 -D -p %{SOURCE1} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

mkdir -p %{buildroot}%{_datadir}/%{name}
cp -pr web views %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/%{name}/src/%{composer_namespace}
cp -pr src/* %{buildroot}%{_datadir}/%{name}/src/%{composer_namespace}
mkdir -p %{buildroot}%{_bindir}
(
cd bin
for phpFileName in $(ls *)
do
    binFileName=$(basename ${phpFileName} .php)
    install -Dpm755 ${phpFileName} %{buildroot}%{_bindir}/%{name}-${binFileName}
done
)

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/config.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config

mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
ln -s ../../../var/lib/%{name} %{buildroot}%{_datadir}/%{name}/data

%check
mkdir vendor
cat << 'EOF' | tee vendor/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Dependencies::required(array(
    '%{buildroot}/%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php',
));
\Fedora\Autoloader\Autoload::addPsr4('fkooman\\SAML\\DS\\Tests\\', dirname(__DIR__) . '/tests');
EOF

%{_bindir}/phpunit --verbose

%post
semanage fcontext -a -t httpd_sys_rw_content_t '%{_localstatedir}/lib/%{name}(/.*)?' 2>/dev/null || :
restorecon -R %{_localstatedir}/lib/%{name} || :
# remove template cache if it is there
rm -rf %{_localstatedir}/lib/%{name}/tpl/* >/dev/null 2>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then  # final removal
semanage fcontext -d -t httpd_sys_rw_content_t '%{_localstatedir}/lib/%{name}(/.*)?' 2>/dev/null || :
fi

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/config.php
%{_bindir}/*
%{_datadir}/%{name}/src
%{_datadir}/%{name}/web
%{_datadir}/%{name}/data
%{_datadir}/%{name}/views
%{_datadir}/%{name}/config
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/%{name}
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE

%changelog
* Thu Apr 27 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.46
- rebuilt

* Wed Apr 19 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.45
- rebuilt

* Wed Apr 19 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.44
- rebuilt

* Wed Apr 19 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.43
- rebuilt

* Sun Apr 16 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.42
- rebuilt

* Sun Apr 16 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.41
- rebuilt

* Fri Apr 14 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.40
- rebuilt

* Fri Apr 14 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.39
- rebuilt

* Tue Mar 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.1
- initial package
