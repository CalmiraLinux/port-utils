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
import shutil
import tarfile
import wget
import json
import subprocess
import sqlite3
import gettext
from datetime import datetime

gettext.bindtextdomain('port-utils', '/usr/share/locale')
gettext.textdomain('port-utils')
_ = gettext.gettext

## ABOUT PROGRAM ##
PROGRAM_RELEASE = "beta build 1"
NAME_VERSION = "port-utils v1.0b1 DEV " + PROGRAM_RELEASE # Name + version

## BASE CONSTANTS ##
LOGDIR         = "/var/log"                   # Log directory
LOGFILE        = LOGDIR + "port-utils.log"    # Log file
PORTDIR        = "/usr/ports"                 # Port system directory
FILES_DIR      = "/usr/share/ports"           # Files directory
DOCDIR         = "/usr/share/doc/Calmira"     # Documentation dorectory
CACHE          = "/var/cache/ports"           # Cache directory
PORT_CACHE     = CACHE + "/ports.txz"         # Downloaded ports package
DOC_CACHE      = CACHE + "/docs.txz"          # Downloaded documentation package
PORT_CACHE_DIR = CACHE + "/ports"             # Unpacked ports directory
DOC_CACHE_DIR  = CACHE + "/docs"              # Unpacked documentation directory
PORT           = PORT_CACHE_DIR + "/ports"    # Files to install in /usr/ports
DOC            = DOC_CACHE_DIR  + "/docs"     # Files to install in /usr/share/doc/Calmira
METADATA       = FILES_DIR + "/metadata.json" # Links to Port system and CalmiraLinux documentation packages
SETTINGS       = "/etc/port-utils.json"       # Program settings
INITIAL_CONF   = FILES_DIR + "/initial-conf.json"
CALM_RELEASE   = "/etc/calm-release"          # Calmira release info
DATABASE       = "/var/db/ports/ports.db"     # Port system database

## BASE MESSAGES ##
OK_MSG   = _("[   ok   ]")
FAIL_MSG = _("[  FAIL  ]")
WARN_WSG = _("[  WARN  ]")
DIALOG_MESSAGE       = _("Continue? (y/n) ")
CONNECTION_ERROR_MSG = _("Connection error. Check you internet access.")
CONNECTION_ABORT_MSG = _("The connection was aborted. Check you internet access.")
UPDATE_MSG    = _("Updates:")
ADDITIONS_MSG = _("\nAdditions:")
DELETIONS_MSG = _("\nDeletions:")

## Base variables ##
database_lock_file = "/var/lock/port-utils.lock"
user_var_dir       = "~/.local/var"
user_log_dir       = user_var_dir + "/log"
user_cache_dir     = user_var_dir + "/cache/ports"

# Checking in import
if __name__ != "__main__":
    print(_("The executable Port program must not be imported!"))
    sys.exit(1)

## COMMAND LINE PARSING ##
if sys.argv[1] == "-h" and sys.argv[2] == "usage":
    import random
    message_list = ["Windows - must die, GNU/Linux - forever!", "CalmiraLinux LX4 will be released 11/15/2021",
    "Чтобы россияне могли как следует подготовиться к выборам 2018 года, в магазинах теперь будет продаваться только одна марка водки, а в аптеках - только один вид презервативов.",
    "Девушкам на заметку: Если вы зимой опаздываете на свидание, то вас может ожидать холодный конец!"]
    print(random.choice(message_list))
    exit(255)

parser = argparse.ArgumentParser(description=_("port-utils - Port system software"),
                                 epilog=_("Good luck ;)"))

# Install or update Port system
parser.add_argument("--update", "-u",
                    choices=["stable", "testing"],
                    type=str, help=_("Install or update Port system"))

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

# Clean the CalmiraLinux
parser.add_argument("--clean", "-c", type=str,
                    choices=["cache", "log", "src", "all"],
                    help=_("Cleaning the CalmiraLinux system from old ports (and other) files"))

# About port-utils
parser.add_argument("--about", "-a", help=_("About program"), action="store_true")

args = parser.parse_args()

####################
##                ##
## MAIN FUNCTIONS ##
##                ##
####################

