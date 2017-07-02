%global composer_vendor         SURFnet
%global composer_project        vpn-server-api
%global composer_namespace      %{composer_vendor}/VPN/Server

%global github_owner            eduvpn
%global github_name             vpn-server-api
%global github_commit           997b794e46d8f4fc4c5f100b50b60303312e1894
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       vpn-server-api
Version:    1.0.0
Release:    0.96%{?dist}
Summary:    Web service to control OpenVPN processes

Group:      Applications/Internet
License:    AGPLv3+

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz
Source1:    %{name}-httpd.conf
Source2:    %{name}.cron
BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-json
BuildRequires:  php-mbstring
BuildRequires:  php-openssl
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-spl
BuildRequires:  php-standard
BuildRequires:  %{_bindir}/phpunit
BuildRequires:  vpn-lib-common
BuildRequires:  php-composer(fedora/autoloader)
BuildRequires:  php-composer(psr/log)
BuildRequires:  php-composer(christian-riesen/otp)
BuildRequires:  php-composer(fkooman/yubitwee)
BuildRequires:  php-composer(fkooman/oauth2-client)

Requires:   crontabs
Requires:   openvpn
%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif

Requires:   php(language) >= 5.4.0
# the scripts in bin/ require the PHP CLI
Requires:   php-cli
Requires:   php-curl
Requires:   php-date
Requires:   php-json
Requires:   php-mbstring
Requires:   php-openssl
Requires:   php-pcre
Requires:   php-pdo
Requires:   php-spl
Requires:   php-standard
Requires:   vpn-lib-common
Requires:   php-composer(fedora/autoloader)
Requires:   php-composer(psr/log)
Requires:   php-composer(christian-riesen/otp)
Requires:   php-composer(fkooman/yubitwee)
Requires:   php-composer(fkooman/oauth2-client)

Requires(post): /usr/sbin/semanage
Requires(postun): /usr/sbin/semanage

%if 0%{?fedora} >= 24
Requires:   easy-rsa
%else
# EL7 has Easy RSA 2.x
Requires:   openssl
Provides:   bundled(easy-rsa) = 3.0.1
%endif

%description
VPN Server API.

%prep
%setup -qn %{github_name}-%{github_commit} 

