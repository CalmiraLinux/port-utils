#!/bin/python
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
import shutil
import tarfile
import requests

## Base Variables
PORTDIR = "/usr/ports" # Директория с портами
CACHE = "/var/cache/ports" # Директория с кешем
CACHE_FILE = CACHE + "/ports.txz" # Скачанный пакет с портами

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
        for DIR in '/var/cache/ports' '/usr/ports':
            if os.path.isdir(DIR):
                print("Директория {DIR} существует.", DIR)
            else:
                print("Директории {DIR} не существует, создаю новую.", DIR)
                os.makedirs(DIR)

    # Получение данных системы
    def getSystem():
        sysData = "/etc/calm-release"

        if os.path.isfile(sysData):
            log_msg("system data : OK", "OK")
        else:
            log_msg("system data : FAIL", "EMERG")
            print("Ошибка: файла с данными дистрибутива не существует, либо нет доступа на его чтение. Выход.")
            exit(1)

        with open(sysData, 'r') as f:
            systemData = json.loads(f.read())

        return systemData["distroVersion"]



# Обновление и установка портов
class Update(object):
    # Проверка на существование установленных портов
    def checkInstalledPorts():
        if os.path.isdir(PORTDIR):
            print("Предыдущая версия портов установлена. Удаляю...")
            shutil.rmtree(PORTDIR)
        else:
            print("Предыдущей версии портов не найдено.")

    # Проверка на существование архива с портами
    def checkArchiveCache():
        if os.path.isfile(CACHE_FILE):
            print("Предыдущая версия архива с портами найдена в кеше. Удаляю...")
            os.remove(CACHE_FILE)
        else:
            print("Предыдущей версии системы портов не найдено.")


    # Скачивание файла из репозиториев
    def downloadPort(self, tree):
        f = open(r'/var/cache/ports/ports.txz',"wb")

        # Скачивание порта
        # На данный момент поддерживаются ветки 'stable' и 'testing'
        if tree == "stable":
            ufr = requests.get("https://raw.githubusercontent.com/CalmiraLinux/Ports/main/ports-lx4_1.1.txz")
        elif tree == "testing":
            ufr = requests.get("https://raw.githubusercontent.com/CalmiraLinux/Ports/main/ports-lx4_1.1.txz")
        else:
            print("Ошибка! Ветки {tree} не существует!", tree)
            exit(1)

        f.write(ufr.content) # Downloading

        f.close()

    # Установка порта
    def installPort():
        
