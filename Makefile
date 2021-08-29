update-ports: src/port-utils.py src/locales/ru.mo src/docs/branches
	echo "You must be run 'make install'!"

install:
	msgfmt src/locales/ru.po -o ru.mo
	cp -v ru.mo                 /usr/share/locale/ru_RU/LC_MESSAGES/port-utils.mo
	cp -v src/docs/branches     /usr/share/update-ports/branches
	cp -v src/port-utils.py     /usr/bin/port-utils

	chmod +x /usr/bin/update-ports

	rm -v ru.mo
