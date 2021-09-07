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
import tarfile
import gettext
import json

## BASE CONSTANTS ##
ports_PORTS = "/usr/ports"
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

    # Function for check priority of package
    # If priority = system, then package doesn't
    # can remove from Calmira GNU/Linux
    ## Priority:
    # 'system' and 'user'
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

