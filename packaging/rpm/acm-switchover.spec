Name:           acm-switchover
Version:        1.5.0
Release:        1%{?dist}
Summary:        ACM Hub Switchover automation tool
License:        Apache-2.0
URL:            https://github.com/your-org/rh-acm-switchover
Source0:        rh-acm-switchover-%{version}.tar.gz

BuildArch:      noarch

Requires:       python3 >= 3.9
Requires:       python3-kubernetes
Requires:       python3-PyYAML
Requires:       python3-rich
Requires:       python3-tenacity

%description
Automated, idempotent tool for switchover from a primary Red Hat ACM hub to a secondary hub cluster.

%prep
%setup -q

%build
%pyproject_wheel

%install
%pyproject_install

# Install wrappers to set default state dir if unset
install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/acm-switchover << 'EOF'
#!/bin/sh
[ -r /etc/sysconfig/acm-switchover ] && . /etc/sysconfig/acm-switchover
[ -r /etc/default/acm-switchover ] && . /etc/default/acm-switchover
: "${ACM_SWITCHOVER_STATE_DIR:=/var/lib/acm-switchover}"
export ACM_SWITCHOVER_STATE_DIR
exec /usr/bin/python3 -m acm_switchover "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/acm-switchover

cat > %{buildroot}%{_bindir}/acm-switchover-rbac << 'EOF'
#!/bin/sh
[ -r /etc/sysconfig/acm-switchover ] && . /etc/sysconfig/acm-switchover
[ -r /etc/default/acm-switchover ] && . /etc/default/acm-switchover
: "${ACM_SWITCHOVER_STATE_DIR:=/var/lib/acm-switchover}"
export ACM_SWITCHOVER_STATE_DIR
exec /usr/bin/python3 -m check_rbac "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/acm-switchover-rbac

cat > %{buildroot}%{_bindir}/acm-switchover-state << 'EOF'
#!/bin/sh
[ -r /etc/sysconfig/acm-switchover ] && . /etc/sysconfig/acm-switchover
[ -r /etc/default/acm-switchover ] && . /etc/default/acm-switchover
: "${ACM_SWITCHOVER_STATE_DIR:=/var/lib/acm-switchover}"
export ACM_SWITCHOVER_STATE_DIR
exec /usr/bin/python3 -m show_state "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/acm-switchover-state

# Create state dir
install -d -m 0750 %{buildroot}/var/lib/acm-switchover

# Docs and man
install -d %{buildroot}%{_mandir}/man1
install -m 0644 packaging/common/man/acm-switchover.1.gz %{buildroot}%{_mandir}/man1/
install -m 0644 packaging/common/man/acm-switchover-rbac.1.gz %{buildroot}%{_mandir}/man1/
install -m 0644 packaging/common/man/acm-switchover-state.1.gz %{buildroot}%{_mandir}/man1/

install -d %{buildroot}%{_docdir}/%{name}
install -m 0644 README.md %{buildroot}%{_docdir}/%{name}/

# Deploy assets
install -d %{buildroot}%{_datadir}/%{name}/deploy
cp -a deploy/* %{buildroot}%{_datadir}/%{name}/deploy/

# Completions
install -d %{buildroot}%{_datadir}/bash-completion/completions
cp -a completions/* %{buildroot}%{_datadir}/bash-completion/completions/

%files
%license LICENSE
%doc %{_docdir}/%{name}/README.md
%{_bindir}/acm-switchover
%{_bindir}/acm-switchover-rbac
%{_bindir}/acm-switchover-state
%{python3_sitelib}/acm_switchover.py*
%{python3_sitelib}/check_rbac.py*
%{python3_sitelib}/show_state.py*
%{python3_sitelib}/lib/*
%{python3_sitelib}/modules/*
%{_mandir}/man1/acm-switchover.1.gz
%{_mandir}/man1/acm-switchover-rbac.1.gz
%{_mandir}/man1/acm-switchover-state.1.gz
%{_datadir}/%{name}/deploy
%{_datadir}/bash-completion/completions/*
/var/lib/acm-switchover

%changelog
* Fri Dec 12 2025 Platform Engineering <noreply@example.com> - 1.4.0-1
- Initial RPM spec skeleton with wrappers, man pages, deploy assets, and completions
