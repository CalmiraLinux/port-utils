# update-ports

`update-ports` - скрипт для обновления системы портов Calmira, написанный с нуля.

## Синтаксис:

```
update-ports --tree stable/testing
```

## Ветки

Сейчас поддерживаются только две ветки:

* `stable` - стабильная ветка;
* `testing` - нестабильная ветка, порты из которой ещё тестируются.

## Зависимости

* `requests` - модуль Python. Установка:

```python
pip3 install requests
```
