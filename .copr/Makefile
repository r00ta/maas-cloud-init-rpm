srpm:
	dnf install -y git rpm-build rpm-sign
	git clone https://github.com/r00ta/cloud-init.git /tmp/cloud-init-main
	tar czf cloud-init-main.tar.gz -C /tmp cloud-init-main/
	mv cloud-init-main.tar.gz /builddir/build/SOURCES/
	echo "d /run/cloud-init 0700 root root - -" > /builddir/build/SOURCES/cloud-init-tmpfiles.conf
	cp $(spec) /builddir/build/SPECS/
	rpmbuild -bs --noclean --target noarch --nodeps /builddir/build/SPECS/cloud-init.spec
	cp /builddir/build/SRPMS/* $(outdir)
