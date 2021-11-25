#!/bin/bash
# Модуль API для работы с окнами.
# Предназначено ТОЛЬКО для использования в 
# скриптах системы портов
# (C) 2021 Михаил Краснов <linuxoid85@gmail.com>

# Depends:
# dialog, tput

BACKTITLE="CalmiraLinux Port system"
SRCDIR="/usr/src"

# Function for print messages
# USAGE:
# msg $title $message
function msg() {
    dialog --backtitle $BACKTITLE --title " $1 " \
        --msgbox "$2" 0 0
}

function print_info_msg() {
    echo -e "\e[1;32m$1\e[0m"
}

# Function for print yes/no dialogs
# USAGE:
# msg $title $message
function dial() {
    dialog --backtitle $BACKTITLE --title " $1 " \
        --yesno "$2" 0 0
}

# Function for print status messages
# USAGE:
# status $message $status
function status() {
    ## Base messages ##
    SUCCESS="echo -en \\e[1;32m"
    FAIL="echo -en \\e[1;31m"
    NORMAL="echo -en \\e[0;39m"

    ## Printing message ##
    if [ $2 -eq "ok" ]; then
        echo -n "$1"
        $SUCCESS
        echo -n "$(tput hpa $(tput cols))$(tput cub 6)[ok]"
        $NORMAL
    elif [ $2 -eq "fail" ]; then
        echo -n "$1"
        $FAIL
        echo -n "$(tput hpa $(tput cols))$(tput cub 6)[FAIL]"
        $NORMAL
    fi
}

function fetch() {
    if [ -d $SRCDIR ]; then
        echo "$SRCDIR: ok"
    else
        mkdir -pv $SRCDIR
    fi

    cd $SRCDIR

    if [ -f "$1" ]; then
        rm -rvf "$1"
    fi

    wget "$1"

    if [ $? -eq 0 ]; then
        status "Getting package \"$1\":" "ok"
    else
        status "Getting package \"$1\":" "fail"
        exit 1
    fi
}

function unpack() {
    if [ -f "$1" ]; then
        echo "Package \"$1\": found"
    else
        echo "Package \"$1\": NOT found"
        exit 1
    fi

    tar -xvf $1

    if [ $? -eq 0 ]; then
        status "Unpacking package \"$1\":" "ok"
    else
        status "Unpacking package \"$1\":" "fail"
        exit 1
    fi
}