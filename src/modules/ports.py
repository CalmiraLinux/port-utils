#!/usr/bin/python3
#
# port-utils - Port system software
# Copyright (C) 2021 Michail Krasnov
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Project Page: http://github.com/CalmiraLinux/port-utils
# Michail Krasnov <linuxoid85@gmail.com>
#

import os
import sys
import json
import subprocess
import sqlite3
import gettext

gettext.bindtextdomain('port-utils', '/usr/share/locale')
gettext.textdomain('port-utils')
_ = gettext.gettext

# TODO - добавить переводы gettext

## BASE CONSTANTS ##
ports_PORTS = "/usr/ports"
ports_DATABASE = "/var/db/ports/ports.db"

## BASE MESSAGES ##
OK_MSG = "\033[32mOK\033[0m"
FAIL_MSG = "\033[31mFAIL\033[0m"


## BASE FUNCTIONS ##

##################################
##                              ##
## Class for working with files ##
##                              ##
##################################
class files(object):
    # Checking for the existence of a port file
    def check_port_file(port_file, mode):
        if mode == "dir":
            file_test = os.path.isdir(port_file)
        elif mode == "file":
            file_test = os.path.isfile(port_file)
        else:
            print(_("'check_port_file': Error: Option {} does not exist!").format(mode))
            exit(1)

        if file_test:
            print(OK_MSG)
            return 0
        else:
            print(FAIL_MSG)
            return 1

    # Create database
    def create_db(db):
        if files.check_port_file(db, "file"):
            return 1
        else:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()

            cursor.execute("""
                            CREATE TABLE ports (
                                name TEXT, version TEXT, maintainer TEXT,
                                description TEXT, priority TEXT, files TEXT
                            );
                            INSERT INTO ports VALUES (
                                'ports', 'lx4/1.1', 'Linuxoid85, 'Ports system for Calmira',
                                'user', '/usr/ports'
                            );
                           """)
            conn.commit()


##################################
##                              ##
## Class for working with ports ##
##                              ##
##################################
class port(object):
    # Checking for the existence of a port
    def check_port(port):
        print(_("Checking for the existence of a port {} ...").format(port), end = " ")

        ports_PORTNAME = ports_PORTS + "/" + port
        ports_PORTJSON = ports_PORTNAME + "/config.json"

        if os.path.isdir(ports_PORTNAME):
            if os.path.isfile(ports_PORTJSON):
                print(OK_MSG)
                return 0
            else:
                print(FAIL_MSG)

                print(_("\033[1m\033[31mError: port data file does not exist\033[0m"))
                return 1
        else:
            print(_("\033[1m\033[31mError: the directory with the port \033[0m\033[35m'{}'\033[0m\033[1m\033[31m does not exist\033[0m").format(port))
            return 1

    """
    Function for check priority of port.
    If priority = 'system', then package doesn't
    can remove from Calmira GNU/Linux.

    PRIORITY:
        * 'system',
        * 'user'

    On success:
        return code = 0

    On failure:
        return code = 1
    """
    def check_priority(port):
        print(_("Port {} priority check...").format(port), end = " ")

        ports_PORTNAME = ports_PORTS + "/" + port
        ports_PORTJSON = ports_PORTNAME + "/config.json"

        if check_port_file(ports_PORTJSON):
            with open(ports_PORTJSON, 'r') as f:
                package_data = json.load(f.read())

                if package_data["priority"] == "system":
                    return 1
                elif package_data["priority"] == "user":
                    return 0
                else:
                    print(_("'check_priority': Error: priority {} does not exist!").format(package_data["priority"]))
                    exit(1)

        else:
            exit(1)

    """
    Function for run make port

    Mode:
        * 'quiet' - minimum of messages displayed on the screen;
        * 'nonquiet' - output all assembly messages to the screen.

    On success:
        return code = 0

    On failure:
        return code = 1
    """
    def build_port(port, mode):
        print(_("Checking for build instructions..."), end = " ")

        ports_PORTNAME = ports_PORTS + "/" + port
        ports_PORTBUILD = ports_PportsORTNAME + "/install" # Build instructions

        if files.check_port_file(ports_PORTBUILD, "file"):
            print(OK_MSG)
        else:
            print(FAIL_MSG)
            exit(1)

        port_build = subprocess.run(ports_PORTBUILD, shell=True)

        # Проверка на корректное выполнение
        if port_build.returncode == 0:
            return 0
        else:
            return 1

    """
    Function for add port in database.

    Modules:
        * 'json' - for parse config.js;
        * 'sqlite3' - for adding config.js data in database.

    Return codes:
        * 0 - success;
        * 1 - uknown error

    Files:
        * 'config.json' - port data;
        * '/var/db/ports/ports.db' - ports database.
    """
    def port_add_in_db(port_json):
        print(_("Database initialization..."), end = " ")

        # Проверка на наличие базы данных
        if os.path.isfile(ports_DATABASE):
            print(OK_MSG)
        else:
            print(FAIL_MSG)
            files.create_db(ports_DATABASE)

        # Проверка на наличие config.json
        print(_("Checking for port data..."), end = " ")
        if files.check_p(port_json, "file"):
            print(OK_MSG)
        else:
            print(FAIL_MSG)
            exit(1)

        with open(port_json) as f:
            port_data = json.load(f.read())

        PortJson = [(port_data["name"], port_data["version"], port_data["maintainer"],
                     port_data["description"], port_data["priority"], port_data["files"])]

        cursor.executemany("INSERT INTO ports VALUES (?,?,?,?,?,?)", PortJson)
        conn.commit()

        return 0

