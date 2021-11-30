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
# Project Page: https://github.com/CalmiraLinux/port-utils
# Michail Krasnov <linuxoid85@gmail.com>
#

import os
import sys
import argparse
import gettext

import ports_base
import ports_manage
import update_ports

gettext.bindtextdomain('port-utils', '/usr/share/locale')
gettext.textdomain('port-utils')
_ = gettext.gettext

## ABOUT PROGRAM ##
PROGRAM_RELEASE = "beta build 1"
NAME_VERSION = "port-utils v1.0b1 DEV " + PROGRAM_RELEASE # Name + version

CONFIG = "/etc/port-utils.json"

def about_msg():
    title = _("About port-utils")
    about_text = _("Utilities for download, install, update, remove ports and check his changelog")

    print("{0}\n\n {1}".format(about_title, NAME_VERSION))
    print("\n", about_text)
    print(_("\n(C) Michail Krasnov <linuxoid85@gmail.com>"))

parser = argparse.ArgumentParser(description=_("port-utils - Port system software"),
                                 epilog=_("Good luck ;)"))

# Install or update Port system
parser.add_argument("--fetch", "-f",
                    type=str, help=_("Install or update Port system"), action="store_true")

# Install port package
parser.add_argument("--install", "-i", type=str,
                    help=_("Download, build and install port package"))

# Remove port
parser.add_argument("--remove", "-r", type=str,
                    help=_("Remove port package from system"))

# Show info about port package
parser.add_argument("--info", "-I", type=str,
                    help=_("Show information about port package"))

# Update the port-utils metadata
parser.add_argument("--metadata", type=str,
                    choices=["stable", "testing"], help=_("Update the port-utils metadata files"))

# About port-utils
parser.add_argument("--about", "-a", help=_("About program"), action="store_true")

args = parser.parse_args()

if args.fetch:
    # Update metadata
    config = update_ports.fetch_metadata.parse()
    branch = config["branch"]

    update_ports.fetch_metadata.get_metadata(branch)

    if update_ports.fetch_metadata.install_metadata():
        print("Updating metadata: ok")
    else:
        print("Updating metadata: FAIL")
        exit(1)
    

    # Update Port system
    update_ports.fetch_ports.get_ports()
    update_ports.fetch_ports.install_ports()

elif args.metadata:
    # Update metadata
    config = update_ports.fetch_metadata.parse()
    branch = config["branch"]

    update_ports.fetch_metadata.get_metadata(branch)

    if update_ports.fetch_metadata.install_metadata():
        print("Updating metadata: ok")
    else:
        print("Updating metadata: FAIL")
        exit(1)
