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
import argparse
import shutil
import tarfile
import requests
import gettext
import json
from datetime import datetime
from tkinter import *
import tkinter as tk

## BASE CONSTANTS ##
ports_PORTS = "/usr/ports"
OK_MSG = "\033[32mOK\033[0m"
FAIL_MSG = "\033[31mFAIL\033[0m"

# Проверка на существование порта
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
