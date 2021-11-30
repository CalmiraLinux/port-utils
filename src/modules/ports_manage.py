#!/usr/bin/python3
# Модуль с функциями, предназначенными для управления пакетами
# системы портов
# (C) 2021 Михаил Краснов <linuxoid85@gmail.com>

import os
import sys
import shutil
import json
import gettext
import time
import subprocess
import sqlite3

import ports_default

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

        try:
            print(f"[{msg}]: {data[param]}")
            f.close()

            return True

        except KeyError:
            message = _(f"[{msg}]: Information is not specified")
            print(message)
            f.close()

            return False

    def get(self, port):
        self.port = port
        portjson = PORTDIR + "/" + port + "/config.json"

        if os.path.isfile(portjson):
            print(_("File {}not found").format(portjson))

        port_info.print_item(_("Name:"), "name", portjson)
        port_info.print_item(_("Version:"), "version", portjson)
        port_info.print_item(_("Maintainer:"), "maintainer", portjson)
        port_info.print_item(_("Priority:"), "priority", portjson)
            
class build_ports():
    def check(self, port, mode) -> bool:
        """
        Checking the port.

        Usage:
        `build_ports.check(port, mode)`

        - port - port name (e.g. `base/editors/vim`);
        - mode - work mode.

        Work modes:
        - install,
        - remove.
        """

        self.port = port
        self.mode = mode

        match mode:
            case "install":
                check_files = [ 'config.json', 'install' ]
            case "remove":
                check_files = [ 'config.json', 'remove' ]
        
        check_dir = PORTDIR + "/" + port

        for file in check_files:
            check_file = check_dir + "/" + file
            if os.path.isfile(check_file):
                return True
            else:
                return False
    
    def get_release(self, port):
        """
        Function for get CalmiraLinux release value from port config

        Usage:
        `build_ports.get_release(port)`

        - port - port name (e.g. 'base/editors/vim')
        """

        self.port = port

        port_dir = PORTDIR + "/" + port
        port_config = port_dir + "/config.json"

        f = open(port_config)
        data = json.load(f)
        release = data["release"]

        f.close()
        return release
    
    def get_calm_release(self):
        """ Get CalmiraLinux release number """

        f = open(CALM_RELEASE)
        data = json.load(f)
        distro_version = data["distroVersion"]

        f.close()
        return distro_version
    
    def build(self, port):
        """
        Function for build port package and install this.

        Usage:

        `build_ports.build(port)`

        - port - port name (e.g. 'base/editors/vim')
        """

        self.port = port

        port_dir = PORTDIR + "/" + port
        port_config = port_dir + "/config.json"
        port_install = port_dir + "/install"

        if build_ports.check(port, "install"):
            print(_("Port '{0}' found in {1}").format(port, PORTDIR))

            port_release = build_ports.get_release(port)
            calm_release = build_ports.get_calm_release()

            if port_release != calm_release:
                print(_("[WARNING] - this port may NOT be intended for installation on this version of the operating system. If you are not sure that it will work correctly in CalmiraLinux {}, then answer 'n'!").format(CALM_RELEASE))

                port_defaults.dialog_msg(_("Continue building (POTENTIALLY UNSAFE)?"), return_code=1)
            else:
                print(_("This port is compatible with the installed CalmiraLinux release ;-) !"))

                if not port_defaults.dialog_msg(_("Continue?")):
                    exit(1)

        else:
            print(_("Port '{0}' NOT fount in {1}").format(port, PORTDIR))
            exit(1)

        build = subprocess.run(port_install, shell=True)

        if build.returncode == 0:
            print(_("\n\n\033[1m\033[32mOperation success!\033[0m")
        else:
            print(_("\n\n\033[1m\033[31mOperation FAIL!\033[0m"))
            print(_("\033[1mReturncode:\033[0m {}").format(build.returncode))

        return build.returncode
    
    def add_in_db(self, port):
        """
        Function for addint the port in ports database.

        Usage:
        `build_ports.add_in_db(port)`

        - port - portname (e.g. 'base/editors/vim')
        """

        self.port = port

        port_dir = PORTDIR + "/" + port
        port_config = port_dir + "/config.json"
        add_time = time.ctime() # Время добавления порта в базу данных. Пусть равняется времени вызова этой функции.

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        if not os.path.isfile(port_config):
            print(_("File '{0}' NOT found in {1}").format(port_config, port_dir))
            exit(1)
        
        f = open(port_config)
        data = json.load(f)

        register = [(
            data["name"], data["version"], data["maintainer"], data["release"], add_time
        )] # Запись, которая отправится в БД

        try:
            cursor.execute("INSERT INTO ports VALUES (?,?,?,?,?)", register)
            conn.commit()
        except:
            print(_("Unknown error while adding port '{0}' to the database").format(port))
            exit(1)
    
    def remove(self, port):
        """
        Function for remove port package from system

        Usage:
        `build_ports.remove(port)`

        - port - port name (e.g. 'base/editors/vim')
        """

        self.port = port

        port_dir = PORTDIR + "/" + port
        port_config = port_dir + "/config.json"
        port_remove = port_dir + "/remove"

        if build_ports.check(port, "remove"):
            print(_("Port '{0}' found in {1}").format(port, PORTDIR))
        else:
            print(_("Port '{0}' NOT found in {1}").format(port, PORTDIR))
            exit(0)
        
        remove = subprocess.run(port_remove, shell=True)

        if remove.returncode == 0:
            print(_("\n\n\033[1m\033[32mOperation success!\033[0m"))
        else:
            print(_("\n\n\033[1m\033[31mOperation FAIL!\033[0m"))
        
        return remove.returncode
    
    def remove_from_db(self, name):
        """
        Function for remove port information from ports database.

        Usage:
        `build_ports.remove_from_db(name)`

        - name - port name (e.g. 'base/editors/vim')
        """

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        command = "DELETE from ports WHERE name = '" + name + "'"

        try:
            cursor.execute(command)
            conn.commit()
        except:
            print(_("Error while removing package '{}' from database!").format(name))
            exit(1)
