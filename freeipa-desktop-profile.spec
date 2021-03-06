%global debug_package %{nil}
%global plugin_name desktop-profile

%if 0%{?fedora} > 26 || 0%{?rhel} > 7
%global ipa_python3_sitelib %{python3_sitelib}
%endif

Name:           freeipa-%{plugin_name}
Version:        0.0.8
Release:        2%{?dist}
Summary:        FleetCommander integration with FreeIPA

BuildArch:      noarch

License:        GPL
URL:            https://github.com/abbra/freeipa-desktop-profile
Source0:        freeipa-desktop-profile-%{version}.tar.gz

%if 0%{?fedora} > 26 || 0%{?rhel} > 7
BuildRequires: python3-devel
BuildRequires: python3-ipaserver >= 4.6.0
%endif


%if 0%{?rhel} == 7
BuildRequires: python2-devel
BuildRequires: python2-ipaserver >= 4.4.0
Requires:      ipa-server-common >= 4.4.0
%else
Requires:       ipa-server-common >= 4.4.1
%endif

# In Fedora 27 we have FreeIPA using Python 3, enforce that
# For FleetCommander also we provide Python 2 client
%if 0%{?fedora} > 26 || 0%{?rhel} > 7
Requires(post): python3-ipa-%{plugin_name}-server
Requires: python3-ipa-%{plugin_name}-server
Requires: python3-ipa-%{plugin_name}-client
%else
Requires(post): python2-ipa-%{plugin_name}-server
Requires: python2-ipa-%{plugin_name}-server
Requires: python2-ipa-%{plugin_name}-client
%endif

%description
A module for FreeIPA to allow managing desktop profiles defined
by the FleetCommander.

%package -n freeipa-%{plugin_name}-common
Summary: Common package for client side FleetCommander integration with FreeIPA
License:        GPL

%description  -n freeipa-%{plugin_name}-common
A module for FreeIPA to allow managing desktop profiles defined
by the FleetCommander. This package adds common files needed by client-side packages

%if 0%{?fedora} < 28 || 0%{?rhel} == 7
%package -n python2-ipa-%{plugin_name}-server
Summary: Server side of FleetCommander integration with FreeIPA for Python 2
License:        GPL
Requires: python2-ipaserver

%description  -n python2-ipa-%{plugin_name}-server
A module for FreeIPA to allow managing desktop profiles defined
by the FleetCommander. This package adds server-side support for Python 2
version of FreeIPA
%endif

%if 0%{?fedora} > 26 || 0%{?rhel} == 7
%package -n python2-ipa-%{plugin_name}-client
License:        GPL
Summary: Client side of FleetCommander integration with FreeIPA for Python 2
Requires: python2-ipaclient
Requires: freeipa-%{plugin_name}-common

%description  -n python2-ipa-%{plugin_name}-client
A module for FreeIPA to allow managing desktop profiles defined
by the FleetCommander. This package adds client-side support for Python 2
version of FreeIPA
%endif

%if 0%{?fedora} > 26 || 0%{?rhel} > 7
%package -n python3-ipa-%{plugin_name}-server
Summary: Server side of FleetCommander integration with FreeIPA for Python 3
License:        GPL
Requires: python3-ipaserver

%description  -n python3-ipa-%{plugin_name}-server
A module for FreeIPA to allow managing desktop profiles defined
by the FleetCommander. This package adds server-side support for Python 3
version of FreeIPA

%package -n python3-ipa-%{plugin_name}-client
License:        GPL
Summary: Client side of FleetCommander integration with FreeIPA for Python 3
Requires: python3-ipaclient
Requires: freeipa-%{plugin_name}-common

%description  -n python3-ipa-%{plugin_name}-client
A module for FreeIPA to allow managing desktop profiles defined
by the FleetCommander. This package adds client-side support for Python 3
version of FreeIPA

%endif

%prep
%autosetup

%build
touch debugfiles.list

%install
rm -rf $RPM_BUILD_ROOT
%__mkdir_p %buildroot/%{_sysconfdir}/ipa
%__mkdir_p %buildroot/%_datadir/ipa/schema.d
%__mkdir_p %buildroot/%_datadir/ipa/updates
#%__mkdir_p %buildroot/%_datadir/ipa/ui/js/plugins/deskprofile

%__cp plugin/etc/ipa/fleetcommander.conf %buildroot/%{_sysconfdir}/ipa/
sitelib2=
sitelib3=
targets2="ipaclient ipaserver"
%if 0%{?fedora} > 26 || 0%{?rhel} > 7
sitelib3="%{ipa_python3_sitelib}"
targets2="ipaclient"
targets3="ipaclient ipaserver"
%endif

