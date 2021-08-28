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
import argparse
import shutil
import tarfile
import requests
from datetime import datetime
import gettext
import json
from tkinter import *
import tkinter as tk

## Base Variables
NAME_VERSION="port-utils v0.2 DEV"
LOGFILE = "/var/log/port-utils.log"
PORTDIR = "/usr/ports" # Ports directory
CACHE = "/var/cache/ports" # Cache directory
CACHE_FILE = CACHE + "/ports.txz" # Downloaded package with ports
CACHE_PORT_DIR = CACHE + "/ports" # Ports unpacked to cache
PORT = CACHE_PORT_DIR + "/ports"  # Ports to install in /usr/ports

## getext
gettext.bindtextdomain('port-utils', '/usr/share/locale')
gettext.textdomain('port-utils')
_ = gettext.gettext

# Проверка на запуск от root
GID = os.getgid()

if GID != 0:
    print(_("Error: you must run this script as root!"))
    exit(1)

# Проверка на импортирование
if __name__ != "__main__":
    print(_("The executable Port module must not be imported."))
    sys.exit(1)


##########################
##                      ##
## Command line parsing ##
##                      ##
##########################

parser = argparse.ArgumentParser(description='port-utils - Port system software',
                                 epilog="Good luck ;)")

# Net branch
parser.add_argument("--tree", "-t",
                    choices=["stable", "testing"],
                    type=str, help="Net branch from which ports are update")

# Debug mode
parser.add_argument("--debug", "-d",
                    choices=["yes", "no"],
                    type=str, help="Displaying debug messages")

# Clean
parser.add_argument("--clear",
                    choices=["cache", "log", "src", "all"],
                    type=str, help="Cleaning the system from old ports files")

# Read news

parser.add_argument("--news",
                    choices=["stable", "testing"], help="Read news of ports")

# About

parser.add_argument("--about", "-a",
                    choices=["gui", "cli"], type=str, help="About program")


args = parser.parse_args()

####################
##                ##
## Main functions ##
##                ##
####################

# Window functions
class Window(object):
    # About window
    def about(mode):
        if mode == "gui":
            window = tk.Tk()

            window.title("About port-utils")
            window.resizable(False, False)

            frame_first = tk.Frame()
            label_first = tk.Label(master=frame_first, text=NAME_VERSION)
            label_first.pack()

            frame_second = tk.Frame()
            label_second = tk.Label(master=frame_second, text="Utilities for download, update ports and check his changelog")
            label_second.pack()

            frame_third = tk.Frame()
            label_third = tk.Label(master=frame_third, text="\n(C) 2021 Linuxoid85 <linuxoid85@gmail.com>")
            label_third.pack()

            frame_first.pack()
            frame_second.pack()
            frame_third.pack()

            window.mainloop()

        elif mode == "cli":
            print("About port-utils\n\n", NAME_VERSION)
            print("\nUtilities for download, update ports and check his changelog")
            print("\n(C) 2021 Linuxoid85 <linuxoid85@gmail.com>")

        else:
            print(_("Error: unknown operating mode "), mode)
            exit(1)


# Other functions
class Other(object):
    # Getting the current date and time
    def getDate():
        return datetime.fromtimestamp(1576280665)

    # Logging
    def log_msg(message, status):
        f = open(LOGFILE, "a")
        for index in message:
            f.write(index)

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
            Other.log_msg("system data : OK", "OK")
        else:
            Other.log_msg("system data : FAIL", "EMERG")
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

# Updating and installing the port
class Update(object):
    # Checking for the existence of installed ports
    def checkInstalledPorts():
        if os.path.isdir(PORTDIR):
            print(_("The previous version of ports is installed. Removed..."))
            shutil.rmtree(PORTDIR)
        else:
            print(_("No previous ports were found."))

    # Checking for the existence of a port with an archive
    def checkArchiveCache():
        if os.path.isfile(CACHE_FILE):
            print(_("The previous version of the archive with ports was found in the cache. Removed ..."))
            os.remove(CACHE_FILE)
        else:
            print(_("No previous version of the ports system was found."))


    # Downloading the port from repositories
    def downloadPort(tree):
        f = open(r'/var/cache/ports/ports.txz',"wb")

        # Downloading
        # Currently the 'stable' and 'testing' branches are supported
        if tree == "stable":
            ufr = requests.get("https://raw.githubusercontent.com/CalmiraLinux/Ports/main/ports-lx4_1.1.txz")
        elif tree == "testing":
            ufr = requests.get("https://raw.githubusercontent.com/CalmiraLinux/Ports/testing/ports-lx4_1.1.txz")
        elif tree == "list":
            fp = open("/usr/share/update-ports/branches", "r")
            print(*fp)
            fp.close()

            exit(0)

        else:
            print(_("Error! Branch {0} does not exist!"), tree)
            exit(1)

        f.write(ufr.content) # Downloading

        f.close()

        if os.path.isfile(CACHE_FILE):
            print(_("Downloaded successfully!"))
        else:
            print(_("The file has not been downloaded! Check internet access."))
            exit(1)


    # Unpacking the port
    def unpackPort():
        if os.path.isfile(CACHE_FILE):
            try:
                t = tarfile.open(CACHE_FILE, 'r')

                t.extractall(path=CACHE_PORT_DIR)

                # Checking for an unpacked directory
                if os.path.isdir(CACHE_PORT_DIR):
                    print(_("Package unpacked successfully."))
                else:
                    print(_("Unknown error, crash."))
                    exit(1)

            except ReadError:
                print(_("Package read error. Perhaps he is broken."))
                exit(1)

            except CompressionError:
                print(_("Package unpacking error. The format is not supported."))
                exit(1)
        else:
            print(_("Package unpacking error. Package not found. It may not have been downloaded, or a third-party program changed it's name during unpacking."))
            exit(1)

    # Installing the port
    def installPort():
        # Checking just in case
        if os.path.isdir(CACHE_PORT_DIR):
            print(_("Directory with unpacked ports found, installing..."))
        else:
            print(_("Package unpacking error: directory not found."))
            exit(1)

        # Checking for a previous version of ports
        if os.path.isdir(PORTDIR):
            print(_("Found directory with previous ports version. Removed..."))
            shutil.rmtree(PORTDIR)
        else:
            print(_("No previous ports were found."))

        # Copying
        shutil.copytree(PORT, '/usr/ports')

