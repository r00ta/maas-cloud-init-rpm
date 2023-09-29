srpm:
	dnf install -y git rpm-build rpm-sign
	mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	git clone https://github.com/r00ta/cloud-init.git /tmp/cloud-init-main
	tar czf cloud-init-main.tar.gz -C /tmp cloud-init-main/
	mv cloud-init-main.tar.gz ~/rpmbuild/SOURCES/
	cp $(spec) ~/rpmbuild/SPECS/
	pwd
	ls
	ls /builddir/build/
	ls ~/rpmbuild/
	pwd ~/rpmbuild/
	rpmbuild -bs --noclean --target noarch --nodeps ~/rpmbuild/SPECS/cloud-init.spec
	cp ~/rpmbuild/SRPMS/* $(outdir)
