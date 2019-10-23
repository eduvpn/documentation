%global git 812f764321f53092a4a138d397386f974be05157

%if ! 0%{?gobuild:1}
%define gobuild(o:) go build -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')" -a -v -x %{?**}; 
%endif
%if ! 0%{?gotest:1}
%define gotest(o:) go test -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')" -a -v -x %{?**}; 
%endif

Name:           lc-daemon
Version:        0.0.0
Release:        0.16%{?dist}
Summary:        Daemon to manage OpenVPN for use with Let's Connect! VPN

License:        MIT
URL:            https://software.tuxed.net/lc-daemon

%if %{defined git}
Source0:        https://git.tuxed.net/LC/lc-daemon/snapshot/lc-daemon-%{git}.tar.xz
%else
Source0:        https://software.tuxed.net/lc-daemon/files/lc-daemon-%{version}.tar.xz
Source1:        https://software.tuxed.net/lc-daemon/files/lc-daemon-%{version}.tar.xz.minisig
Source2:        minisign-8466FFE127BCDC82.pub
%endif 

Source3:        %{name}.service
Source4:        %{name}.sysconfig

BuildRequires:  minisign
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%if 0%{?fedora} >= 30
BuildRequires:	systemd-rpm-macros
%else
BuildRequires:	systemd
%endif

%description
Daemon to manage OpenVPN for use with Let's Connect! VPN.

%prep
%if %{defined git}
%setup -qn lc-daemon-%{git}
%else
/usr/bin/minisign -V -m %{SOURCE0} -x %{SOURCE1} -p %{SOURCE2}
%setup -qn lc-daemon-%{version}
%endif

%build
for cmd in lc-daemon; do
  %gobuild -o _bin/$(basename $cmd) $cmd/main.go
done

%install
install -m 0755 -D _bin/%{name} %{buildroot}%{_bindir}/%{name}
install -m 0644 -D %{SOURCE3}   %{buildroot}%{_unitdir}/%{name}.service
install -m 0644 -D %{SOURCE4}   %{buildroot}%{_sysconfdir}/sysconfig/%{name}

%check
for cmd in lc-daemon; do
    %gotest $cmd/main.go $cmd/main_test.go
done

%post
%systemd_post lc-daemon.service

%preun
%systemd_preun lc-daemon.service

%postun
%systemd_postun_with_restart lc-daemon.service

%files
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_bindir}/*
%{_unitdir}/%{name}.service

%doc README.md AUTHORS.md ROADMAP.md
%license LICENSE

%changelog
* Tue Oct 22 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.16
- rebuilt

* Mon Oct 21 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.15
- rebuilt

* Mon Oct 21 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.14
- rebuilt

* Mon Oct 21 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.13
- rebuilt

* Mon Oct 21 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.12
- rebuilt

* Mon Oct 21 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.11
- rebuilt

* Mon Oct 21 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.10
- rebuilt

* Mon Oct 21 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.9
- rebuilt

* Sat Oct 19 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.8
- rebuilt

* Fri Oct 18 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.7
- rebuilt

* Fri Oct 18 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.6
- rebuilt

* Fri Oct 18 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.5
- rebuilt

* Fri Oct 18 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.4
- rebuilt

* Thu Oct 17 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.3
- rebuilt

* Thu Oct 17 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.2
- add systemd unit

* Thu Oct 10 2019 François Kooman <fkooman@tuxed.net> - 0.0.0-0.1
- initial package
