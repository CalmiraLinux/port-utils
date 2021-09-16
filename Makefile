update-ports:
	echo "You must be run 'make install'!"
install:
	msgfmt src/locales/ru.po -o ru.mo
	cp -v  ru.mo                 /usr/share/locale/ru_RU/LC_MESSAGES/port-utils.mo
	cp -v  src/docs/branches     /usr/share/ports/branches
	cp -v  docs/usage.html       /usr/share/ports/docs
	cp -vr docs/css              /usr/share/ports
	cp -v  src/port-utils.py     /usr/bin/port-utils

	mkdir /usr/share/ports/modules
	cp -v src/modules/ports.py   /usr/share/ports/modules/
	chmod +x /usr/bin/port-utils
	rm -v ru.mo
