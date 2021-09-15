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
        ports_PORTINSTALL = ports_PORTNAME + "/install"
        ports_PORTREMOVE = ports_PORTNAME + "/remove"

        for file in ports_PORTJSON, ports_PORTINSTALL:
            print(_("checking {}...").format(file), end = " ")
            if os.path.isfile(file):
                print(OK_MSG)
            else:
                print(FAIL_MSG)
                return 1
        
        print(_("checking {}...").format(ports_PORTREMOVE), end = " ")
        if os.path.isfile(ports_PORTREMOVE):
            print(OK_MSG)
            return 0
        else:
            print(_("WARNING: there is no file with instructions to remove the port."))

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

    On success:
        return code = 0

    On failure:
        return code = 1
    """
    def build_port(port):
        print(_("Checking for build instructions..."), end = " ")

        ports_PORTNAME = ports_PORTS + "/" + port
        ports_PORTBUILD = ports_PORTNAME + "/install" # Build instructions

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
    Function for remove port from system

    Synopsis:
        port.remove_port(name)

            * name - port name

    On success:
        return code = 0

    On failure:
        return code = 1
    """
    def remove_port(port):
        ports_PORTREMOVE = ports_PORTS + "/" + port + "/remove"

        if port.check_port(port):
            port_remove = subprocess.call(ports_PORTREMOVE, shell=True)

            if port_remove.returncode == 0:
                return 0
            else:
                return 1

    """
    Function for add port in database.

    Synopsis:
        port.port_add_in_db(name)

        * name - port name (e.g. base/editors/vim)

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
    def port_add_in_db(port):
        ports_PORTNAME = ports_PORTS + "/" + port
        port_json = ports_PORTNAME + "/config.json"
        
        print(_("Database initialization..."), end = " ")

        # Проверка на наличие базы данных
        if os.path.isfile(ports_DATABASE):
            print(OK_MSG)
        else:
            print(FAIL_MSG)
            files.create_db(ports_DATABASE)

        # Проверка на наличие config.json
        print(_("Checking for port data..."), end = " ")
        if files.check_port_file(port_json, "file"):
            print(OK_MSG)
        else:
            print(FAIL_MSG)
            exit(1)
        
        port_data = json.load(open(port_json))
        PortJson = [(port_data["name"], port_data["version"], port_data["maintainer"],
                     port_data["description"], port_data["priority"], port_data["files"])]

        cursor.executemany("INSERT INTO ports VALUES (?,?,?,?,?,?)", PortJson)
        conn.commit()

        return 0

class service(object):
    # Checking to run a function as root
    def getRoot(mode):
        GID = os.getgid()
        if mode == "check":
            if GID != 0:
                print(_("\033[31mError: you must run this script as root!\033[0m"))
                exit(1)

        elif mode == "return":
            if GID != 0:
                return(1)
            else:
                return(0)

        else:
            print(_("Uknown option 'getRoot()' for 'mode'!"))
            exit(1)

    # Getting the current date and time
    def getDate():
        return datetime.fromtimestamp(1576280665)

    # Logging
    def log_msg(message, status):
        if Other.getRoot("return"):
            f = open(LOGFILE, "a")
            for index in message:
                f.write(index)

        else:
            pass

    # Checking for the existence of required directories
    def checkDirs(mode):
        if mode == "tree":
            for DIR in "/var/cache/ports", "/usr/ports":
                if os.path.isdir(DIR):
                    print(_("Directory {0} exists."), DIR)
                else:
                    print(_("Directory {} does not exist, creating a new one."), DIR)
                    os.makedirs(DIR)

        elif mode == "news":
            if os.path.isdir("/var/cache/ports"):
                print(_("Directory /var/cache/ports exists."))
            else:
                print(_("Directory /var/cache/ports does not exist, creating a new one"))
                os.makedirs("/var/cache/ports")
        else:
            exit(1)


    # Receiving system data
    # TODO - use to download ports for a specific version of the distribution
    def getSystem():
        sysData = "/etc/calm-release"

        if os.path.isfile(sysData):
            pass
        else:
            print(_("Error: the file with distribution data does not exist, or there is no access to read it. Exit."))
            exit(1)

        with open(sysData, 'r') as f:
            systemData = json.loads(f.read())

        return systemData["distroVersion"]

    # Outputting debug messages
    def printDbg(message):
        if args.debug == "yes":
            # Display messages on screen
            print(message)
        elif args.debug == "no":
            # Log messages
            f = open("/var/log/update-ports-dbg.log", "a")

            for index in message:
                f.write(index)

            f.close()
        else:
            pass

########################################################################
##                                                                    ##
## Basic functions for installing, removing and viewing port information ##
##                                                                    ##
########################################################################

# Function for install port
def InstallPortPKG(port):
    service.printDbg("Checking for the existence of a port")
    if port.check_port(port):
        service.printDbg(" OK\nBuilding port")
        port.build_port(port)

        service.printDbg("\nAdding a port to the database")
        port.port_add_in_db(port)

# Проверка на импорт
if __name__ == "__main__":
    print(_("The executable Port module must be imported."))
    log_msg("ERROR: Attempting to directly launch a module")
    sys.exit(1)