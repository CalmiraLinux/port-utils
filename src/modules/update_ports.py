#!/usr/bin/python3
# Модуль с функциями, предназначенными для обновления
# системы портов до актуальной версии
# (C) 2021 Михаил Краснов <linuxoid85@gmail.com>

import os
import sys
import shutil
import tarfile
import wget
import json
import gettext
import ports_default # Стандартные функции и переменные Ports API
import ports_manage  # Управление системой портов

gettext.bindtextdomain('port-utils', '/usr/share/locale')
gettext.textdomain('port-utils')
_ = gettext.gettext

class settings():
    
    params = [
        "branch",
        "ports_repo",
        "debug",
        "pager",
        "downgrade_with_fetch"
    ]

    def check_file(self) -> bool:
        if not os.path.isfile(SETTINGS):
            print(_("File {} not found!").format(SETTINGS))
            return False

        f = open(SETTINGS)
        data = json.load(f)
        check_error = False

        for param in settings.params:
            try:
                print(_("Param [{data[param]}]: ok"))
            except KeyError:
                print(_("Param [{}]: not found").format(param))
                check_error = True
        
        if check_error:
            return False
        
    def get(self, param):
        """Get param"""

        self.param = param

        if settings.check_file():
            f = open(SETTINGS, 'r')
        else:
            exit(1)

        data = json.load(f)
        try:
            parameter = data[param]
        except KeyError:
            print(_(f"Param {param} doesn't found!"))
            return None

        f.close()

        return parameter

class fetch_metadata():
    """
    Class for update Port system metadata

    Usage:
    `fetch_metadata()`
    """

    ports_archive_file = CACHE + "/ports.txz" # Куда скачивать
    ports_unpack = CACHE "/ports" # Куда распаковывать
    ports_unpack_file = ports_unpack + "/ports" # Директория с портами

    def parse(self, file):
        """
        Returns the contents of the metadata file in the Python object format

        `parse(file)`
        """

        self.file = file

        if not os.path.isfile(file):
            print(_("File {} not found").format(file))
            exit(1)
        
        f = open(file, 'r')
        data = json.load(data)
        f.close()

        return data

    def get_metadata(self, branch):
        """
        Download metadata.

        `get_metadata(branch)`
        """

        self.branch = branch

        metadata = settings.get("repo") + settings.get("branch") + "/metadata.json" # File

        if os.path.isfile(METADATA_TMP):
            os.remove(METADATA_TMP)
        
        wget.download(metadata, METADATA_TMP)

    def get_updt_num(self, file) -> int:
        """
        Returns the 'update_number' from metadata
        """

        self.file = file

        if not os.path.isfile(file):
            print(_("File {} not found").format(file))
            exit(1)
        
        f = open(file, "r")
        data = json.load(f)
        
        num = data["update_number"]
        f.close()

        return num
    
    def get_difference(self) -> str:
        """
        Getting differences in the port system
        """

        md_i = fetch_metadata.get_updt_num(METADATA) # Installed metadata
        md_tmp = fetch_metadata.get_updt_num(METADATA_TMP) # Downloaded metadata

        difference = md_tmp - md_i # Полученное значение, с которым будем работать

        if difference < 0:
            # Даунгрейдим до более старой ветки/какие-то проблемы
            if settings.get("downgrade_with_fetch") == True:
                print(_("Downgrading the port system is a bad idea."))
                status = "downgrade"

            else:
                print(_("Downgrading the port system is a bad idea."))
                exit(1)

        elif difference > 0:
            # Есть обновления
            print(_("There are updates to the port system"))
            status = "update"

        else:
            # Обновлений нет
            print(_("There are no changes in the port system."))
            status = "no_updates"
        
        return status

    def install_metadata() -> bool:
        """
        Installing metadata file
        """

        for file in METADATA METADATA_TMP:
            if not os.path.isfile(file):
                print(_("File {} not found").format(file))
                exit(1)
        
        """
        Вычисление 'update_number' из двух
        файлов метаданных: METADATA и METADATA_TMP
        """

        if fetch_metadata.get_difference() == "no_updates":
            exit(0)
        
        """
        Установка новой версии файла метаданных
        """

        os.remove(METADATA)
        shutil.copyfile(METADATA_TMP, METADATA)

        return os.path.isfile(METADATA)

class fetch_ports():
    """
    Updating the port system
    """

    archive_file = CACHE + "/ports.txz" # Куда скачивать
    unpack = CACHE "/ports" # Куда распаковывать
    unpack_file = ports_unpack + "/ports" # Директория с портами

    def clean_files(self):
        """
        Checking for the presence of a previous version of the
        ports system in the cache
        """

        for file in fetch_ports.unpack, fetch_ports.unpack_file:
            shutil.rmtree(file)
        
        if os.path.isfile(fetch_ports.archive_file):
            os.remove(fetch_ports.archive_file)
        
    def get_ports(self):
        """
        Getting an archive with a port system from CalmiraLinux repositories
        """

        fetch_ports.clean_files()

        file = settings.get("repo") + settings.get("branch") + "/ports.txz"

        wget.download(file, fetch_ports.archive_file) # Downloading
    
    def install_ports(self):
        """
        Unpacking port system archive and install files from this
        """

        archive = fetch_ports.archive_file # Архив для распаковки
        file    = fetch_ports.unpack_file  # Что копировать

        """
        Распаковка архива
        """

        if not os.path.isfile(archive):
            print(_("File {} not found").format(archive))
            exit(1)
        
        try:
            t = tarfile.open(archive)
            t.extractall(path=fetch_ports.unpack)
        except tarfile.ReadError:
            print(_("Package read error. Perhaps he is broken"))
            sys.exit(1)

        except tarfile.CompressionError:
            print(_("Package unpacking error. The format is not supported"))
            sys.exit(1)
            
        except:
            print(_("Uknown error"))
            sys.exit(1)
        

        """
        Копирование файлов
        """
        if os.path.isdir(file):
            if os.path.isdir(PORTDIR):
                shutil.rmtree(PORTDIR)
            
            try:
                shutil.copytree(file, PORTDIR)
            except:
                print(_("Uknown error"))
                exit(1)
        
        else:
            print(_("File {} not found").format(file))
            exit(1)
