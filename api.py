import logging
import os
import requests
import time

from dotenv import load_dotenv
from http import HTTPStatus
from telegram import Bot
from pprint import pprint


load_dotenv()

PRACTICUM_TOKEN_URL = os.getenv('PRACTICUM_TOKEN_URL')
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = 805926951

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

timestamp = {'from_date': int(time.time())}

#logging.basicConfig(
    #level=logging.DEBUG,
    #format='%(asctime)s, %(levelname)s, %(message)s')


def check_tokens():
    """Проверка наличия и доступности переменных окружения."""
    try:
        CHECK_LIST = (PRACTICUM_TOKEN_URL, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
        return all(CHECK_LIST)
    except Exception as error:
        #logging.error('Ошибка при проверке переменных окружения: {error}')
        return f'Ошибка при проверке переменных окружения: {error}'
    

def send_message(bot, message):
    """Бот посылает сообщение о статусе домашки в чат."""
    try:
        text = message
        bot.send_message(TELEGRAM_CHAT_ID, text)
        #logging.DEBUG('Сообщение отправлено')
    except Exception as error:
        #logging.ERROR('Сбой при отправке сообщения: {a}')
        return f'Ошибка при отправке сообщения: {error}'
        #bot.send_message(TELEGRAM_CHAT_ID, text=a)
    

def get_api_answer(timestamp):
    """Делаем запрос к API домашки."""
    response = requests.get(ENDPOINT, headers=HEADERS, params=timestamp)
    response = response.json()
    print(type(response))
    pprint(response)
    return response


get_api_answer(timestamp)
