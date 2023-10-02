%define use_systemd (0%{?fedora} && 0%{?fedora} >= 18) || (0%{?rhel} && 0%{?rhel} >= 7)

%if %{use_systemd}
%define init_system systemd
%else
%define init_system sysvinit
%endif

# See: http://www.zarb.org/~jasonc/macros.php
# Or: http://fedoraproject.org/wiki/Packaging:ScriptletSnippets
# Or: http://www.rpm.org/max-rpm/ch-rpm-inside.html

Name:           cloud-init
Version:        23.2.1
Release:        %autorelease
Summary:        Cloud instance init scripts

Group:          System Environment/Base
License:        Dual-licesed GPLv3 or Apache 2.0
URL:            https://github.com/canonical/cloud-init 

Source0:        cloud-init-main.tar.gz

BuildArch:      noarch
BuildRoot:      %{_tmppath}

%if "%{?el6}" == "1"
BuildRequires:  python-argparse
%endif
%if %{use_systemd}
Requires:           systemd
BuildRequires:      systemd
Requires:           systemd-units
BuildRequires:      systemd-units
%else
Requires:           initscripts >= 8.36
Requires(postun):   initscripts
Requires(post):     chkconfig
Requires(preun):    chkconfig
%endif

BuildRequires:  python3-devel
BuildRequires:  python3-jsonschema
BuildRequires:  python3-passlib
BuildRequires:  python3-pytest
BuildRequires:  python3-pytest-cov
BuildRequires:  python3-pytest-mock
BuildRequires:  python3-responses
BuildRequires:  python3-setuptools

# System util packages needed
%ifarch %{?ix86} x86_64 ia64
Requires:       dmidecode
%endif


# Install 'dynamic' runtime reqs from *requirements.txt and pkg-deps.json.
# Install them as BuildRequires too as they're used for testing.
BuildRequires:  e2fsprogs
Requires:       e2fsprogs
BuildRequires:  hostname
Requires:       hostname
BuildRequires:  iproute
Requires:       iproute
BuildRequires:  net-tools
Requires:       net-tools
BuildRequires:  procps
Requires:       procps
BuildRequires:  python3-configobj
Requires:       python3-configobj
BuildRequires:  python3-jinja2
Requires:       python3-jinja2
BuildRequires:  python3-jsonpatch
Requires:       python3-jsonpatch
BuildRequires:  python3-jsonschema
Requires:       python3-jsonschema
BuildRequires:  python3-netifaces
Requires:       python3-netifaces
BuildRequires:  python3-oauthlib
Requires:       python3-oauthlib
BuildRequires:  python3-pyserial
Requires:       python3-pyserial
BuildRequires:  python3-pyyaml
Requires:       python3-pyyaml
BuildRequires:  python3-requests
Requires:       python3-requests
BuildRequires:  rsyslog
Requires:       rsyslog
BuildRequires:  shadow-utils
Requires:       shadow-utils
BuildRequires:  sudo
Requires:       sudo

# Custom patches

%if "%{init_system}" == "systemd"
Requires(post):       systemd
Requires(preun):      systemd
Requires(postun):     systemd
%else
Requires(post):       chkconfig
Requires(postun):     initscripts
Requires(preun):      chkconfig
Requires(preun):      initscripts
%endif

%description
Cloud-init is a set of init scripts for cloud instances.  Cloud instances
need special scripts to run during initialization to retrieve and install
ssh keys and to let the user run various scripts.

%prep
%setup -q -n cloud-init-main

# Custom patches activation

%build
%{__python3} setup.py build

%install

%{__python3} setup.py install -O1 \
            --skip-build --root $RPM_BUILD_ROOT \
            --init-system=%{init_system}

# Note that /etc/rsyslog.d didn't exist by default until F15.
# el6 request: https://bugzilla.redhat.com/show_bug.cgi?id=740420
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/rsyslog.d
cp -p tools/21-cloudinit.conf \
      $RPM_BUILD_ROOT/%{_sysconfdir}/rsyslog.d/21-cloudinit.conf

# Remove the tests
rm -rf $RPM_BUILD_ROOT%{python3_sitelib}/tests

# Required dirs...
mkdir -p $RPM_BUILD_ROOT/%{_sharedstatedir}/cloud
mkdir -p $RPM_BUILD_ROOT/%{_libexecdir}/%{name}

