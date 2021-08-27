update-ports: src/update-ports.py src/locales/ru.mo src/docs/branches
	echo "You must be run 'make install'!"

install:
	if [ -f "/usr/share/update-ports" ]; then
		mkdir -v /usr/share/update-ports
	fi

	msgfmt src/locales/ru.po
	cp -v src/locales/ru.po   /usr/share/locale/ru/update-ports.mo
	cp -v src/docs/branches   /usr/share/update-ports/branches
	cp -v src/update-ports.py /usr/bin/update-ports

	chmod +x /usr/bin/update-ports
