import json
import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import EmptyStatusError, JSONError, UndocumentedStatusError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
previous_message = ''

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("program.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def check_tokens() -> bool:
    """Функция проверяет доступность переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def send_message(bot: telegram.bot.Bot, message: str) -> None:
    """Функция отправляет сообщение в Telegram чат."""
    logger.debug('Сообщение отправляется')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Cообщение успешно отправлено')
    except telegram.error.TelegramError as error:
        logger.error(f"Ошибка отправки статуса в telegram: {error}")


def get_api_answer(timestamp: int) -> dict:
    """Функция делает запрос к эндпоинту API-сервиса."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException:
        raise Exception('Ошибка при запросе к ENDPOINT.')
    if response.status_code != HTTPStatus.OK:
        raise requests.HTTPError(f'Код ответа {response.status_code} '
                                 f'не равен 200')
    try:
        return response.json()
    except json.JSONDecodeError:
        raise JSONError('Формат ответа не json')


def check_response(response: dict) -> list:
    """Функция проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('Формат ответа не словарь')
    if 'homeworks' not in response:
        raise KeyError('Ключ "homeworks" отсутствует в словаре')
    if 'current_date' not in response:
        raise KeyError('Ключ "current_date" отсутствует в словаре')
    response_list = response.get('homeworks')
    if not isinstance(response_list, list):
        raise TypeError('Формат ответа не список')
    return response_list


def parse_status(homework: dict) -> str:
    """Функция извлекает статус домашней работы."""
    if 'homework_name' not in homework:
        raise KeyError('Такого ключа homework_name нет')
    homework_name = homework.get('homework_name')
    status_homework = homework.get('status')
    if status_homework not in HOMEWORK_VERDICTS:
        raise UndocumentedStatusError('Недокументированный статус '
                                      'домашней работы')
    verdict = HOMEWORK_VERDICTS.get(status_homework)
    if not verdict:
        raise EmptyStatusError('Нет статуса домашней работы')
    return (f'Изменился статус проверки '
            f'работы "{homework_name}". {verdict}')


def check_changed_value(message: str) -> bool:
    """Функция определяет изменилось ли значение статуса."""
    global previous_message
    value_changed = previous_message != message
    previous_message = message
    return value_changed


def check_send_message(message: str, homework: list) -> None:
    """Функция проверяет подготовленное сообщение.
    Тип сообщения и содержит ли оно статус из словаря.
    """
    if not isinstance(message, str):
        raise TypeError('Подготовленное сообщение не строка')
    status = homework[0].get('status')
    if HOMEWORK_VERDICTS[status] not in message:
        raise TypeError('Подготовленное сообщение не из словаря')


def generate_message(homework: list) -> str:
    """Функция формирует сообщение о статусе."""
    if homework:
        message = parse_status(homework[0])
        logger.debug(message)
        check_send_message(message, homework)
    else:
        message = 'Новых статусов нет'
        logger.debug(message)
    return message


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствие обязательных переменных '
                        'окружения во время запуска бота')
        raise SystemExit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            timestamp = int(response.get('current_date'))
            homework = check_response(response)
            message = generate_message(homework)
            if check_changed_value(message):
                send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.exception('Бот остановлен')
