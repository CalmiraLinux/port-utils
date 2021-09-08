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

## Base Constants
NAME_VERSION="port-utils v0.2 DEV"
LOGFILE = "/var/log/port-utils.log"
PORTDIR = "/usr/ports"               # Ports directory
FILES_DIR = "/usr/share/ports"       # Files directory
MODULES_DIR = FILES_DIR + "/modules" # Modules directory
DOCDIR = "/usr/share/doc/Calmira"    # Documents dir
CACHE = "/var/cache/ports"           # Cache directory
CACHE_FILE = CACHE + "/ports.txz"    # Downloaded package with ports
CACHE_DOC_FILE = CACHE + "/docs.txz" # Downloaded package with documentation
CACHE_PORT_DIR = CACHE + "/ports"    # Ports unpacked to cache
CACHE_DOC_DIR = CACHE + "/docs"      # Documentation unpacked to cache
PORT = CACHE_PORT_DIR + "/ports"     # Ports to install in /usr/ports
DOC = CACHE_DOC_DIR + "/docs"

sys.path.append(MODULES_DIR)
#import core-functions

# TODO - закончить функцию для скачивания файла downloadPkg - добавить
# скачивание документации

# FIXME - getext
gettext.bindtextdomain('port-utils', '/usr/share/locale')
gettext.textdomain('port-utils')
_ = gettext.gettext

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

# Read news
parser.add_argument("--news",
                    choices=["stable", "testing"], help="Read news of ports")

# Install documentation
parser.add_argument("--doc",
                    choices=["stable", "testing"], help="Download Calmira and Ports System documentation")

# Debug mode
parser.add_argument("--debug", "-d",
                    choices=["yes", "no"],
                    type=str, help="Displaying debug messages")

# Clean
parser.add_argument("--clear",
                    choices=["cache", "log", "src", "all"],
                    type=str, help="Cleaning the system from old ports files")

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
        about_text = "Utilities for download, update ports and check his changelog"

        if mode == "gui":
            window = tk.Tk()

            window.title("About port-utils")
            window.resizable(False, False)

            frame_first = tk.Frame()
            label_first = tk.Label(master=frame_first, text=NAME_VERSION)
            label_first.pack()

            frame_second = tk.Frame()
            label_second = tk.Label(master=frame_second, text=about_text)
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
            print("\n", about_text)
            print("\n(C) 2021 Linuxoid85 <linuxoid85@gmail.com>")

        else:
            print(_("Error: unknown operating mode "), mode)
            exit(1)


# Other functions
class Other(object):
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
    def downloadPkg(tree, mode):
        print(_("Job selection..."), end = " ")

        if mode == "port":
            print(_("Port download..."), end = " ")

            f = open(r'/var/cache/ports/ports.txz',"wb")
            # Ссылка для скачивания стабильной версии портов
            stable_link = "https://raw.githubusercontent.com/CalmiraLinux/Ports/main/ports-lx4_1.1.txz"
            # Ссылка для скачивания портов из тестингов
            unstable_link = "https://raw.githubusercontent.com/CalmiraLinux/Ports/testing/ports-lx4_1.1.txz"

        elif mode == "doc":
            print(_("Documentation download..."), end = " ")

            f = open(r'/var/cache/ports/docs.txz', "wb")
            # Ссылка для скачивания стабильной версии документации
            stable_link = "https://raw.githubusercontent.com/CalmiraLinux/CalmiraLinux/lx4/v1.1/docs/archives/docs.txz"
            # Ссылка для скачивания нестабильной версии документации
            # NOTE - на данный момент поддерживается только одна ветка.
            unstable_link = stable_link
            # Изменение значения переменной (для тестирования)
            CACHE_FILE = CACHE + "/docs.txz"


        # Downloading
        # Currently the 'stable' and 'testing' branches are supported
        if tree == "stable":
            ufr = requests.get(stable_link)
        elif tree == "testing":
            ufr = requests.get(unstable_link)
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
    def unpackPkg(mode):
        if mode == "port":
            cache_file = CACHE_FILE
            cache_dir = CACHE_PORT_DIR
        elif mode == "doc":
            cache_file = CACHE_DOC_FILE
            cache_dir = CACHE_DOC_DIR
        else:
            print(_("Error: uknown option for 'unpackPkg'!"))
            exit(1)


        if os.path.isfile(cache_file):
            try:
                t = tarfile.open(cache_file, 'r')

                t.extractall(path=cache_dir)

                # Checking for an unpacked directory
                if os.path.isdir(cache_dir):
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
    def installPkg(mode):
        # Выбор нужных файлов
        if mode == "port":
            cache_dir = CACHE_PORT_DIR # Unpacked dir
            prefix_dir = PORTDIR # Куда распаковать
            target_file = PORT # Что распаковать
            target_dir = '/usr/ports' # Куда скопировать
        elif mode == "doc":
            cache_dir = CACHE_DOC_DIR # Unpacked dir
            prefix_dir = DOCDIR # Куда распаковать
            target_file = DOC # Что распаковать
            target_dir = DOCDIR # Куда скопировать
        else:
            print(_("Error: uknown option for 'installPkg'!"))
            exit(1)

        # Checking just in case
        if os.path.isdir(cache_dir):
            print(_("Directory with unpacked ports/documentation found, installing..."))
        else:
            print(_("Package unpacking error: directory not found."))
            exit(1)

        # Checking for a previous version of ports
        if os.path.isdir(prefix_dir):
            print(_("Found directory with previous ports/documentation version. Removed..."))
            shutil.rmtree(prefix_dir)
        else:
            print(_("No previous ports/documentation were found."))

        # Copying
        shutil.copytree(target_file, target_dir)

