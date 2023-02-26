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
TELEGRAM_CHAT_ID = 805926951

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s',
    stream=sys.stdout
)


def check_tokens() -> bool:
    """Проверка наличия и доступности переменных окружения."""
    CHECK_LIST = (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    result = all(CHECK_LIST)
    logging.critical('Ошибка при проверке переменных окружения')
    return result


def send_message(bot: telegram.bot.Bot, message: str) -> None:
    """Бот посылает сообщение о статусе домашки в чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text=message)
        logging.debug('Сообщение отправлено')
    except telegram.TelegramError:
        logging.error('Сбой при отправке сообщения')


def get_api_answer(timestamp: dict[str, int]) -> dict:
    """Делаем запрос к API домашки."""
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=timestamp)
        if response.status_code != HTTPStatus.OK:
            raise requests.HTTPError(
                f'API домашки вернул статус {response.status_code}'
            )
        return response.json()
    except requests.RequestException():
        logging.error('Сбой при запросе к эндпоинту')


def check_response(response: dict[str, str]) -> dict:
    """Проверяем ответ API на соответствие."""
    logging.error('Ошибка при проверке ответа API')
    if not isinstance(response, dict):
        raise TypeError('Тип ответа не соответствует документации')
    if 'homeworks' not in response:
        raise KeyError('В словаре ответа отсутствует ключ к домашке')
    homework = response.get('homeworks')
    if not isinstance(homework, list):
        raise TypeError('Тип ответа не соответствует документации')
    return homework[0]


def parse_status(homework: dict[str, str]) -> str:
    """Получаем статус домашки и готовим сообщение для бота."""
    logging.error('В ответе API домашки нет ключей')
    if 'homework_name' not in homework:
        raise KeyError('В ответе API домашки нет ключа "homework_name"')
    homework_name = homework.get('homework_name')
    if 'status' not in homework:
        raise KeyError('В ответе API домашки нет ключа "status"')
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise KeyError('У домашки не бывает такого статуса')
    verdict = HOMEWORK_VERDICTS.get(status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = {'from_date': int(time.time())}
    hw_status = 'sent'
    while True:
        try:
            if check_tokens() is False:
                logging.critical('Переменные окружения недоступны')
                sys.exit()
            else:
                response = get_api_answer(timestamp)
                homework = check_response(response)
                status = homework.get('status')
                if status != hw_status:
                    hw_status == status
                    message = parse_status(homework)
                    send_message(bot, message)
                    logging.error('Сбой при отправке сообщения')
                else:
                    logging.debug('Статус домашки не изменился')
                    return None
        except Exception as error:
            logging.error(f'Сбой в работе программы {error}')
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        time.sleep(600)


if __name__ == '__main__':
    main()
