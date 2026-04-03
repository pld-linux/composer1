#
# Conditional build:
%bcond_with	tests		# build with tests
%bcond_with	online		# online self-test

%if 0%{?_pld_builder:1}
%undefine	with_online
%endif

%define		php_min_version 5.3.4
%define		upstream_name	composer
Summary:	Dependency Manager for PHP (legacy 1.x branch)
Name:		composer1
Version:	1.10.26
Release:	1
License:	MIT
Group:		Development/Languages/PHP
Source0:	https://github.com/composer/composer/archive/%{version}/%{upstream_name}-%{version}.tar.gz
# Source0-md5:	170c36246e52522e17540a6aaee57d8c
Source2:	https://raw.githubusercontent.com/iArren/composer-bash-completion/86a8129/composer
# Source2-md5:	cdeebf0a0da1fd07d0fd886d0461642e
Source3:	autoload.php
Patch0:		autoload.patch
Patch1:		update-memory-limit.patch
Patch2:		svn-ignore-externals.patch
URL:		https://getcomposer.org/
BuildRequires:	php-devel
BuildRequires:	rpm-php-pearprov >= 4.4.2-11
BuildRequires:	rpmbuild(macros) >= 1.673
%{?with_online:BuildRequires:	%{php_name}-cli}
%if %{with tests}
BuildRequires:	composer >= 1.7.0
BuildRequires:	git-core
BuildRequires:	phpab
BuildRequires:	phpunit >= 4.8
%endif
Requires:	php(core) >= %{php_min_version}
Requires:	php(ctype)
Requires:	php(date)
Requires:	php(filter)
Requires:	php(hash)
Requires:	php(json)
Requires:	php(openssl)
Requires:	php(pcntl)
Requires:	php(pcre)
Requires:	php(phar)
Requires:	php(posix)
Requires:	php(simplexml)
Requires:	php(spl)
Requires:	php(zip)
Requires:	php(zlib)
Requires:	php-composer-ca-bundle >= 1.0.2
Requires:	php-composer-semver >= 1.0.0
Requires:	php-composer-spdx-licenses >= 1.2
Requires:	php-composer-xdebug-handler >= 1.1
Requires:	php-justinrainbow-json-schema >= 3.0
Requires:	php-psr-log >= 1.0
Requires:	php-seld-jsonlint >= 1.4
Requires:	php-seld-phar-utils >= 1.0.0
Requires:	php-symfony2-ClassLoader >= 2.7.7
Requires:	php-symfony2-Console >= 2.7.7
Requires:	php-symfony2-Filesystem >= 2.7.7
Requires:	php-symfony2-Finder >= 2.7.7
Requires:	php-symfony2-Process >= 2.7.7
Requires:	unzip
Suggests:	bash-completion-%{name}
Suggests:	git-core
Suggests:	mercurial
Suggests:	subversion
Conflicts:	composer
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Composer is a tool for dependency management in PHP.

Composer helps you declare, manage and install dependencies of PHP
projects, ensuring you have the right stack everywhere.

This is the legacy 1.x branch for environments running PHP < 7.2.5.
For PHP >= 7.2.5 environments use the composer (2.x) package instead.

%package -n bash-completion-%{name}
Summary:	Bash completion for Composer 1
Summary(pl.UTF-8):	bashowe uzupełnianie nazw dla Composera 1
Group:		Applications/Shells
Requires:	%{name}
Requires:	bash-completion >= 2.0

%description -n bash-completion-%{name}
Bash completion for Composer 1 package and dependency manager.

%description -n bash-completion-%{name} -l pl.UTF-8
Pakiet ten dostarcza bashowe uzupełnianie nazw dla Composera 1.

%prep
%setup -q -n %{upstream_name}-%{version}
%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1

mv composer.lock{,.disabled}
# NOTE: do not use %{__php} macro here, need unversioned php binary
%{__sed} -i -e '1s,^#!.*env php,#!/usr/bin/php,' bin/*

cp -p %{SOURCE3} src/Composer/autoload.php

# AutoloadGenerator needs this runtime
mv LICENSE res

# move to Composer dir, this will simplify testing
mv res src/Composer
ln -s src/Composer/res

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

%build
%if %{with online}
# always run self-test
%{__php} ./bin/composer diagnose
%endif

%if %{with tests}
phpab -n -o src/bootstrap.php -e '*/Fixtures/*' src/ tests/
echo "require 'src/Composer/autoload.php';" >> src/bootstrap.php
phpunit
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{php_data_dir}/Composer,/var/cache/composer}
cp -a src/Composer $RPM_BUILD_ROOT%{php_data_dir}
install -p bin/composer $RPM_BUILD_ROOT%{_bindir}/composer

install -d $RPM_BUILD_ROOT%{bash_compdir}
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{bash_compdir}/composer

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md CHANGELOG.md
%doc src/Composer/res/LICENSE
%attr(755,root,root) %{_bindir}/composer
%{php_data_dir}/Composer

# top level cachedir, create user cache dirs here manually
%dir %attr(711,root,http) /var/cache/composer

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
%{bash_compdir}/composer
