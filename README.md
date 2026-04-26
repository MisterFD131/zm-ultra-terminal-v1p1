# zm-ultra-terminal-v1p1

Personal portable launcher utility.

## Скачать

Готовые сборки будут появляться во вкладке **Releases**.

Обычный пользователь скачивает архив `ZapretManager_vX.zip`, распаковывает папку и запускает `ZapretManager.exe`.

Python пользователю не нужен.

## Для владельца

Основной сценарий обновлений:

1. Изменения попадают в репозиторий.
2. GitHub Actions автоматически собирает Windows-сборку.
3. Новый архив публикуется в GitHub Releases.

Запасной локальный сценарий:

1. Скачать новый `ZapretManager_Setup_vX.py` или `zapret_manager_gui_vX.py` в папку Downloads.
2. Запустить `publish_update.bat` из локальной копии репозитория.
3. Скрипт сам найдёт новую версию, проверит, что она новее, обновит исходник и отправит изменения в GitHub.
