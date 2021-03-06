# dialog_msg()

Функция предназначена для запроса у пользователя продолжения выполнения операции. Вывод в stdout в таком формате:

```
{message} (y/n) 
```

Пользователь должен ответить Y или y для продолжения, либо n/N для отказа. В таком случае функция либо завершится с определённым кодом (0 в случае Y/y или 1 в случае n/N), либо спровоцирует выход из программы с кодом завершения 0, либо указанным пользователем.

## Прототип

```python
def dialog_msg(message, mode="none", return_code=0)
```

- `message` - нужное сообщение, которое будет выведено в stdout;
- `mode` - режим работы. Если установлен как `none` (либо любое другое значение), либо не установлен вовсе при передаче параметров функции `dialog_msg()`, то при ответе n/N функция не спровоцирует выход из программы. Если режим работы установлен как `exit`, то при ответе n/N будет спровоцирован выход из программы с кодом завершения, установленным параметром `return_code`;
- `return_code` - параметр, указывающие код завершения программы. По умолчанию равен нулю. При необходимости заменяется на нужное значение. Выход с кодом `return_code` провоцируется при использовании `mode` равного строке `exit` (режим работы = `exit`).