# About message (for args.about)
def about_msg():
    about_title = _("About port-utils")
    about_text = _("Utilities for download, install, update, remove ports and check his changelog")

    print("{0}\n\n {1}".format(about_title, NAME_VERSION))
    print("\n", about_text)
    print(_("\n(C) Michail Krasnov <linuxoid85@gmail.com>"))

# Logging
def log_msg(message, status):
    """
    Function for write messages in log file

    Usage:
    `log_msg(message, status)`

    Statuses:
    - 'ok',
    - 'notice',
    - 'error',
    - 'fail',
    - 'emerge'
    """
    log_message = message + " [ " + status + " ]\n" # Формирование сообщения, которое отправится в лог
    gid = os.getgid()

    if gid == 0:
        f = open(LOGFILE, "a")
        for index in log_message:
            f.write(index)
    else:
        if os.path.isdir(user_log_dir):
            pass
        else:
            os.makedirs(user_log_dir)
        
        log_msg_user = user_log_dir + "/port-utils.log"
        f = open(log_msg_user, "a")
        
        for index in log_message:
            f.write(index)

# Print debug messages
def print_dbg(message):
    gid = os.getgid()
    f = open(SETTINGS, 'r')
    settings_data = json.load(f)

    if settings_data["debug"] == "True":
        print(message)
    else:
        message = message + "\n"
        if gid == 0:
            file = open("/var/log/port-utils-dbg.log", "a")
        else:
            if os.path.isdir(user_log_dir):
                pass
            else:
                os.makedirs(user_log_dir)
            
            dbg_msg_file = user_log_dir + "/port-utils-dbg.log"
            file = open(dbg_msg_file, "a")

        for index in message:
            file.write(index)
        
        file.close()
    
    f.close()

# Dialog message
def dialog_msg(message=DIALOG_MESSAGE, return_code=0):
    """
    Function for print dialog message.

    Usage:
    `dialog_msg(message=`"message"`, return_code=`"return code (0, 1, 255, etc.)"`)`
    
    'message' - str type;
    'return code' - ONLY int type.
    """
    
    run = input(message)
    if run == "y" or run == "Y":
        pass
    else:
        sys.exit(return_code)

# Checking to run a function as root
def check_root(v_exit=True):
    """
    Function for checking to run a program as root
    
    Usage:
    `check_root(v_exit=False)`
    """
    
    message = _("Error: you must run this script as root!")
    gid = os.getgid()
    if gid != 0:
        if v_exit:
            print("\033[31m{}\033[0m".format(message))
            sys.exit(1)
        else:
            return 1

def check_ports(mode):
    """
    Function for check port files

    Usage:
        * check_ports(mode)

    Work modes:
        * 'installed_ports' - check the /usr/ports (default) directory;
        * 'ports_cache'     - check the downloaded Port system package;
    """
    if mode == "installed_ports":
        if os.path.isdir(PORTDIR):
            log_msg("Removing Port system ('check_ports()')", "notice")
            print(_("The previous version of the Port system is installed. Removed..."), end = " ")
            try:
                shutil.rmtree(PORTDIR)
                log_msg("Removing OK", "ok")
                print(OK_MSG)
            except:
                log_msg("Removing fail", "FAIL")
                print(_("Removing error!"))
                return 1
        else:
            print(_("No previous Port system version were found"))
            return 1

    elif mode == "ports_cache":
        if os.path.isfile(PORT_CACHE):
            print(_("The previous version of the package with Port system was found in the cache. Removed..."))
            try:
                os.remove(PORT_CACHE)
            except:
                print(_("Removing error!"))
                return 1
        else:
            print(_("No previous version of the packages with Port system was found"))
            return 1

