# Telegram Homework Bot
## Описание
Бот, который проверяет статусы проектов при помощи Telegram API.

## Установка
Клонируем репозиторий:
```
git clone whoishacked/homework_bot
```
Переходим в папку с проектом:
```
cd homework_bot
```
Устанавливаем и активируем venv:
```
python3 -m venv venv
```
```
source venv/bin/activate
```
Устанавливаем pip:
```
python3 -m pip install --upgrade pip
```
Устанавливаем зависимости:
```
pip instal -r requirements.txt
```
Запускаем проект:
```
python3 homework.py
```
Для запуска скрипта по расписанию используйте CRON (https://wikipedia.org/wiki/Cron) или разместите проект на Heroku (https://www.heroku.com/).

## Используемые технологии
Краткий список:
- Python 3
- Telegram API