sed -i "s|require_once sprintf('%s/vendor/autoload.php', dirname(__DIR__));|require_once '%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php';|" bin/*
sed -i "s|require_once sprintf('%s/vendor/autoload.php', dirname(__DIR__));|require_once '%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php';|" web/*.php
sed -i "s|dirname(__DIR__)|'%{_datadir}/%{name}'|" bin/*

# remove bundled Easy RSA 3.x
%if 0%{?fedora} >= 24
rm -rf easy-rsa
%endif

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('SURFnet\\VPN\\Server\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/Otp/autoload.php',
    '%{_datadir}/php/Psr/Log/autoload.php',
    '%{_datadir}/php/fkooman/YubiTwee/autoload.php',
    '%{_datadir}/php/fkooman/OAuth/Client/autoload.php',   
    '%{_datadir}/php/SURFnet/VPN/Common/autoload.php',
));
AUTOLOAD

%install
install -m 0644 -D -p %{SOURCE1} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

mkdir -p %{buildroot}%{_datadir}/%{name}
cp -pr web %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/%{name}/src/%{composer_namespace}
cp -pr src/* %{buildroot}%{_datadir}/%{name}/src/%{composer_namespace}
mkdir -p %{buildroot}%{_bindir}
(
cd bin
for phpFileName in $(ls *)
do
    binFileName=$(basename ${phpFileName} .php)
    cp -pr ${phpFileName} %{buildroot}%{_bindir}/%{name}-${binFileName}
    chmod 0755 %{buildroot}%{_bindir}/%{name}-${binFileName}
done
)

mkdir -p %{buildroot}%{_sysconfdir}/%{name}/default
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/default/config.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config

mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
ln -s ../../../var/lib/%{name} %{buildroot}%{_datadir}/%{name}/data

# Easy RSA
%if 0%{?fedora} >= 24
ln -s ../../../usr/share/easy-rsa/3 %{buildroot}%{_datadir}/%{name}/easy-rsa
%else 
cp -pr easy-rsa %{buildroot}%{_datadir}/%{name}
%endif 

# cron
mkdir -p %{buildroot}%{_sysconfdir}/cron.d
%{__install} -p -D -m 0640 %{SOURCE2} %{buildroot}%{_sysconfdir}/cron.d/%{name}

%check
mkdir vendor
cat << 'EOF' | tee vendor/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Dependencies::required(array(
    '%{buildroot}/%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php',
));
\Fedora\Autoloader\Autoload::addPsr4('SURFnet\\VPN\\Server\\Tests\\', dirname(__DIR__) . '/tests');
EOF

%{_bindir}/phpunit --verbose

%post
semanage fcontext -a -t httpd_sys_rw_content_t '%{_localstatedir}/lib/%{name}(/.*)?' 2>/dev/null || :
restorecon -R %{_localstatedir}/lib/%{name} || :

%postun
if [ $1 -eq 0 ] ; then  # final removal
semanage fcontext -d -t httpd_sys_rw_content_t '%{_localstatedir}/lib/%{name}(/.*)?' 2>/dev/null || :
fi

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/%{name}
%dir %attr(0750,root,apache) %{_sysconfdir}/%{name}/default
%config(noreplace) %{_sysconfdir}/%{name}/default/config.php
%config(noreplace) %{_sysconfdir}/cron.d/%{name}
%{_bindir}/*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/src
%{_datadir}/%{name}/web
%{_datadir}/%{name}/easy-rsa
%{_datadir}/%{name}/config
%{_datadir}/%{name}/data
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/%{name}
%doc README.md composer.json config/config.php.example CHANGES.md
%license LICENSE

%changelog
* Sun Jul 02 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.96
- rebuilt

* Sun Jun 25 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.95
- rebuilt

* Sun Jun 25 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.94
- rebuilt

* Mon Jun 19 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.93
- rebuilt

* Sat Jun 10 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.92
- rebuilt

* Sat Jun 10 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.91
- rebuilt

* Sat Jun 10 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.90
- rebuilt

* Fri Jun 09 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.89
- rebuilt

* Fri Jun 09 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.88
- rebuilt

* Fri Jun 09 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.87
- rebuilt

* Thu Jun 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.86
- rebuilt

* Thu Jun 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.85
- rebuilt

* Wed Jun 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.84
- rebuilt

* Wed Jun 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.83
- rebuilt

* Wed Jun 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.82
- rebuilt

* Sun May 14 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.81
- rebuilt

* Sun May 14 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.80
- rebuilt

* Sat May 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.79
- rebuilt

* Sat May 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.78
- rebuilt

* Sat May 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.77
- rebuilt

* Fri May 12 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.76
- rebuilt

* Fri May 12 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.75
- rebuilt

* Tue May 09 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.74
- rebuilt

* Tue May 09 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.73
- rebuilt

* Mon May 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.72
- rebuilt

* Sat May 06 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.71
- rebuilt

* Sun Apr 30 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.70
- rebuilt

* Sun Apr 23 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.69
- rebuilt

* Sun Apr 23 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.68
- rebuilt

* Sat Apr 22 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.67
- rebuilt

* Sat Apr 22 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.66
- rebuilt

* Sat Apr 22 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.65
- rebuilt

* Fri Apr 21 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.64
- rebuilt

* Fri Apr 21 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.63
- rebuilt

* Fri Apr 21 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.62
- rebuilt

* Mon Apr 17 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.61
- rebuilt

* Thu Apr 13 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.60
- rebuilt

* Tue Apr 11 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.59
- rebuilt

* Fri Mar 31 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.58
- rebuilt

* Wed Mar 29 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.57
- rebuilt

* Thu Mar 16 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.56
- rebuilt

* Wed Mar 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.55
- rebuilt

* Wed Mar 08 2017 François Kooman <fkooman@tuxed.net>
- rebuilt

* Tue Feb 07 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.53
- rebuilt

* Sun Jan 22 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.52
- rebuilt

* Tue Jan 17 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.51
- rebuilt

* Thu Jan 05 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.50
- rebuilt

* Wed Jan 04 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.49
- rebuilt

* Wed Jan 04 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.48
- rebuilt

* Wed Jan 04 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.47
- rebuilt

* Tue Jan 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.46
- rebuilt

* Tue Jan 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.45
- rebuilt

* Tue Jan 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.44
- rebuilt

* Tue Jan 03 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.43
- rebuilt

* Thu Dec 29 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.42
- rebuilt

* Wed Dec 28 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.41
- rebuilt

* Wed Dec 28 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.40
- rebuilt

* Mon Dec 19 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.39
- rebuilt

* Mon Dec 19 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.38
- rebuilt

* Fri Dec 16 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.37
- rebuilt

* Fri Dec 16 2016 François Kooman <fkooman@tuxed.net> - 1.0.0-0.36
- rebuilt
