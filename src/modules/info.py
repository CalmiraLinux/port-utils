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
import json
import gettext

gettext.bindtextdomain('port-utils', '/usr/share/locale')
gettext.textdomain('port-utils')
_ = gettext.gettext

class info_ports(object):
    def __init__(self, port_json, only_deps=False):
        if os.path.isfile(self.port_json):
            pass
        else:
            print(_("File {} not exists").format(self.port_json))
            sys.exit(1)
        
        info_ports.info_port(self.port_json)

    def info_port(self, port_json, only_deps=False):
        self.port_json = port_json

        f = open(port_json, "r")
        
        try:
            port_data = json.load(f)

        except:
            print(_("Uknown error"))
            sys.exit(1)
        
        if only_deps == False:
            print(_("Name: {}").format(port_data["name"]))
            print(_("Version: {}").format(port_data["version"]))
            print(_("Maintainer: {}").format(port_data["maintainer"]))
            print(_("Priority: {}").format(port_data["priority"]))
            print(_("Calmira release: {}").format(port_data["release"]))
            
        try:
            # FIXME: добавить проверку на наличие определённой
            # категории зависимостей, т.к. в config.json могут
            # отсутствовать некоторые поля, которые выводятся здесь.
            print(_("Depends:"))
            print(_("Required: \n{}").format(port_data["deps"]["required"]))
            print(_("Runtime: \n{}").format(port_data["deps"]["runtime"]))
            print(_("Optional: \n{}").format(port_data["deps"]["optional"]))
            print(_("Recommend: \n{}").format(port_data["deps"]["recommend"]))
            print(_("Before: \n{}").format(port_data["deps"]["before"]))
            print(_("Conflicts: \n{}").format(port_data["deps"]["conflict"]))

            return_code = 0
        except:
            print(_("Uknown error"))
            return_code = 1
        
        finally:
            f.close()
            return return_code