##################
##              ##
## MAIN CLASSES ##
##              ##
##################
class update_ports(object):
    """
    Class for update Port system and CalmiraLinux documentation

    Usage:
    
    `ports(mode, branch)`

    - 'mode' - work mode:
      - 'port' - download port package.
    - 'branch' - download branch:
      - 'stable',
      - 'testing'.
    """
    def __init__(branch):
        check_root() # Checking for run program as non-root user

        update_ports.update_meta(branch) # Update metadata
        if update_ports.check_meta():
            update_ports.get_file(branch)  # Download the required files
        else:
            print(_("The metadata does not match the CalmiraLinux release!")) # FIXME: translate
            dialog_msg(return_code=1)
        
        if os.path.isdir(PORT_CACHE_DIR):
            try:
                os.remove(PORT_CACHE_DIR)
                os.makedirs(PORT_CACHE_DIR)
            except:
                print(_("Uknown error"))
        
        update_ports.unpack_file(PORT_CACHE, PORT_CACHE_DIR)
        update_ports.install_file(PORT_CACHE_DIR, PORTDIR)
    
    def print_changes(self, change, message):
        """
        Function for printing information about changes to stdout.

        Usage:
        `update_ports.print_changes(change, message)`
        """
        
        self.change = change
        self.message = message

        try:
            for package in change:
                print("{0}: {1}".format(change, message))
        except:
            print(_("Uknown error"))

    def get_update_number(self, metadata):
        """
        Function for checking update_number

        Usage:
        `check_update_meta(metadata)`

        `metadata` - metadata file (e.g. /tmp/metadata.json)
        """

        self.metadata = metadata

        if os.path.isfile(metadata):
            f = open(metadata, "r")
        else:
            print(_("File {} not found").format(metadata))
            return 1
        
        meta_data = json.load(f)
        yield meta_data["update_number"]
        f.close()
    
    def update_meta(self, branch):
        """
        Function for update port-utils metadata

        Files:
        - `/usr/share/ports/metadata.json` - metadata file.

        Branches:
        - 'stable',
        - 'testing'.
        """

        self.branch = branch

        log_msg("Updating metadata", "notice")

        # Check branches
        if branch == "stable":
            content_md = "https://raw.githubusercontent.com/CalmiraLinux/Ports/main/metadata.json"
        elif branch == "testing":
            content_md = "https://raw.githubusercontent.com/CalmiraLinux/Ports/testing/metadata.json"
        else:
            print(_("Uknown branch {}").format(branch))
            sys.exit(1)
        
        METADATA_tmp = "/tmp/metadata_tmp.json"

        # Downloading metadata
        if os.path.isfile(METADATA_tmp):
            os.remove(METADATA_tmp)
        
        wget.download(content_md, METADATA_tmp)

        # Checking
        try:
            f_i = open(METADATA_tmp)
            metadata_file = json.load(f_i)
        except FileNotFoundError:
            print(_("File {} not found").format(METADATA_tmp))
            sys.exit(1)
        except:
            print(_("Uknown error"))
            sys.exit(1)

        metadata_install = update_ports.check_update_meta(METADATA)

        if metadata_file["update_number"] > metadata_install:
            changes = True
        
        elif metadata_file["update_number"] < metadata_install:
            print(_("\nThe update number of the received metadata is less than the number of the installed ones. This means that you are rolling back the Ports system to a previous version. You may be using the testing branch and installing an update from stable."))
            dialog_msg(return_code=1)

        else:
            print(_("\nAn error occurred while checking for metadata updates. The update number of the metadata received or installed could not be parsed."))
            f_i.close()
            sys.exit(1)
        
        if changes:
            difference = int(metadata_file["update_number"]) - int(update_ports.get_update_number(METADATA))
            print(_("Number of changes: {}\n").format(difference))

            print(_("Changes in the current update:"))
            #print(_("Updates:"))
            update_ports.print_changes(metadata_file["updates"], UPDATE_MSG)        # Updates
            update_ports.print_changes(metadata_file["additions"], ADDITIONS_MSG)   # Additions
            update_ports.print_changes(metadata_file["deletions"], DELETIONS_MSG)   # Deletions

            print(_("Changes in previous missed updates:"))
            f_i.close()
            
            file = "https://github.com/CalmiraLinux/Ports/raw/" + metadata_file["prev"] + "/metadata.json"
            while i <= difference:
                if os.path.isfile(METADATA_tmp):
                    os.remove(METADATA_tmp)
                
                wget.download(file, METADATA_tmp)

                if os.path.isfile(METADATA_tmp):
                    f_i = open(METADATA_tmp, "r")
                    metadata_file = json.load(f_i)

                    print(_("\nUpdate ID: {}").format(metadata_file["prev"]))

                    update_ports.print_changes(metadata_file["updates"], UPDATE_MSG)
                    update_ports.print_changes(metadata_file["additions"], ADDITIONS_MSG)
                    update_ports.print_changes(metadata_file["deletions"], DELETIONS_MSG)

                    f_i.close()
                else:
                    print(_("Error: old metadata file doesn't been downloaded!"))
                    sys.exit(1)
            
            dialog_msg()
    
    def get_distro_version(self):
        """
        Function for get CalmiraLinux version
        """
        f_distro = open(CALM_RELEASE)
        distro = json.load(f_distro)

        yield distro["distroVersion"]
        f_distro.close()

    def check_meta(self):
        """
        Function for check metadata for compatible
        with CalmiraLinux release
        """
        log_msg("Checking metadata compatible with this CalmiraLinux distribution", "notice")

        for file in METADATA, CALM_RELEASE:
            if os.path.isfile(file):
                pass
            else:
                print(_("File {} not found").format(file))
                sys.exit(1)
        
        f_meta = open(METADATA)
        metadata = json.load(f_meta)

        if int(metadata["system_version"]) == int(update_ports.get_distro_version()):
            log_msg("metadata OK", "ok")
            return_code =  0
        else:
            log_msg("metadata FAIL", "FAIL")
            return_code =  1
            
        f_meta.close()
        return return_code

    def get_file(self, branch):
        """
        Function for download Port system and CalmiraLinux documentation

        Usage:

        `ports.get_file(mode, branch)`
        * 'branch' - download branch:
            * 'stable',
            * 'testing'.
        """

        self.branch = branch

        log_message = "Getting file from branch '" + branch + "'"
        log_msg(log_message, "notice")

        try:
            pkg_data = open(METADATA, 'r')
        except FileNotFoundError:
            log_msg("File not found", "error")
            print(_("File {} not found").format(METADATA))
            sys.exit(1)
        except:
            log_msg("Uknown error", "error")
            print(_("Uknown error"))
            sys.exit(1)
        
        package_data = json.load(pkg_data)

        # Downloading
        for file in PORT_CACHE, DOC_CACHE:
            if os.path.isfile(file):
                os.remove(file)
        
        try:
            if branch == "stable":
                download_file = package_data["ports_stable"] + "/" + package_data["port_file"]
                wget.download(download_file, PORT_CACHE)

            elif branch == "testing":
                download_file = package_data["ports_unstable"] + "/" + package_data["port_file"]
                wget.download(download_file, PORT_CACHE)

            else:
                print(_("Uknown mode or branch for 'download_file'!"))
                sys.exit(1)

        except:
            # FIXME: очень часто неправильно выбирается исключение и тип ошибки "Uknown"
            print(_("Uknown error"))
            sys.exit(1)
    
    def unpack_file(self, file, extract_dir):
        """
        Function for unpacking files.

        Usage:
        
        `ports.unpack_file(mode)`
        """

        self.file = file
        self.extract_dir = extract_dir

        if os.path.isfile(file):
            try:
                t = tarfile.open(file, 'r')
                t.extractall(path=extract_dir)

            except tarfile.ReadError:
                print(_("Package read error. Perhaps he is broken"))
                sys.exit(1)

            except tarfile.CompressionError:
                print(_("Package unpacking error. The format is not supported"))
                sys.exit(1)
            
            except:
                print(_("Uknown error"))
                sys.exit(1)
        else:
            print(_("Package searching error. He's not found. It may have not been downloaded, or a third-party program changed it's name during unpacking"))
            sys.exit(1)
    
    def install_file(self, net_dir, target_dir):
        """
        Function for install Port system or CalmiraLinux documentation package.

        Usage:

        `update_ports.install_file(net_dir, target_dir)`

        * `net_dir` - что копировать;
        * `target_dir` - куда копировать.
        """

        self.net_dir = net_dir
        self.target_dir = target_dir

        # Checking for a previous version of package
        if os.path.isdir(target_dir):
            print(_("Found directory with previous Port system/CalmiraLinux documentation. Removing..."))
            shutil.rmtree(target_dir)
        else:
            pass
        
        # Copying
        try:
            print(_("Copying files..."))
            shutil.copytree(net_dir, target_dir)
        except:
            print(_("Uknown error of copy target files"))
            sys.exit(1)

