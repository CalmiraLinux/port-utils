#!/usr/bin/python
#
# port-additions - additional functions for Port utils software
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
import gettext

gettext.bindtextdomain('port-utils', '/usr/share/locale')
gettext.textdomain('port-utils')

## BASE CONSTANTS ##
LOGDIR = "/var/log"
LOGFILE = LOGDIR + "/port-utils.log"
USER_VAR_DIR = "~/.local/port-utils/var"
USER_LOG_DIR = USER_VAR_DIR + "/log"

def log_msg(message, status):
    """
    Functions for write messages on log file

    Usage:
    `log_msg(message, status)`

    Statuses:
    - 'ok',
    - 'notice',
    - 'error',
    - 'fail',
    - 'emerge'.
    """

    log_message = message + " [ " + status + " ]\n"
    gid = os.getgid()

    if gid == 0:
        f = open(LOGFILE, "a")
    else:
        if os.path.isdir(USER_LOG_DIR):
            pass
        else:
            os.makedirs(USER_LOG_DIR)
        
        log_msg_user = USER_LOG_DIR + "/port-utils.log"
        f = open(log_msg_user, "a")
    
    for index in log_message:
        f.write(index)
    
    f.close()