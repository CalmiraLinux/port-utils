all:
	msgfmt po/ru.po

install:
	cp src/port-utils.py /usr/bin/port-utils
	chmod +x /usr/bin/port-utils
	cp config/port-utils.json /etc
	cp messages.mo /usr/share/locale/ru/LC_MESSAGES/port-utils.mo