class port_functions():
    """
    Other functions for Port system
    """
    def clean_sys(self, mode):
        """
        Function for cleaning system

        Work modes:
        - `cache` - clean the cache;
        - `log` - clean the log dir.
        """

        self.mode = mode
        
        check_root()
        
        if mode == "cache":
            # Очистка кеша
            print(_("Checking for cache existence..."), end = " ")

            if os.path.isdir(CACHE):
                print(OK_MSG)
                print(_("Removing {}...").format(CACHE))

                try:
                    shutil.rmtree(CACHE)
                except:
                    print(_("Error removing directory {}").format(CACHE))
                    sys.exit(1)
                
                print(_("Make {}...").format(CACHE))
                try:
                    os.makedirs(CACHE)
                except:
                    print(_("Error making {}").format(CACHE))
                    sys.exit(1)
            else:
                print(_("Fail: cache directory not found"))
                sys.exit(1)

        elif mode == "log":
            # Очистка лога
            print(_("Checking for log files existence..."))

            for file in LOGFILE, '/var/log/port-utils-dbg.log':
                print(_("Checking file {}...").format(file), end = " ")
                if os.path.isfile(file):
                    print(OK_MSG)
                else:
                    print(FAIL_MSG)
                    file_not_exists = True
                
            if file_not_exists == True:
                sys.exit(1)
                
            try:
                os.remove(file)
            except:
                print(_("Error removing file {}").format(file))
                sys.exit(1)

        elif mode == "src":
            # Очистка директории /usr/src

            src_dir = "/usr/src"
            print(_("Checking for src directory existence..."), end = " ")
            
            if os.path.isdir(src_dir):
                print(OK_MSG)
            else:
                print(FAIL_MSG)
                file_non_exists = True
            
            if file_non_exists == True:
                sys.exit(1)
            
            print(_("Removing {}...").format(src_dir))
            try:
                shutil.rmtree(src_dir)
            except:
                print(_("Error removing directory {}").format(src_dir))
                sys.exit(1)
            
            print(_("Make {}...").format(src_dir))
            try:
                os.makedirs(src_dir)
            except:
                print(_("Error making {}").format(src_dir))
                sys.exit(1)

