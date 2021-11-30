#!/usr/bin/python3
# Модуль со стандартными и общими функциями и
# переменными, используемыми в Ports API
# (C) 2021 Михаил Краснов <linuxoid85@gmail.com>

PORTDIR      = "/usr/ports"                   # Директория с системой портов
PROGRAM_DIR  = "/usr/share/ports"             # Директория с данными утилиты
CACHE        = "/var/cache/ports"             # Директория с кешем
DB           = "/var/db/ports/ports.db"       # База данных установленных портов
METADATA     = PROGRAM_DIR + "/metadata.json" # Метаданные утилиты
METADATA_TMP = "/tmp/metadata.json"           # Скаченные метаданные
CALM_RELEASE = "/etc/calm-release"            # Файл с информацией о системе
SETTINGS     = "/etc/port-utils.json"         # Параметры утилиты

def log_msg(message, status):
    """
    Функция для отправки сообщений в лог

    Использование:
    `log_msg(message, status)`
    """

    f = open(LOGFILE, "a")
    
    message = message + "[ " + status " ]\n"

    f.write(message)
    f.close()

def dbg_msg(function, message, status, mode):
    """
    Функция для отправки debug-сообщений в stdout.

    Использование:
    `dbg_msg(function, message, status)`

    - `function` - название функции;
    - `message` - сообщение;
    - `status` - статус выполнения функции.
    """

    v_msg = "message from " + function + ". This status: [ " + status " ]"
    
    if mode == "quiet":
        print(v_msg)
        return 0
    else:
        return 0

def dialog_msg(return_code=0, exit_pr=False):
    """
    Диалоговые сообщения. `return_code` - код выхода из
    программы, либо функции. Если `exit_pr` установлен
    как `True`, то значение `return_code` будет
    использовано для кода выхода из программы. Если `False`,
    то из функции.
    """

    print(_("Continue? (y/n)"), end=" ")
    run = input()

    if run == "n" or run == "N":
        if exit_pr:
            exit(return_code)
        else:
            return return_code
    elif run == "Y" or run == "y":
        print(_("Continue"))
    else:
        print(_("Uknown input"))
        exit(1)

def check_port(port):
    """
    Функция для проверки порта на совместимость
    стандартам CalmiraLinux.

    Проверяет наличие необходимых файлов (install,
    remove, config.json).
    """

    port_dir = PORTDIR + "/" + port + "/"

    files = ("install", "remove", "config.json")
    ustar_files = ("config.sh", "info")
    
    v_error = False
    v_ustar = False

    for file in files:
        if not os.path.isfile(portdir+file):
            print(f"[{portdir+file}]: not found!")
            v_error = True

    # Проверка на наличие устаревших файлов
    for file in ustar_files:
        if os.path.isfile(portdir+file):
            print(f"[{portdir+file}]: ustar file detected!")
            v_ustar = True

    if v_ustar:
        print(f"Port '{port}' is ustar format!")
        dialog_msg(return_code=1, exit_pr=True)
    
    if v_error:
        return 1

def check_root() -> bool:
    """
    Проверка на запуск от имени root
    """

    gid = os.getgid()

    if gid != 0:
        return False
    else:
        return True