# Other functions for ports
class PortFunctions(object):
    # Checking for the existence of the required file (for cleanSys)
    # file - check file;
    # mode - work mode:
    #   exists     - checking for file existence
    #   non_exists - check for missing file
    # TODO - adding a check for file existence
    def checkDir(file, mode):
        # Выбор режима работы
        if mode == "exists":
            returnVar = 0   # В случае наличия
            returnUnVar = 1 # В случае отсутствия
        elif mode == "non_exists":
            returnVar = 1   # В случае наличия
            returnUnVar = 0 # В случае отсутствия
        else:
            print(_("Error using checkFile: argument {0} for 'mode' does not exist!"), mode)
            exit(1)

        # Проверка
        if os.path.isdir(file):
            print(_("Directory {0} is exist"), file)
            return(returnVar)
        else:
            print(_("Directory {0} does not exist"), file)
            return(returnUnVar)

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

        # Выбор режима работы
        if tree == "stable":
            file_branch = "main"

        elif tree == "testing":
            file_branch = tree

        else:
            print(_("Error! Branch {} does not exist!").format(tree))
            exit(1)
        
        # Downloading
        branch = "https://raw.githubusercontent.com/CalmiraLinux/Ports/" + file_branch + "/CHANGELOG.md" # Что скачивать
        
        ufr = requests.get(branch)
        f.write(ufr.content)

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

# Check for compatibility with Calmira
if Other.getSystem() != "1.1":
    print(_("\033[31mError: the update-ports version is not compatible with the current Calmira version!\033[0m"))
    exit(1)

Other.getRoot("check")

# Command line parsing (2)
if (args.news):
    # Initial checks
    Other.printDbg("checkArchiveCache\n")
    Update.checkArchiveCache()

    # Get change logs
    Other.checkDirs("news")
    PortFunctions.checkNews(args.news)

elif (args.tree):
    # Initial checks
    Other.printDbg("checkDirs\n")
    Other.checkDirs('tree')

    Other.printDbg("checkArchiveCache\n")
    Update.checkArchiveCache()

    Other.printDbg("checkInstalledPorts\n")
    Update.checkInstalledPorts()

    # Download and install
    Other.printDbg("downloadPort\n")
    Update.downloadPkg(args.tree, "port")

    Other.printDbg("unpackPort\n")
    Update.unpackPkg("port")

    Other.printDbg("installPort\n")
    Update.installPkg("port")

    # Final checks
    print(_("Checking for correct update..."), end = ' ')
    if os.path.isdir(PORTDIR):
        print("ОК")
        exit(0)
    else:
        print(_("NOT FOUND! It is possible that something went wrong during the update."))
        exit(1)

elif (args.doc):
    Other.checkDirs("tree")

    Update.checkArchiveCache()

    Update.downloadPkg(args.doc, "doc")
    Update.unpackPkg("doc")
    Update.installPkg("doc")

elif (args.clear):
    Other.printDbg("checkArchiveCache\n")

    Update.checkArchiveCache()

    # Clean the system
    PortFunctions.cleanSys(args.clear)
    exit(0)

elif (args.about):
    Window.about(args.about)
    exit(0)