# Работа с файлами для класса install_ports
class port_files(object):# Create database
    def create_db(self, db):
        """
        Function for create database

        Usage:
        `port_files.create_db(db)`

        - `db` - file with database.
        """

        self.db = db

        if os.path.isfile(db):
            return 1
        else:
            try:
                conn   = sqlite3.connect(db, timeout=3)
                cursor = conn.cursor()

                cursor.execute("""
                    CREATE TABLE ports (
                        name TEXT, version TEXT, maintainer TEXT,
                        description TEXT, priority TEXT
                    );
                    INSERT INTO ports VALUES (
                        'ports', 'lx4/v1.1', 'Linuxoid85', 'Ports system for CalmiraLinux', 'system'
                    );
                    INSERT INTO ports VALUES (
                        'port-utils', 'v1.0a2', 'Linuxoid85', 'Port system software', 'system'
                    );
                """)
                conn.commit()
                cursor.close()
            
            except sqlite3.Error as error:
                print(_("SQLite3 connection error: {}").format(error))
    
    # FIXME: убрать устаревшие функции
    # Lock database
    def lock_db(self):
        """
        Function for locking database

        Usage:
        `port_files.lock_db()`
        """
        message = "port-utils database was locked\n"

        if os.path.isfile(database_lock_file):
            print(_("Error: the database already locked!"))
            return 1
        else:
            try:
                f = open(database_lock_file, 'w')
                for index in message:
                    f.write(index)
                return 0
            except:
                return 1
    
    # Checking lock database
    def check_lock_db(self):
        """
        Function for checking lock database

        Usage:
        `port_files.check_lock_db()`
        """
        if os.path.isfile(database_lock_file):
            print(_("An instance of the program is already running. Complete it before accessing the database."))
            return 1
        else:
            return 0

