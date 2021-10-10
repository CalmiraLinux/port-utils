# Использование

## Синтаксис

```bash
port-utils[-h] [--update {stable,testing}] [--news {stable,testing}] [--install INSTALL] [--remove REMOVE] [--info INFO] [--doc {stable,testing}] [--metadata {stable,testing}] [--clean {cache,log,src,all}] [--about]
```

## Опции

- `-h`, `--help` - показать краткую справку по утилите;
- `-u`, `--update` - обновить систему портов до определённой ветки;
- `-n`, `--news` - просмотреть список изменений в портах;
- `-i`, `--install` - собрать определённый порт (например, `base/editors/vim`);
- `-r`, `--remove` - удалить определённый порт (например, `/base/editors/vim`);
- `-I`, `--info` - просмотреть информацию о порте;
- `-d`, `--doc` - обновить документацию CalmiraLinux;
- `--metadata` - обновить метаданные портов;
- `--clean` - очистить систему от устаревших файлов СП;
- `-a`, `--about` - просмотреть информацию об утилите.