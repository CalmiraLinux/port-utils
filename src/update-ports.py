#!/usr/bin/python3
#
# update-ports - Port system update program
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
# Project Page: http://github.com/CalmiraLinux/update-ports
# Michail Krasnov <linuxoid85@gmail.com>
#

import os
import argparse
import shutil
import tarfile
import requests
from datetime import datetime
import gettext

## Base Variables
PORTDIR = "/usr/ports" # Директория с портами
CACHE = "/var/cache/ports" # Директория с кешем
CACHE_FILE = CACHE + "/ports.txz" # Скачанный пакет с портами
CACHE_PORT_DIR = CACHE + "/ports" # Распакованные в кеш порты
PORT = CACHE_PORT_DIR + "/ports"  # Порты, которые установятся в /usr/ports

## getext
gettext.bindtextdomain('update-ports', '/usr/share/locale')
gettext.textdomain('update-ports')
_ = gettext.gettext

# Проверка на запуск от root
GID = os.getgid()

if GID != 0:
    print(_("Error: you must run this script as root!"))
    exit(1)

# Command line parsing

parser = argparse.ArgumentParser(description='update-ports - port system update program')
parser.add_argument("--tree", "-t",
                    choices=["stable", "testing"],
                    required=True, type=str, help="Net branch from which ports are update")
parser.add_argument("--debug", "-d",
                    choices=["yes", "no"],
                    type=str, help="Displaying debug messages")

args = parser.parse_args()

####################
##                ##
## Main functions ##
##                ##
####################

# Другие функции, не относящиеся к обновлению
class Other(object):
    # Получение текущих даты и времени
    def getDate():
        return datetime.fromtimestamp(1576280665)

    # Логирование
    def log_msg(message, status):
        f = open(LOGFILE, "a")
        for index in message:
            f.write(index + '\n')

    # Проверка на существование необходимых директорий
    def checkDirs():
        for DIR in "/var/cache/ports", "/usr/ports":
            if os.path.isdir(DIR):
                print(_("Directory {0} exists.", DIR))
            else:
                print(_("Directory {} does not exist, creating a new one.", DIR))
                os.makedirs(DIR)

    # Получение данных системы
    # TODO - использовать для скачивания портов для конкретной версии дистрибутива
    # NOTE - сейчас не используется, так как должен вызываться после выхода
    # Calmira LX4 1.2
    def getSystem():
        sysData = "/etc/calm-release"

        if os.path.isfile(sysData):
            log_msg("system data : OK", "OK")
        else:
            log_msg("system data : FAIL", "EMERG")
            print(_("Error: the file with distribution data does not exist, or there is no access to read it. Exit."))
            exit(1)

        with open(sysData, 'r') as f:
            systemData = json.loads(f.read())

        return systemData["distroVersion"]

    # Вывод debug-сообщений на экран
    def printDbg(message):
        if args.debug == "yes":
            # Выводить на экран сообщения
            print(message)
        elif args.debug == "no":
            # Выводить сообщения в лог
            f = open("/var/log/update-ports-dbg.log", "a")

            for index in message:
                f.write(index)

            f.close()
        else:
            pass

# Обновление и установка портов
class Update(object):
    # Проверка на существование установленных портов
    def checkInstalledPorts():
        if os.path.isdir(PORTDIR):
            print(_("The previous version of ports is installed. Removed..."))
            shutil.rmtree(PORTDIR)
        else:
            print(_("No previous ports were found."))

    # Проверка на существование архива с портами
    def checkArchiveCache():
        if os.path.isfile(CACHE_FILE):
            print(_("The previous version of the archive with ports was found in the cache. Removed ..."))
            os.remove(CACHE_FILE)
        else:
            print(_("No previous version of the ports system was found."))


    # Скачивание файла из репозиториев
    def downloadPort(tree):
        f = open(r'/var/cache/ports/ports.txz',"wb")

        # Скачивание порта
        # На данный момент поддерживаются ветки 'stable' и 'testing'
        if tree == "stable":
            ufr = requests.get("https://raw.githubusercontent.com/CalmiraLinux/Ports/main/ports-lx4_1.1.txz")
        elif tree == "testing":
            ufr = requests.get("https://raw.githubusercontent.com/CalmiraLinux/Ports/main/ports-lx4_1.1.txz")
        else:
            print(_("Error! Branch {0} does not exist!", tree))
            exit(1)

        f.write(ufr.content) # Downloading

        f.close()
        
        if os.path.isfile(CACHE_FILE):
            print("Downloaded successfully!")
        else:
            print("The file has not been downloaded! Check internet access.")
            exit(1)


    # Распаковка порта
    def unpackPort():
        if os.path.isfile(CACHE_FILE):
            try:
                t = tarfile.open(CACHE_FILE, 'r')

                t.extractall(path=CACHE_PORT_DIR)

                # Проверка на наличие распакованной директории
                if os.path.isdir(CACHE_PORT_DIR):
                    print("Package unpacked successfully.")
                else:
                    print("Unknown error, crash.")
                    exit(1)

            except ReadError:
                print("Package read error. Perhaps he is broken.")
                exit(1)

            except CompressionError:
                print(_("Package unpacking error. The format is not supported."))
                exit(1)
        else:
            print(_("Package unpacking error. Package not found. It may not have been downloaded, or a third-party program changed it's name during unpacking."))
            exit(1)
    
    # Установка порта
    def installPort():
        # Проверка на всякий случай
        if os.path.isdir(CACHE_PORT_DIR):
            print(_("Directory with unpacked ports found, installing..."))
        else:
            print(_("Package unpacking error: directory not found."))
            exit(1)
        
        # Проверка на наличие предыдуще
        if os.path.isdir(PORTDIR):
            print(_("Found directory with previous ports version. Removed..."))
            shutil.rmtree(PORTDIR)
        else:
            print(_("No previous ports were found.")))

        # Копирование
        #shutil.copytree(CACHE_PORT_DIR, '/usr/ports')
        shutil.copytree(PORT, '/usr/ports')

#################
##             ##
## Script body ##
##             ##
#################


# Начальные проверки

Other.printDbg("checkDirs\n")
Other.checkDirs()

Other.printDbg("checkInstalledPorts\n")
Update.checkInstalledPorts()

Other.printDbg("checkArchiveCache\n")
Update.checkArchiveCache()

# Скачивание и установка

Other.printDbg("downloadPort\n")
Update.downloadPort(args.tree)

Other.printDbg("unpackPort\n")
Update.unpackPort()

Other.printDbg("installPort\n")
Update.installPort()

# Конечные проверки

print(_("Checking for correct update...", end = ' '))
if os.path.isdir(PORTDIR):
    print("ОК")
    exit(0)
else:
    print(_("NOT FOUND! It is possible that something went wrong during the update."))
    exit(1)