# Other functions for ports
# FIXME - updating translation into other languages
class PortFunctions(object):
    # Checking for the existence of the required file (for cleanSys)
    # file - file;
    # mode - work mode:
    #   exists     - checking for file existence
    #   non_exists - check for missing file
    # FIXME - adding a check for file existence
    def checkDir(file, mode):
        if mode == "exists":
            if os.path.isdir(file):
                print(_("Directory {0} is exist"), file)
                return(0)
            else:
                print(_("Error: the required directory {0} does not exist!"), file)
                return(1)

        elif mode == "non_exists":
            if os.path.isdir(file):
                print(_("Directory: file {0} is exist!"), file)
                return(1)
            else:
                print(_("Directory {0} does not exist"), file)
                return(0)

        else:
            print(_("Error using checkFile: argument {0} for 'mode' does not exist!"), mode)
            exit(1)

    # Cleaning the system from unnecessary files
    def cleanSys(mode):
        if mode == "cache":
            # Очистка кеша
            print(_("Checking for cache existence..."), end = " ")
            if os.path.isdir(CACHE):
                print(_("OK"))

                shutil.rmtree(CACHE)
                os.makedirs(CACHE)
            else:
                print(_("FAIL: Cache directory not found"))
                exit(1)

        elif mode == "log":
            # Очистка логов
            print(_("Checking for the existence of log files..."), end = " ")
            for FILE in LOGFILE, '/var/log/update-ports-dbg.log':
                if os.path.isfile(FILE):
                    print(_("File {0}: OK"))
                    os.remove(FILE)
                else:
                    print(_("Error: the required file {0} does not exist!"), FILE)
                    exit(1)

                # Проверка на корректное удаление
                if os.path.isfile(FILE):
                    print(_("Error: the required file {0} has not been deleted!"))
                    exit(1)
                else:
                    print(_("File {0} has deleted succesfully!"))
                    exit(0)

        elif mode == "src":
            # Очистка дерева исходных кодов
            print(_("Checking for the existence of a source tree..."), end = " ")
            if PortFunctions.checkDir("/usr/src", "exists"):
                pass
            else:
                exit(1)

            shutil.rmtree("/usr/src")

            # Проверка на корректное удаление
            if PortFunctions.checkDir("/usr/src", "non_exists"):
                pass
            else:
                print(_("Error: the required /usr/src has not been deleted!"))
                exit(1)

            os.mkdirs("/usr/src")

            exit(0)

    # News reader
    def checkNews(tree):
        f = open(r'/var/cache/ports/news.txt', "wb")

        # Downloading
        if tree == "stable":
            ufr = requests.get("https://raw.githubusercontent.com/CalmiraLinux/Ports/main/CHANGELOG.md")
        elif tree == "testing":
            ufr = requests.get("https://raw.githubusercontent.com/CalmiraLinux/Ports/testing/CHANGELOG.md")
        else:
            print(_("Error! Branch {0} does not exist!"), tree)
            exit(1)

        f.write(ufr.content) # Downloading

        try:
            f = open("/var/cache/ports/news.txt", "r")

        except FileNotFoundError:
            print(_("No such file /var/cache/ports/news.txt"))
            exit(1)

        print(*f)



#################
##             ##
## Script body ##
##             ##
#################


# Initial checks

Other.printDbg("checkArchiveCache\n")
Update.checkArchiveCache()

##

#if args.clean == "cache" or args.clean == "log" or args.clean == "src" or args.clean == "all":
#    PortFunctions.cleanSys(args.clean)
#    exit(0)

# Check for compatibility with Calmira
if Other.getSystem() != "1.1":
    print(_("Error: the update-ports version is not compatible with the current Calmira version!"))
    exit(1)

# Command line parsing (2)
if (args.news):
    Other.checkDirs("news")
    PortFunctions.checkNews(args.news)

elif (args.tree):
    Other.printDbg("checkDirs\n")
    Other.checkDirs('tree')

    Other.printDbg("checkInstalledPorts\n")
    Update.checkInstalledPorts()

    # Download and install

    Other.printDbg("downloadPort\n")
    Update.downloadPort(args.tree)

    Other.printDbg("unpackPort\n")
    Update.unpackPort()

    Other.printDbg("installPort\n")
    Update.installPort()

    # Final checks

    print(_("Checking for correct update..."), end = ' ')
    if os.path.isdir(PORTDIR):
        print("ОК")
        exit(0)
    else:
        print(_("NOT FOUND! It is possible that something went wrong during the update."))
        exit(1)

elif (args.clear):
    PortFunctions.cleanSys(args.clear)
    exit(0)

elif (args.about):
    Window.about(args.about)
    exit(0)