class info_ports(object):
    def __init__(self, port, only_deps=False):
        self.port    = port

        port_name    = PORTDIR   + "/" + port
        port_json    = port_name + "/config.json"

        build_ports.check_port(port_name, port_json)

        info_ports.info_port(port_json, only_deps)
    
    def info_port(port_json, only_deps=False):
        # Base information
        try:
            f = open(port_json)
        except FileNotFoundError:
            print(_("File {} not found").format(port_json))
            sys.exit(1)
        
        try:
            port_data = json.load(f)

            if only_deps == False:
                print(_("Name: {}").format(port_data["name"]))
                print(_("Version: {}").format(port_data["version"]))
                print(_("Maintainer: {}").format(port_data["maintainer"]))
                print(_("Priority: {}").format(port_data["priority"]))
                print(_("Calmira release: {}").format(port_data["release"]))
            
            # FIXME: добавить проверку на наличие определённой
            # категории зависимостей, т.к. в config.json могут
            # отсутствовать некоторые поля, которые выводятся здесь.
            print(_("Depends:"))
            print(_("Required: \n{}").format(port_data["deps"]["required"]))
            print(_("\nRuntime: \n{}").format(port_data["deps"]["runtime"]))
            print(_("\nOptional: \n{}").format(port_data["deps"]["optional"]))
            print(_("\nRecommend: \n{}").format(port_data["deps"]["recommend"]))
            print(_("\nBefore: \n{}").format(port_data["deps"]["before"]))
            print(_("\nConflicts: \n{}").format(port_data["deps"]["conflict"]))

            return_code = 0

        except:
            print(_("Uknown error"))
            return_code = 1
        
        finally:
            f.close()
            sys.exit(return_code)

class build_ports(object):
    """
    Class with functions for building, installing,
    removing ports packages.

    TODO: add an `__init__()` function for choose work
    mode and other works...
    """
    def __init__(self, port):
        self.port = port

        # Вычисление данных порта
        port_path    = PORTDIR   + "/" + port
        port_json    = port_path + "/config.json"
        port_install = port_path + "/install"
        port_remove  = port_path + "/remove"
        
        # Вызов нужных функций
        build_ports.check_port(port_path, port_json, port_install, port_remove)
        
        print(_("Checking database lock..."))
        if port_files.check_lock_db():
            print(OK_MSG)
            
            # Print deps
            print(_("These dependencies need to be satisfied (installed) before or after building the port {}:").format(port))
            info_ports(port, only_deps=True)
            dialog_msg(return_code=1)

            # Building and installing port package
            build_ports.install_file(port_install)
            build_ports.add_in_db(port, port_json)
        else:
            print(FAIL_MSG)
            sys.exit(1)
        
    # Checking for the existence of a port package
    def check_port(self, port_name, json_file,
                   install_file, remove_file):
        """
        Function for checking for the existence of a port package

        Usage:
        `build_ports.check_port(port)`

        `port` - the required port package
        """

        self.port_name = port_name
        self.json_file = json_file
        self.install_file = install_file
        self.remove_file = remove_file

        # FIXME: переделать алгоритм проверки порта

        # Checking for file existence
        print(_("Port: {}").format(port_name))
        
        for file in json_file, install_file:
            print(_("Checking {}...").format(file), end = " ")
            if os.path.isfile(file):
                print(OK_MSG)
            else:
                print(FAIL_MSG)
                NoFile = True
        
        if NoFile:
            sys.exit(1)
        
        print(_("Checking {}...").format(remove_file), end = " ")
        if os.path.isfile(remove_file):
            print(OK_MSG)
            return 0
        else:
            print(_("WARNING: there is no file with instructions to remove this port"))


    # Установка порта
    def install_port(self, install_file):
        self.install_file = install_file

        install_instruction = install_file + " 2>&1 |tee " + LOGDIR + "/port-utils-build.log"
        build = subprocess.run(install_instruction, shell=True)
        
        return build.returncode
    
    # Добавление порта в базу данных
    def add_in_db(self, port, json_file):
        self.port = port
        self.json_file = json_file

        if os.path.isfile(DATABASE):
            print(_("Adding {} in database...").format(port))
        else:
            print(_("Error adding {} in database: database not found!").format(port))
            return 1
        
        file    = open(json_file, "r")
        package = json.load(file)
        
        package_data = [(package["name"], package["version"], package["maintainer"], package["description"], package["priority"])]
        
        conn   = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO ports VALUES (?,?,?,?,?);", package_data)
        conn.commit()