if [ -n "$sitelib2" ] ; then
    for s in $targets2 ; do
        %__mkdir_p %buildroot/$sitelib2/$s/plugins
        for j in $(find plugin/$s/plugins -name '*.py') ; do
            %__cp $j %buildroot/$sitelib2/$s/plugins
        done
    done
fi

if [ -n "$sitelib3" ] ; then
    for s in $targets3 ; do
        %__mkdir_p %buildroot/$sitelib3/$s/plugins
        for j in $(find plugin/$s/plugins -name '*.py') ; do
            %__cp $j %buildroot/$sitelib3/$s/plugins
        done
    done
fi

for j in $(find plugin/schema.d -name '*.ldif') ; do
    %__cp $j %buildroot/%_datadir/ipa/schema.d
done

for j in $(find plugin/updates -name '*.update') ; do
    %__cp $j %buildroot/%_datadir/ipa/updates
done

# Do not package web UI plugin yet
#for j in $(find plugin/ui/%{plugin_name} -name '*.js') ; do
#    %__cp $j %buildroot/%_datadir/ipa/js/plugins/%{plugin_name}
#done

%posttrans
%if 0%{?fedora} > 26 || 0%{?rhel} > 7
ipa_interp=python3
%else
ipa_interp=python2
%endif
$ipa_interp -c "import sys; from ipaserver.install import installutils; sys.exit(0 if installutils.is_ipa_configured() else 1);" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    # This must be run in posttrans so that updates from previous
    # execution that may no longer be shipped are not applied.
    /usr/sbin/ipa-server-upgrade --quiet >/dev/null || :

    # Restart IPA processes. This must be also run in postrans so that plugins
    # and software is in consistent state
    # NOTE: systemd specific section

    /bin/systemctl is-enabled ipa.service >/dev/null 2>&1
    if [  $? -eq 0 ]; then
        /bin/systemctl restart ipa.service >/dev/null 2>&1 || :
    fi
fi

%files
%license COPYING
%doc plugin/Feature.mediawiki
%_datadir/ipa/schema.d/*
%_datadir/ipa/updates/*
#_datadir/ipa/ui/js/plugins/deskprofile/*

%files -n freeipa-%{plugin_name}-common
%{_sysconfdir}/ipa/fleetcommander.conf

%if 0%{?fedora} > 26 || 0%{?rhel} > 7
%files -n python3-ipa-%{plugin_name}-client
%ipa_python3_sitelib/ipaclient/plugins/*

%files -n python3-ipa-%{plugin_name}-server
%ipa_python3_sitelib/ipaserver/plugins/*
%endif

%changelog
* Sun Jul 22 2018 Alexander Bokovoy <abokovoy@redhat.com> 0.0.8-2
- Do not ship python2-ipa-deskprofile-server for Fedora 29 or later

* Tue May 29 2018 Alexander Bokovoy <abokovoy@redhat.com> 0.0.8-1
- Add a default privilege 'FleetCommander Desktop Profile Administrators'
  during upgrade

* Mon May 21 2018 Alexander Bokovoy <abokovoy@redhat.com> 0.0.7-1
- Add a default role 'FleetCommander Desktop Profile Administrators'
  during upgrade

* Thu Nov 23 2017 Oliver Gutierrez <ogutierrez@redhat.com> 0.0.6-4
- Fixed dependencies for EPEL 7

* Thu Nov 23 2017 Oliver Gutierrez <ogutierrez@redhat.com> 0.0.6-3
- Moved context configuration file to a common package for client side packages

* Mon Nov 20 2017 Oliver Gutierrez <ogutierrez@redhat.com> 0.0.6-2
- Fixed errors in specfile

* Fri Nov 17 2017 Alexander Bokovoy <abokovoy@redhat.com> 0.0.6-1
- Allow loading JSON data from files only in interactive mode
- Package Python2 and Python3 versions separately
- Package client and server side separately

* Wed Feb  8 2017 Alexander Bokovoy <abokovoy@redhat.com> 0.0.4-1
- New release
- Added global desktop profile policy

* Wed Nov  2 2016 Alexander Bokovoy <abokovoy@redhat.com> 0.0.2-1
- New release

* Tue Nov  1 2016 Fabiano Fid??ncio <fidencio@redhat.com> 0.0.1-2
- Use the same posttrans method used by FreeIPA

* Mon Sep  5 2016 Alexander Bokovoy <abokovoy@redhat.com> 0.0.1-1
- Initial release
