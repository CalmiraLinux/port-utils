# port-utils

`port-utils` - программа для управления системой портов. Система портов пришла на смену бинарным и port-пакетам ныне устаревшего `cpkg`.

port-utils умеет обновлять как саму систему портов, так и документацию CalmiraLinux. Так же в релизе 1.0 ожидаются возможности установки и удаления определённого порта, а так же просмотр о нём информации.

## Синтаксис

```
port-utils [ключ] {ветка}/{категория и имя порта}
```

## Ключи

- `--update` - обновление системы портов;
- `--doc` - обновление документации дистрибутива;
- `--install` - собрать порт;
- `--info` - информация о проте;
- `--remove` - удалить порт;
- `--news` - просмотреть изменения в системе портов;
- `--metadata` - обновить метаданные port-utils;

## Использование

Обновление системы портов из стабильной ветки:

```bash
port-utils --update stable
```

Сборка порта `base/editors/emacs`:

```bash
port-utils --install base/editors/emacs
```

Просмотр информации о `base/gcc`:

```bash
port-utils --info base/gcc
```

## Зависимости

Python Modules:
- `wget`;
- `subprocess`.