# patch in the full version to version.py
version_pys=$(cd "$RPM_BUILD_ROOT" && find . -name version.py -type f)
[ -n "$version_pys" ] ||
   { echo "failed to find 'version.py' to patch with version." 1>&2; exit 1; }
( cd "$RPM_BUILD_ROOT" &&
  sed -i "s,@@PACKAGED_VERSION@@,%{version}-%{release}," $version_pys )

%clean
rm -rf $RPM_BUILD_ROOT

%post

%if "%{init_system}" == "systemd"
if [ $1 -eq 1 ]
then
    /bin/systemctl enable cloud-config.service     >/dev/null 2>&1 || :
    /bin/systemctl enable cloud-final.service      >/dev/null 2>&1 || :
    /bin/systemctl enable cloud-init.service       >/dev/null 2>&1 || :
    /bin/systemctl enable cloud-init-local.service >/dev/null 2>&1 || :
fi
%else
/sbin/chkconfig --add %{_initrddir}/cloud-init-local
/sbin/chkconfig --add %{_initrddir}/cloud-init
/sbin/chkconfig --add %{_initrddir}/cloud-config
/sbin/chkconfig --add %{_initrddir}/cloud-final
%endif

%preun

%if "%{init_system}" == "systemd"
if [ $1 -eq 0 ]
then
    /bin/systemctl --no-reload disable cloud-config.service >/dev/null 2>&1 || :
    /bin/systemctl --no-reload disable cloud-final.service  >/dev/null 2>&1 || :
    /bin/systemctl --no-reload disable cloud-init.service   >/dev/null 2>&1 || :
    /bin/systemctl --no-reload disable cloud-init-local.service >/dev/null 2>&1 || :
fi
%else
if [ $1 -eq 0 ]
then
    /sbin/service cloud-init stop >/dev/null 2>&1 || :
    /sbin/chkconfig --del cloud-init || :
    /sbin/service cloud-init-local stop >/dev/null 2>&1 || :
    /sbin/chkconfig --del cloud-init-local || :
    /sbin/service cloud-config stop >/dev/null 2>&1 || :
    /sbin/chkconfig --del cloud-config || :
    /sbin/service cloud-final stop >/dev/null 2>&1 || :
    /sbin/chkconfig --del cloud-final || :
fi
%endif

%postun

%if "%{init_system}" == "systemd"
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
%endif

%files

%{_udevrulesdir}/66-azure-ephemeral.rules

%if "%{init_system}" == "systemd"
/usr/lib/systemd/system-generators/cloud-init-generator
%{_sysconfdir}/systemd/system/sshd-keygen@.service.d/disable-sshd-keygen-if-cloud-init-active.conf
%{_unitdir}/cloud-*
%else
%attr(0755, root, root) %{_initddir}/cloud-config
%attr(0755, root, root) %{_initddir}/cloud-final
%attr(0755, root, root) %{_initddir}/cloud-init-local
%attr(0755, root, root) %{_initddir}/cloud-init
%endif

# Program binaries
%{_bindir}/cloud-init*
%{_bindir}/cloud-id*

# Docs
%doc LICENSE ChangeLog TODO.rst requirements.txt
%doc %{_defaultdocdir}/cloud-init/*

# Configs
%config(noreplace)      %{_sysconfdir}/cloud/cloud.cfg
%dir                    %{_sysconfdir}/cloud/clean.d
%config(noreplace)      %{_sysconfdir}/cloud/clean.d/README
%dir                    %{_sysconfdir}/cloud/cloud.cfg.d
%config(noreplace)      %{_sysconfdir}/cloud/cloud.cfg.d/*.cfg
%config(noreplace)      %{_sysconfdir}/cloud/cloud.cfg.d/README
%dir                    %{_sysconfdir}/cloud/templates
%config(noreplace)      %{_sysconfdir}/cloud/templates/*
%config(noreplace) %{_sysconfdir}/rsyslog.d/21-cloudinit.conf

# Bash completion script
%{_datadir}/bash-completion/completions/cloud-init

%{_libexecdir}/%{name}
%dir %{_sharedstatedir}/cloud

# Python code is here...
%{python3_sitelib}/*

