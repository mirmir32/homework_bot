import logging
import os
import requests
import sys
import telegram
import time

from dotenv import load_dotenv
from http import HTTPStatus

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
)

handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


def send_message(bot, message):
    """Отправка сообщения."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info('Сообщение отправлено')
    except telegram.error.TelegramError:
        logger.error('Сообщение не отправлено')


def get_api_answer(current_timestamp):
    """Запрос к API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.exceptions.ConnectTimeout as error:
        logger.error(f'Превышено время ожидания ответа сервера {error}')
        raise error
    except requests.exceptions.RequestException as error:
        logger.error(f'Ошибка соединения {error}')
        raise error
    if response.status_code != HTTPStatus.OK:
        logger.error(f'Эндпоинт {ENDPOINT} недоступен.'
                     f'Код ответа сервера: {response.status_code}')
        raise requests.HTTPError(f'Код ответа сервера: {response.status_code}')
    return response.json()


def check_response(response):
    """Проверка корректности ответа API."""
    if not isinstance(response, dict):
        logger.error('Ответ API не соответствует ожиданиям')
        raise TypeError('Ответ API не соответствует ожиданиям')
    if 'homeworks' not in response:
        logger.error('Отсутствует ключ homeworks')
        raise KeyError('Отсутствует ключ homeworks')
    if not isinstance(response['homeworks'], list):
        logger.error('Ответ API не соответствует ожиданиям')
        raise TypeError('Ответ API не соответствует ожиданиям')
    homework = response['homeworks']
    return homework


def parse_status(homework):
    """Извлечение из информации о домашней работе её статуса."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    if homework_status is None:
        logger.error('Отсутствует ключ homework_status')
        raise KeyError('Отсутствует ключ homework_status')
    if homework_status not in HOMEWORK_STATUSES:
        logger.error('Неожиданный статус')
        raise ValueError('Неожиданный статус')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка токенов."""
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    for token in tokens:
        if tokens[token] is None:
            logger.critical(f'Отсутствует токен {token}')
            return False
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Отсутствует токен')
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            check_response(response)
            new_homework = response.get('homeworks')
            if new_homework:
                logging.info('Работа найдена')
                send_message(bot, parse_status(new_homework[0]))
            else:
                logging.exception('Бот не нашел домашнюю работу')
                send_message(bot, 'Бот не нашел домашнюю работу')
                raise ValueError('Бот не нашел домашнюю работу')
        except Exception as error:
            logging.exception(f'Ошибка: {error}')
        finally:
            time.sleep(int(RETRY_TIME))


if __name__ == '__main__':
    main()
