update-ports: src/update-ports.py src/locales/ru.mo
	echo "You must be run 'make install'!"

install:
	msgfmt src/locales/ru.po
	cp -v src/locales/ru.po   /usr/share/locale/ru/update-ports.mo
	cp -v src/update-ports.py /usr/bin/update-ports
	chmod +x /usr/bin/update-ports
