%define __find_requires %{nil}
%define __find_provides %{nil}

Summary: %{summary}
Name: %{name}
Version: %{version}
Release: %{release}
License: %{license}
Group: %{group}
URL: %{url}
Vendor: %{vendor}
Packager: %{packager}
Provides: %{provides}
AutoReqProv: no

%description
%{description}

%prep

%build

%install

%files
%defattr(-,root,root,-)
%{installs}

%changelog
* Mon Aug 02 2024 Breakout Scanner Global Markets
- Automatic RPM creation

%post
# Register the application with desktop environment
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications || true
fi

%postun
# Cleanup on uninstall
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications || true
fi
