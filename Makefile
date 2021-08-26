update-ports: src/update-ports.py
	echo "You must be run 'make install'!"

install:
	cp -v src/update-ports.py /usr/bin/update-ports
	chmod +x /usr/bin/update-ports
