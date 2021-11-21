#!/usr/bin/python3

import os
import sys
import shutil
import tarfile
import wget
import json
import gettext
import time
import subprocess
import sqlite3

gettext.bindtextdomain('port-utils', '/usr/share/locale')
gettext.textdomain('port-utils')
_ = gettext.gettext

PORTDIR      = "/usr/ports"
PROGRAM_DIR  = "/usr/share/ports"
CACHE        = "/var/cache/ports"
DB           = "/var/db/ports/ports.db"
METADATA     = PROGRAM_DIR + "/metadata.json"
CALM_RELEASE = "/etc/calm-release"
FILES_DIR    = "/usr/share/ports"
METADATA     = FILES_DIR + "/metadata.json"
METADATA_TMP = "/tmp/metadata.json"
SETTINGS     = "/etc/port-utils.json"

class port_info():
    """Viewing port information"""

    config = [
        'name', 'version', 'description', 'maintainer',
        'priority', 'release'
    ] # Базовое содержимое конфига

    def print_item(self, msg, param, fjson) -> bool:
        self.msg = msg
        self.param = param
        self.fjson = fjson

        try:
            f = open(fjson, "r")
        except FileNotFoundError:
            print(_("File {} not found").format(fjson))
            return False
        
        data = json.load(f)

        if not data[param]:
            message = _(f"{msg}: Information is not specified")
            print(message)
            yield False
        else:
            print(f"{msg}: {data[param]}")
            yield True
        
        f.close()

    def get(self, port):
        self.port = port
        portjson = PORTDIR + "/" + port + "/config.json"

        if os.path.isfile(portjson):
            print(_("File {}not found").format(portjson))

        port_info.print_item(_("Name:"), "name", portjson)
        port_info.print_item(_("Version:"), "version", portjson)
        port_info.print_item(_("Maintainer:"), "maintainer", portjson)
        port_info.print_item(_("Priority:"), "priority", portjson)
            