class remove_ports(object):
    # Класс для удаления порта из системы.
    # TODO: добавить логирование
    def __init__(self, port):
        self.port = port

        # Вычисление данных порта
        port_path   = PORTDIR   + "/" + port
        port_json   = port_path + "/config.json"
        port_remove = port_path + "/remove"
        
        # Вызов нужных функций
        if remove_ports.check_remove_port(port_path, port_json, port_remove):
            pass
        else:
            sys.exit(1)

        f = open(port_remove)
        portData = json.load(f)

        if portData["priority"] == "system":
            print(_("This port package is systemic and cannot be removed"))
            sys.exit(1)
        
        print(_("Checking database lock..."))
        if port_files.check_lock_db():
            print(OK_MSG)

            # Print depends
            print(_("These dependencies need to be satisfied (removed) before or after removing the installed port {}:").format(port))
            info_ports(port, only_deps=True)
            dialog_msg(return_code=1)
            
            # Removing port
            remove_ports.remove_port(port_remove)
            remove_ports.remove_from_db(port_path, port_json)
        else:
            print(FAIL_MSG)
            sys.exit(1)
        
    def check_remove_port(self, port_name, json_file, remove_file):
        """
        Function for checking for the existence of a port package
        
        Usage:
        `remove_ports.check_remove_port(...)`
        """

        self.port_name = port_name
        self.json_file = json_file
        self.remove_file = remove_file

        print(_("Port: {}").format(port_name))
        
        for file in json_file, remove_file:
            print(_("Checking {}...").format(file), end = " ")
            if os.path.isfile(file):
                print(OK_MSG)
            else:
                print(FAIL_MSG)
                NoFile = True
        
        if NoFile:
            sys.exit(1)
        else:
            return 0

    def remove_port(self, remove_file):
        """
        Function for remove port from system
        
        Usage:
        `remove_ports.remove_port(file)`
        """

        self.remove_file = remove_file
        
        remove_instructions = remove_file + " 2>&1 |tee " + LOGDIR + "/port-utils-remove.log"
        remove = subprocess.run(remove_instructions, shell = True)
        
        return remove.returncode
        
    def remove_from_db(self, port, json_file):
        """
        Function for remove port package from database
        
        Usage:
            remove_ports.remove_from_db(port)
            
            'port' - port name (e.g. base/editors/emacs)
        """

        self.port = port
        self.json_file = json_file
        
        if os.path.isfile(DATABASE):
            print(_("Removing {} from database...").format(port))
        else:
            print(_("Error removing {} from database: database not found!").format(port))
            return 1
        
        file    = open(json_file, "r")
        package = json.load(file)
        
        package_data = [(package["name"])]
        
        conn   = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM ports WHERE name=?", package_data)
        conn.commit()

class update_data(object):
    """
    Class for updating ports packages and other files
    """
    def update_port(self, port):
        """
        Function for update port package

        Usage:
        `update_data.update_port(portname)`

        - `portname` e.g. base/editors/vim
        """

        self.port = port
        port_path = PORTDIR   + "/" + port
        port_json = port_path + "/config.json"

        print(_("Checking database lock..."))
        if port_files.check_lock_db():
            print(OK_MSG)

            # Print deps
            print(_("These dependencies need to be satisfied (updated) before or after update port {}:").format(port))
            info_ports(port, only_deps=True)
            dialog_msg(return_code=1)

            # Removing port
            remove_ports.remove_from_db(port_path, port_json)
        else:
            print(FAIL_MSG)
            sys.exit(0)
        
        build_ports(port) # Build the port package and add this into database

#################
##             ##
## Script body ##
##             ##
#################

# Command line parsing

if args.update:
    # Update port system
    update_ports(args.update)

elif args.install:
    # Install port package
    build_ports(args.install)

elif args.remove:
    # Remove port package
    remove_ports(args.remove)

elif args.info:
    # Info about port package
    info_ports(args.info)

elif args.metadata:
    # Get port system metadata
    update_ports.update_meta(args.metadata)

elif args.clean:
    port_functions.clean_sys(args.clean)

elif args.about:
    about_msg()

else:
    print(_("Usage: port-utils -h"))
    sys.exit(1)
