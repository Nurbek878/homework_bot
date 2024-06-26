# Telegram-bot
Telegram-бот обращается к API сервиса Практикум.Домашка и узнает статус домашней работы.
## Возможности
- Раз в 10 минут опрашивать API сервиса Практикум.Домашка и проверять статус отправленной на ревью домашней работы 
- При обновлении статуса анализировать ответ API и отправлять вам соответствующее уведомление в Telegram.
- Логировать свою работу и сообщать вам о важных проблемах сообщением в Telegram.
## Tехнологии
- [Python 3.9]

Проект опубликован в [репозитории][dill] на Github.
 
 ## Запуск проекта в dev-режиме

- Установите и активируйте виртуальное окружение
```
python3 -m venv venv
```
```
source venv/bin/activate
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
- Создаем .env файл с токенами в корневой папке:
```
PRACTICUM_TOKEN=<practicum's token>
TELEGRAM_TOKEN=<your token>
CHAT_ID=<your chat_id>
```
- Запускаем бота:
```
python homework.py
```

### Авторы
Нурбек Орозалиев

   [dill]: <https://github.com/Nurbek878/homework_bot>

